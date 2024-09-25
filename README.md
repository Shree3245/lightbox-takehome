# FastAPI User and Post Management API

This project is a FastAPI-based API for managing users and posts. It provides endpoints for creating, reading, updating, and deleting both users and posts.
This app can be found on the URL https://api.hirehack.me
The documentations can be found here

-   ReDoc documentation: `https://api.hirehack.me/redoc`
-   Swagger UI documentation: `https://api.hirehack.me/docs`

## Features

-   User management (CRUD operations)
-   Post management (CRUD operations)
-   JSON responses for all endpoints
-   MongoDB integration for data storage
-   Comprehensive API documentation using ReDoc
-   Dockerized application for easy deployment
-   SSL/TLS support using Traefik
-   Deployment instructions for Amazon EC2

## Prerequisites

Before you begin, ensure you have met the following requirements:

-   Python 3.7+
-   pip (Python package manager)
-   MongoDB installed and running
-   Docker and Docker Compose installed
-   An Amazon EC2 instance (for deployment)

## Installation

1. Clone the repository:

    ```
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. Create a virtual environment and activate it:

    ```
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the root directory of the project.
2. Add the following environment variables:
    ```
    MONGODB_URL=mongodb://localhost:27017
    DATABASE_NAME=your_database_name
    ```

## Running the Application Locally

To run the application locally, use the following command:

```
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access the API documentation:

-   ReDoc documentation: `http://localhost:8000/redoc`
-   Swagger UI documentation: `http://localhost:8000/docs`

## API Endpoints

### Users

-   `POST /users`: Create a new user
-   `GET /users`: Get all users
-   `GET /users/{user_id}`: Get a specific user
-   `PUT /users/{user_id}`: Update a user
-   `DELETE /users/{user_id}`: Delete a user

### Posts

-   `POST /posts`: Create a new post
-   `GET /posts`: Get all posts
-   `GET /posts/{post_id}`: Get a specific post
-   `PUT /posts/{post_id}`: Update a post
-   `DELETE /posts/{post_id}`: Delete a post

## Usage Examples

Here are some examples of how to use the API with curl:

### Create a new user

```bash
curl -X POST "http://localhost:8000/users" -H "Content-Type: application/json" -d '{"fullName": "John Doe", "email": "john@example.com"}'
```

### Create a new post

```bash
curl -X POST "http://localhost:8000/posts" -H "Content-Type: application/json" -d '{"title": "My First Post", "content": "This is the content of my first post.", "user_id": "user_id_here"}'
```

### Get all posts

```bash
curl "http://localhost:8000/posts"
```

## Deployment

This project uses Docker, Docker Compose, and Traefik to create a scalable and secure deployment on an Amazon EC2 instance.

### Prerequisites for Deployment

1. An Amazon EC2 instance with Docker and Docker Compose installed
2. A domain name pointed to your EC2 instance's public IP
3. Open ports 80 and 443 on your EC2 security group

### Deployment Steps

1. SSH into your EC2 instance.

2. Clone the repository and navigate to the project directory.

3. Create a `docker-compose.yml` file with the following content:

```yaml
version: "3"

services:
    app:
        build: .
        environment:
            - MONGODB_URL=mongodb://mongo:27017
        depends_on:
            - mongo
        labels:
            - "traefik.enable=true"
            - "traefik.http.routers.app.rule=Host(`your_domain.com`)"
            - "traefik.http.routers.app.entrypoints=websecure"
            - "traefik.http.routers.app.tls.certresolver=myresolver"

    mongo:
        image: mongo:latest
        volumes:
            - mongo_data:/data/db

    traefik:
        image: traefik:v2.5
        command:
            - "--api.insecure=true"
            - "--providers.docker=true"
            - "--providers.docker.exposedbydefault=false"
            - "--entrypoints.web.address=:80"
            - "--entrypoints.websecure.address=:443"
            - "--certificatesresolvers.myresolver.acme.httpchallenge=true"
            - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
            - "--certificatesresolvers.myresolver.acme.email=your_email@example.com"
            - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
        ports:
            - "80:80"
            - "443:443"
        volumes:
            - "/var/run/docker.sock:/var/run/docker.sock:ro"
            - "./letsencrypt:/letsencrypt"

volumes:
    mongo_data:
```

4. Create a `Dockerfile` in the project root with the following content:

```Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

5. Build and start the Docker containers:

```bash
docker-compose up -d
```

6. Your application should now be accessible at `https://your_domain.com`, with automatic SSL/TLS certificate management handled by Traefik.

### Updating the Deployment

To update your deployment with new changes:

1. Pull the latest changes from your repository.
2. Rebuild and restart the containers:

```bash
docker-compose up -d --build
```

This setup provides a scalable and secure deployment of your FastAPI application, with automatic SSL/TLS certificate management and easy updates.

## Contributing

Contributions to this project are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
