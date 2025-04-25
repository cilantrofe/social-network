from datetime import datetime
from fastapi import Header
from typing import List, Optional
import httpx
from pydantic import BaseModel
import jwt
import os
from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, Query, Request, HTTPException
import grpc
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../proto")))
from proto import post_service_pb2, post_service_pb2_grpc


class PostCreate(BaseModel):
    title: str
    description: str
    is_private: bool = False
    tags: List[str] = []


class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    tags: Optional[List[str]] = None


class PostResponse(BaseModel):
    id: str
    title: str
    description: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_private: bool
    tags: List[str]


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    per_page: int


async def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    return {"id": user_id}


SECRET_KEY = os.getenv("SECRET_KEY", "123456")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

app = FastAPI()


def verify_token(token: str):
    print(f"[DEBUG] TOKEN: {token}")
    print(f"[DEBUG] SECRET_KEY: {SECRET_KEY}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded token: {payload}")
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def proxy_request(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        # Только user-service идёт через HTTP
        response = await client.request(
            method=request.method,
            url=f"http://user-service:8000{path}",
            headers=request.headers.raw,
            content=await request.body(),
        )
        return response


@app.post("/posts", response_model=dict, status_code=201)
async def create_post(post: PostCreate, user: dict = Depends(get_current_user)):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            response = stub.CreatePost(
                post_service_pb2.CreatePostRequest(
                    title=post.title,
                    description=post.description,
                    user_id=user["id"],
                    is_private=post.is_private,
                    tags=post.tags,
                )
            )
            return {"id": response.id}
        except grpc.RpcError as e:
            handle_grpc_error(e)


@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, user: dict = Depends(get_current_user)):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            response = stub.GetPost(post_service_pb2.GetPostRequest(id=post_id))

            if response.is_private and response.user_id != user["id"]:
                raise HTTPException(
                    status_code=403, detail="Access to private post denied"
                )

            return PostResponse(
                **{
                    "id": response.id,
                    "title": response.title,
                    "description": response.description,
                    "user_id": response.user_id,
                    "created_at": datetime.fromisoformat(response.created_at),
                    "updated_at": datetime.fromisoformat(response.updated_at),
                    "is_private": response.is_private,
                    "tags": response.tags,
                }
            )
        except grpc.RpcError as e:
            handle_grpc_error(e)


@app.put("/posts/{post_id}")
async def update_post(
    post_id: str, post_update: PostUpdate, user: dict = Depends(get_current_user)
):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            existing_post = stub.GetPost(post_service_pb2.GetPostRequest(id=post_id))
            if existing_post.user_id != user["id"]:
                raise HTTPException(
                    status_code=403, detail="You can only update your own posts"
                )

            update_request = post_service_pb2.UpdatePostRequest(id=post_id)
            if post_update.title is not None:
                update_request.title = post_update.title
            if post_update.description is not None:
                update_request.description = post_update.description
            if post_update.is_private is not None:
                update_request.is_private = post_update.is_private
            if post_update.tags is not None:
                update_request.tags.extend(post_update.tags)

            response = stub.UpdatePost(update_request)
            return {"message": "Post updated successfully"}
        except grpc.RpcError as e:
            handle_grpc_error(e)


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, user: dict = Depends(get_current_user)):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            existing_post = stub.GetPost(post_service_pb2.GetPostRequest(id=post_id))
            if existing_post.user_id != user["id"]:
                raise HTTPException(
                    status_code=403, detail="You can only delete your own posts"
                )

            stub.DeletePost(post_service_pb2.DeletePostRequest(id=post_id))
            return {"message": "Post deleted successfully"}
        except grpc.RpcError as e:
            handle_grpc_error(e)


@app.get("/posts", response_model=PostListResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            response = stub.ListPosts(
                post_service_pb2.ListPostsRequest(
                    page=page,
                    per_page=per_page,
                    user_id=user["id"],
                )
            )

            return PostListResponse(
                posts=[parse_post(p) for p in response.posts],
                total=response.total,
                page=response.page,
                per_page=response.per_page,
            )
        except grpc.RpcError as e:
            handle_grpc_error(e)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    print(path)
    if path.startswith("posts"):
        raise HTTPException(status_code=404, detail="Handled separately")

    print(f"[PROXY] Forwarding to user-service: /{path}")
    response = await proxy_request(request, f"/{path}")
    try:
        data = response.json()
    except Exception:
        data = {"detail": response.text}

    return JSONResponse(
        status_code=response.status_code,
        content=data,
    )


@app.post("/posts/{post_id}/view")
async def view_post(post_id: str, user: dict = Depends(get_current_user)):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            stub.ViewPost(
                post_service_pb2.ViewPostRequest(post_id=post_id, user_id=user["id"])
            )
            return {"message": "View recorded"}
        except grpc.RpcError as e:
            handle_grpc_error(e)


@app.post("/posts/{post_id}/like")
async def like_post(post_id: str, user: dict = Depends(get_current_user)):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            stub.LikePost(
                post_service_pb2.LikePostRequest(post_id=post_id, user_id=user["id"])
            )
            return {"message": "Like recorded"}
        except grpc.RpcError as e:
            handle_grpc_error(e)


class CommentCreate(BaseModel):
    content: str


@app.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: str, comment: CommentCreate, user: dict = Depends(get_current_user)
):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            stub.AddComment(
                post_service_pb2.AddCommentRequest(
                    post_id=post_id, user_id=user["id"], content=comment.content
                )
            )
            return {"message": "Comment added"}
        except grpc.RpcError as e:
            handle_grpc_error(e)


class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    per_page: int


@app.get("/posts/{post_id}/comments", response_model=CommentListResponse)
async def get_comments(
    post_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    with grpc.insecure_channel("post-service:50051") as channel:
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        try:
            response = stub.GetComments(
                post_service_pb2.GetCommentsRequest(
                    post_id=post_id, page=page, per_page=per_page
                )
            )

            return CommentListResponse(
                comments=[
                    CommentResponse(
                        id=c.id,
                        post_id=c.post_id,
                        user_id=c.user_id,
                        content=c.content,
                        created_at=datetime.fromisoformat(c.created_at),
                    )
                    for c in response.comments
                ],
                total=response.total,
                page=response.page,
                per_page=response.per_page,
            )
        except grpc.RpcError as e:
            handle_grpc_error(e)


def parse_post(grpc_post):
    return PostResponse(
        id=grpc_post.id,
        title=grpc_post.title,
        description=grpc_post.description,
        user_id=grpc_post.user_id,
        created_at=datetime.fromisoformat(grpc_post.created_at),
        updated_at=datetime.fromisoformat(grpc_post.updated_at),
        is_private=grpc_post.is_private,
        tags=grpc_post.tags,
    )


def handle_grpc_error(e: grpc.RpcError):
    print("gRPC ERROR CODE:", e.code())
    print("gRPC ERROR DETAILS:", e.details())
    error_map = {
        grpc.StatusCode.NOT_FOUND: (404, "Post not found"),
        grpc.StatusCode.PERMISSION_DENIED: (403, "Permission denied"),
        grpc.StatusCode.INVALID_ARGUMENT: (400, "Invalid request data"),
        grpc.StatusCode.UNAUTHENTICATED: (401, "Authentication required"),
    }

    status_code, detail = error_map.get(
        getattr(e, "code", lambda: None)(), (500, "Internal server error")
    )
    raise HTTPException(status_code=status_code, detail=detail)
