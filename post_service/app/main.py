from concurrent import futures
import uuid
import grpc
from datetime import datetime
import sys
import os
from kafka_producer import send_event

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../proto")))
from proto import post_service_pb2, post_service_pb2_grpc
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()
engine = create_engine(
    os.getenv("DATABASE_URL", "postgresql://user:password@db/users_db")
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Post(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True, server_default=text("gen_random_uuid()"))
    title = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_private = Column(Boolean, default=False)
    tags = Column(String)


class PostServicer(post_service_pb2_grpc.PostServiceServicer):
    comments_store = {}
    def CreatePost(self, request, context):
        db = SessionLocal()
        try:
            post = Post(
                title=request.title,
                description=request.description,
                user_id=request.user_id,
                is_private=request.is_private,
                tags=",".join(request.tags),
            )
            db.add(post)
            db.commit()
            db.refresh(post)
            return self._post_to_response(post)
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
        finally:
            db.close()

    def GetPost(self, request, context):
        db = SessionLocal()
        post = db.query(Post).filter(Post.id == request.id).first()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
        return self._post_to_response(post)

    def UpdatePost(self, request, context):
        db = SessionLocal()
        post = db.query(Post).filter(Post.id == request.id).first()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        post.title = request.title
        post.description = request.description
        post.is_private = request.is_private
        post.tags = ",".join(request.tags)
        post.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(post)
        return self._post_to_response(post)

    def DeletePost(self, request, context):
        db = SessionLocal()
        post = db.query(Post).filter(Post.id == request.id).first()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        db.delete(post)
        db.commit()
        return post_service_pb2.DeletePostResponse(success=True)

    def ListPosts(self, request, context):
        db = SessionLocal()
        query = db.query(Post)

        if request.user_id:
            query = query.filter(Post.user_id == request.user_id)

        total = query.count()
        posts = (
            query.offset((request.page - 1) * request.per_page)
            .limit(request.per_page)
            .all()
        )

        return post_service_pb2.ListPostsResponse(
            posts=[self._post_to_response(p) for p in posts],
            total=total,
            page=request.page,
            per_page=request.per_page,
        )
     
    def ViewPost(self, request, context):
        send_event("post_views", {
            "post_id": request.post_id,
            "user_id": request.user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        return post_service_pb2.ViewPostResponse()
    
    def LikePost(self, request, context):
        send_event("post_likes", {
            "post_id": request.post_id,
            "user_id": request.user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        return post_service_pb2.LikePostResponse()
    
    def CommentPost(self, request, context):
        comment_id = str(uuid.uuid4())
        comment = {
            "id": comment_id,
            "post_id": request.post_id,
            "user_id": request.user_id,
            "content": request.content,
            "created_at": datetime.utcnow().isoformat()
        }

        self.comments_store.setdefault(request.post_id, []).append(comment)

        send_event("post_comments", comment)

        return post_service_pb2.Comment(
            id=comment["id"],
            post_id=comment["post_id"],
            user_id=comment["user_id"],
            content=comment["content"],
            created_at=comment["created_at"]
        )

    def GetComments(self, request, context):
        comments = self.comments_store.get(request.post_id, [])
        return post_service_pb2.GetCommentsResponse(
            comments=[
                post_service_pb2.Comment(
                    id=c["id"],
                    post_id=c["post_id"],
                    user_id=c["user_id"],
                    content=c["content"],
                    created_at=c["created_at"]
                ) for c in comments
            ]
        )

        

    def _post_to_response(self, post):
        return post_service_pb2.PostResponse(
            id=post.id,
            title=post.title,
            description=post.description,
            user_id=post.user_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            is_private=post.is_private,
            tags=post.tags.split(",") if post.tags else [],
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_service_pb2_grpc.add_PostServiceServicer_to_server(PostServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    serve()
