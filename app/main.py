from fastapi import FastAPI
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Profile Match API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://profile-match-app-20260819.s3-website-ap-northeast-1.amazonaws.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth.router,
    prefix="/api"
)


@app.get("/")
def root():
    return {
        "message": "Profile Match API is running"
    }
