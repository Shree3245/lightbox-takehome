# Import fastapi modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from routes.users import router as users_router
from routes.posts import router as posts_router

# Init fastapi app
app = FastAPI()

# Add cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Add routes
app.include_router(users_router, tags=["users"])
app.include_router(posts_router, tags=["posts"])
