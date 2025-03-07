import httpx
import jwt
import os
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, HTTPException

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

app = FastAPI()


def verify_token(token: str):
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
        response = await client.request(
            method=request.method,
            url=f"http://user-service:8000{path}",
            headers=request.headers.raw,
            content=await request.body(),
        )
        return response


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    response = await proxy_request(request, f"/{path}")
    return JSONResponse(
        content=response.json(),
        status_code=response.status_code,
        headers=dict(response.headers),
    )
