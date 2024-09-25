import sys
import os
from pathlib import Path

# Add the parent directory of 'app' to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import testing modules
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Import app
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mongo_client():
    mongo_client = MongoClient(os.getenv('MONGO_HOST'))
    yield mongo_client
    mongo_client.close()

@pytest.fixture
def clean_db(mongo_client):
    test_db = mongo_client['takehome']
    yield test_db


# Test creating a new user
@pytest.mark.asyncio
async def test_create_user(client, clean_db):
    response = client.post(
        "/users",
        json={"fullName": "Test User", "email": "test@gmail.com"}
    )
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["fullName"] == "Test User"
    assert data["email"] == "test@gmail.com"

    # Verify user was added to the database
    user = clean_db.users.find_one({"email": "test@gmail.com"})
    user_id = user['user_id']
    clean_db.users.delete_one({"user_id": user_id})
    assert user is not None

# Test creating a duplicate user
@pytest.mark.asyncio
async def test_create_duplicate_user(client, clean_db):
    # First, create a user
    init_response = client.post(
        "/users",
        json={"fullName": "Duplicate User", "email": "duplicate@example.com"}
    )
    init_user_id = init_response.json()['user_id']
    
    # Try to create the same user again
    response = client.post(
        "/users",
        json={"fullName": "Duplicate User", "email": "duplicate@example.com", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"
    clean_db.users.delete_one({"user_id": init_user_id})

# Test getting all users
@pytest.mark.asyncio
async def test_get_all_users(client, clean_db):
    # First, add a user to the database
    clean_db.users.insert_one({"fullName": "Test User", "email": "test@example.com", "user_id": "testid"})
    
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()['users']
    assert isinstance(users, list)
    assert len(users) > 0
    clean_db.users.delete_one({"user_id": "testid"})

# Test getting a user by ID
@pytest.mark.asyncio
async def test_get_user_by_id(client, clean_db):
    # First, add a user to the database
    user_id = "testid123"
    clean_db.users.insert_one({"fullName": "Get User", "email": "get@example.com", "user_id": user_id})

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["user_id"] == user_id
    assert user["fullName"] == "Get User"
    assert user["email"] == "get@example.com"
    clean_db.users.delete_one({"user_id": user_id})

# Test getting a non-existent user
def test_get_nonexistent_user(client):
    response = client.get("/users/nonexistentid")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Test updating a user
@pytest.mark.asyncio
async def test_update_user(client, clean_db):
    # First, add a user to the database
    user_id = "updateid123"
    clean_db.users.insert_one({"fullName": "Update User", "email": "update@example.com", "user_id": user_id})

    # Now, update this user
    update_response = client.put(
        f"/users/{user_id}",
        json={"fullName": "Updated User", "email": "updated@example.com"}
    )
    assert update_response.status_code == 200
    updated_user = update_response.json()
    assert updated_user["fullName"] == "Updated User"
    assert updated_user["email"] == "updated@example.com"

    # Verify the update in the database
    user = clean_db.users.find_one({"user_id": user_id})
    assert user["fullName"] == "Updated User"
    assert user["email"] == "updated@example.com"
    clean_db.users.delete_one({"user_id": user_id})

# Test deleting a user
@pytest.mark.asyncio
async def test_delete_user(client, clean_db):
    # First, add a user to the database
    user_id = "deleteid123"
    clean_db.users.insert_one({"fullName": "Delete User", "email": "delete@example.com", "user_id": user_id})

    # Now, delete this user
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    # Verify the user was deleted from the database
    user = clean_db.users.find_one({"user_id": user_id})
    assert user is None
    clean_db.users.delete_one({"user_id": user_id})

# Test deleting a non-existent user
def test_delete_nonexistent_user(client):
    response = client.delete("/users/nonexistentid")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"