# Flask App Dockerization and Continuous Integration

This repository contains the code and setup for a Flask application with Docker containerization and continuous integration using pre-commit git hooks.

## Prerequisites

- Docker
- Git
- Python 3.x
- pip (Python package installer)

## Flask Application

The Flask application includes a basic endpoint `/score` which is used to demonstrate the containerization and testing.

## Containerization

### Dockerfile

The `Dockerfile` includes the necessary instructions to build a Docker image for the Flask app. It performs the following tasks:
1. Installs dependencies.
2. Copies `app.py` and `score.py`.
3. Launches the app using `python app.py`.

#### Dockerfile content:
```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]
