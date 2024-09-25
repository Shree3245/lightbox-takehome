from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid1
from bson import json_util
import json
from typing import List

from models.post_models import Post, PostResponse, PostList
from dev_init import mongo_client

router = APIRouter()

mongo_client = mongo_client()
posts = mongo_client['posts']
users = mongo_client['users']

@router.post("/posts", status_code=status.HTTP_200_OK)
async def create_post(post: Post) -> JSONResponse:
    """
    Create a new post.

    This endpoint creates a new post with the provided information.

    Args:
        post (Post): The post information for creation.

    Returns:
        JSONResponse: The created post's information in JSON format.

    Raises:
        HTTPException: If the user does not exist or if a post with the same title already exists.
    """
    user_exists = users.find_one({"user_id": post.user_id})
    if not user_exists:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    post_exists = posts.find_one({"title": post.title})
    if post_exists:
        raise HTTPException(status_code=400, detail="Post already exists")
    
    post_id = str(uuid1())
    post_data = post.model_dump()
    post_data['post_id'] = post_id
    posts.insert_one(post_data)
    return JSONResponse(content=PostResponse(**post_data).model_dump(), status_code=200)

@router.get("/posts")
async def get_posts() -> JSONResponse:
    """
    Get all posts.

    This endpoint retrieves information for all posts.

    Returns:
        JSONResponse: A list containing information for all posts in JSON format.

    Raises:
        HTTPException: If an error occurs while retrieving the posts.
    """
    try:
        all_posts = list(posts.find({}, {"_id": 0, "post_id": 1, "title": 1, "content": 1, "user_id": 1}))
        json_compatible_posts = json.loads(json_util.dumps(all_posts))
        return JSONResponse(content=PostList(posts=json_compatible_posts).model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/posts/{post_id}")
async def get_post_by_id(post_id: str) -> JSONResponse:
    """
    Get a post by ID.

    This endpoint retrieves information for a specific post based on its post ID.

    Args:
        post_id (str): The unique identifier of the post.

    Returns:
        JSONResponse: The post's information in JSON format.

    Raises:
        HTTPException: If the post is not found.
    """
    post = posts.find_one({"post_id": post_id}, {"_id": 0, "post_id": 1, "title": 1, "content": 1, "user_id": 1})
    if post:
        return JSONResponse(content=PostResponse(**post).model_dump())
    else:
        raise HTTPException(status_code=404, detail="Post not found")

@router.put("/posts/{post_id}")
async def update_post(post_id: str, post: Post) -> JSONResponse:
    """
    Update a post.

    This endpoint updates the information for an existing post.

    Args:
        post_id (str): The unique identifier of the post to update.
        post (Post): The updated post information.

    Returns:
        JSONResponse: The updated post's information in JSON format.

    Raises:
        HTTPException: If the post is not found or if the user does not exist.
    """
    post_exists = posts.find_one({"post_id": post_id})
    if not post_exists:
        raise HTTPException(status_code=404, detail="Post not found")

    user_exists = users.find_one({"user_id": post.user_id})
    if not user_exists:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    updated_post = post.model_dump()
    updated_post['post_id'] = post_id
    posts.update_one({"post_id": post_id}, {"$set": updated_post})
    return JSONResponse(content=PostResponse(**updated_post).model_dump())

@router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: str) -> JSONResponse:
    """
    Delete a post.

    This endpoint deletes a post based on its post ID.

    Args:
        post_id (str): The unique identifier of the post to delete.

    Returns:
        JSONResponse: A confirmation message in JSON format.

    Raises:
        HTTPException: If the post is not found.
    """
    post_exists = posts.find_one({"post_id": post_id})
    if not post_exists:
        raise HTTPException(status_code=404, detail="Post not found")
    
    posts.delete_one({"post_id": post_id})
    return JSONResponse(content={"message": "Post deleted successfully"}, status_code=204)