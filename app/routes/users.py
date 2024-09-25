from fastapi import APIRouter, status, HTTPException, Request
from fastapi.responses import JSONResponse
from uuid import uuid1
from bson import json_util
import json
from typing import List, Dict, Any

from models.user_models import UserRegister, UserResponse, UserList

from dev_init import mongo_client

router = APIRouter()

mongo_client = mongo_client()
users = mongo_client['users']

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserRegister) -> JSONResponse:
    """
    Create a new user.

    This endpoint creates a new user with the provided information.

    Args:
        user (UserRegister): The user information for registration.

    Returns:
        JSONResponse: The created user's information in JSON format.

    Raises:
        HTTPException: If a user with the same email already exists.
    """
    user_exists = users.find_one({"email": user.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = str(uuid1())
    user_data = user.model_dump()
    user_data['user_id'] = user_id
    users.insert_one(user_data)
    return JSONResponse(content=UserResponse(**user_data).model_dump())

@router.get("/users")
async def get_all_users() -> JSONResponse:
    """
    Get all users.

    This endpoint retrieves information for all registered users.

    Returns:
        JSONResponse: A list containing information for all users in JSON format.

    Raises:
        HTTPException: If an error occurs while retrieving the users.
    """
    try:
        all_users = list(users.find({}, {"_id": 0, "user_id": 1, "fullName": 1, "email": 1}))
        json_compatible_users = json.loads(json_util.dumps(all_users))
        return JSONResponse(content={"users": json_compatible_users})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/users/{user_id}")
async def get_user_by_id(user_id: str) -> JSONResponse:
    """
    Get a user by ID.

    This endpoint retrieves information for a specific user based on their user ID.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        JSONResponse: The user's information in JSON format.

    Raises:
        HTTPException: If the user is not found.
    """
    user = users.find_one({"user_id": user_id}, {"_id": 0, "user_id": 1, "fullName": 1, "email": 1})
    if user:
        return JSONResponse(content=user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{user_id}")
async def update_user(user_id: str, user: UserRegister) -> JSONResponse:
    """
    Update a user.

    This endpoint updates the information for an existing user.

    Args:
        user_id (str): The unique identifier of the user to update.
        user (UserRegister): The updated user information.

    Returns:
        JSONResponse: The updated user's information in JSON format.

    Raises:
        HTTPException: If the user is not found.
    """
    user_exists = users.find_one({"user_id": user_id})
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = user.model_dump()
    updated_user['user_id'] = user_id
    users.update_one({"user_id": user_id}, {"$set": updated_user})
    return JSONResponse(content=UserResponse(**updated_user).model_dump())

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: str) -> JSONResponse:
    """
    Delete a user.

    This endpoint deletes a user based on their user ID.

    Args:
        user_id (str): The unique identifier of the user to delete.

    Returns:
        JSONResponse: A confirmation message in JSON format.

    Raises:
        HTTPException: If the user is not found.
    """
    user_exists = users.find_one({"user_id": user_id})
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    users.delete_one({"user_id": user_id})
    return JSONResponse(content={"message": "User deleted successfully"}, status_code=204)