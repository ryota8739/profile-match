from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import users
from app.routers import bookmarks
from app.routers import matches
from app.routers import profile
from app.routers import messages

app = FastAPI(
    title="Profile Match API",
    version="0.1.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://profile-match-app-20260819.s3-website-ap-northeast-1.amazonaws.com",
        "http://profile-match-app-20260819.s3.ap-northeast-1.amazonaws.com"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(
    auth.router,
    prefix="/api"
)

app.include_router(
    users.router,
    prefix="/api"
)

app.include_router(
    bookmarks.router,
    prefix="/api"
)

app.include_router(
    matches.router,
    prefix="/api"
)

app.include_router(
    profile.router,
    prefix="/api"
)

app.include_router(
    messages.router,
    prefix="/api"
)

# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Profile Match API is running"
    }
