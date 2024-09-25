from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException
import re

class Post(BaseModel):
    """
    Post model for creating and updating posts.
    """
    title: str = Field(..., description="The title of the post", min_length=1, max_length=100, example="My First Blog Post")
    content: str = Field(..., description="The content of the post", min_length=1, example="This is the content of my first blog post.")
    user_id: str = Field(..., description="The user id of the post author", example="123e4567-e89b-12d3-a456-426614174000")

class PostResponse(BaseModel):
    """
    Post response model for API outputs.
    """
    post_id: str = Field(..., description="The unique identifier of the post")
    title: str = Field(..., description="The title of the post")
    content: str = Field(..., description="The content of the post")
    user_id: str = Field(..., description="The user id of the post author")

class PostList(BaseModel):
    """
    Model for a list of posts.
    """
    posts: list[PostResponse] = Field(..., description="List of posts")