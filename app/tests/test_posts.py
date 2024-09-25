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

# Test creating a new post
@pytest.mark.asyncio
async def test_create_post(client, clean_db):
    # Create a user first
    clean_db.users.insert_one({"fullName": "Test User", "email": "test@gmail.com", "user_id": "test_user_id"})
    response = client.post(
        "/posts",
        json={"title": "Test Post", "content": "This is a test post", "user_id": "test_user_id"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "post_id" in data
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post"
    assert data["user_id"] == "test_user_id"

    # Verify post was added to the database
    post = clean_db.posts.find_one({"post_id": data["post_id"]})
    assert post is not None
    # remove the post from the database
    clean_db.posts.delete_one({"post_id": data["post_id"]})

    # remove the user from the database
    clean_db.users.delete_one({"user_id": "test_user_id"})

# Test creating a duplicate post
@pytest.mark.asyncio
async def test_create_duplicate_post(client, clean_db):
    # Create a user first
    clean_db.users.insert_one({"fullName": "Test User", "email": "test@gmail.com", "user_id": "test_user_id"})
    init_response = client.post(
        "/posts",
        json={"title": "Test Post", "content": "This is a test post", "user_id": "test_user_id"}
    )
    init_post_id = init_response.json()['post_id']
    
    # Try to create the same post again
    response = client.post(
        "/posts",
        json={"title": "Test Post", "content": "This is a test post", "user_id": "test_user_id"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Post already exists"
    clean_db.posts.delete_one({"post_id": init_post_id})
    clean_db.users.delete_one({"user_id": "test_user_id"})

# Test creating a post with a non-existent user
@pytest.mark.asyncio
async def test_create_post_with_non_existent_user(client, clean_db):
    response = client.post(
        "/posts",
        json={"title": "Test Post", "content": "This is a test post", "user_id": "non_existent_user_id"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User does not exist"

# Test getting all posts
@pytest.mark.asyncio
async def test_get_all_posts(client, clean_db):
    # Create a user first
    clean_db.users.insert_one({"fullName": "Test User", "email": "test@gmail.com", "user_id": "test_user_id"})
    clean_db.posts.insert_one({"title": "Test Post", "content": "This is a test post", "user_id": "test_user_id", "post_id": "test_post_id"})
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()['posts']
    assert isinstance(data, list)
    assert len(data) > 0
    clean_db.posts.delete_one({"post_id": "test_post_id"})
    clean_db.users.delete_one({"user_id": "test_user_id"})
    
# Test getting a post by ID
@pytest.mark.asyncio
async def test_get_post_by_id(client, clean_db):
    # Create a user first
    clean_db.users.insert_one({"fullName": "Test User", "email": "test@gmail.com", "user_id": "test_user_id"})
    clean_db.posts.insert_one({"title": "Test Post", "content": "This is a test post", "user_id": "test_user_id", "post_id": "test_post_id"})
    response = client.get("/posts/test_post_id")
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == "test_post_id"
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post"
    assert data["user_id"] == "test_user_id"
    clean_db.posts.delete_one({"post_id": "test_post_id"})
    clean_db.users.delete_one({"user_id": "test_user_id"})

# Test getting a non-existent post
@pytest.mark.asyncio
async def test_get_nonexistent_post(client, clean_db):
    response = client.get("/posts/non_existent_post_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

# Test updating a post
@pytest.mark.asyncio
async def test_update_post(client, clean_db):
    # Create a user first
    clean_db.users.insert_one({"fullName": "Test User", "email": "test@gmail.com", "user_id": "test_user_id"})
    clean_db.posts.insert_one({"title": "Test Post", "content": "This is a test post", "user_id": "test_user_id", "post_id": "test_post_id"})
    response = client.put(
        "/posts/test_post_id",
        json={"title": "Updated Post", "content": "This is an updated post", "user_id": "test_user_id"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == "test_post_id"
    assert data["title"] == "Updated Post"
    assert data["content"] == "This is an updated post"
    assert data["user_id"] == "test_user_id"

    # Verify the update in the database
    post = clean_db.posts.find_one({"post_id": "test_post_id"})
    assert post["title"] == "Updated Post"
    assert post["content"] == "This is an updated post"
    clean_db.posts.delete_one({"post_id": "test_post_id"})
    clean_db.users.delete_one({"user_id": "test_user_id"})


# Test deleting a post
@pytest.mark.asyncio
async def test_delete_post(client, clean_db):
    # Create a user and a post first
    clean_db.users.insert_one({"fullName": "Test User", "email": "test@gmail.com", "user_id": "test_user_id"})
    clean_db.posts.insert_one({"title": "Test Post", "content": "This is a test post", "user_id": "test_user_id", "post_id": "test_post_id"})
    response = client.delete("/posts/test_post_id")
    assert response.status_code == 204

    # Verify the post was deleted from the database
    post = clean_db.posts.find_one({"post_id": "test_post_id"})
    assert post is None
    clean_db.posts.delete_one({"post_id": "test_post_id"})
    clean_db.users.delete_one({"user_id": "test_user_id"})

# Test deleting a non-existent post
@pytest.mark.asyncio    
async def test_delete_nonexistent_post(client, clean_db):
    response = client.delete("/posts/non_existent_post_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"
    



    
