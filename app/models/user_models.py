from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException
import re

class UserRegister(BaseModel):
    """
    User registration model.

    This model is used for creating new users and updating existing user information.
    """
    fullName: str = Field(
        ...,
        description="The full name of the user",
        example="John Doe",
        min_length=2,
        max_length=100
    )
    email: str = Field(
        ...,
        description="The email address of the user",
        example="johndoe@example.com"
    )

    @field_validator('email')
    def validate_email(cls, v):
        """Validate the email format."""
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise HTTPException(status_code=400, detail="Invalid email format")
        return v

    @field_validator('fullName')
    def validate_full_name(cls, v):
        """Validate the full name format."""
        if not re.match(r'^[a-zA-Z ]+$', v):
            raise HTTPException(status_code=400, detail="Invalid full name format. Only letters and spaces are allowed.")
        return v

class UserResponse(BaseModel):
    """
    User response model.

    This model is used for returning user information in API responses.
    """
    user_id: str = Field(..., description="The unique identifier of the user")
    fullName: str = Field(..., description="The full name of the user")
    email: str = Field(..., description="The email address of the user")

class UserList(BaseModel):
    """
    User list model.

    This model is used for returning a list of users in API responses.
    """
    users: list[UserResponse] = Field(..., description="List of users")