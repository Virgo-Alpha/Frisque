# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Add arguments for user and group IDs
ARG UID=1000
ARG GID=1000

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_TIMEOUT=300
ENV PIP_RETRIES=5

# Create a non-root user
# This creates a group and user named 'devuser' with the provided IDs
RUN groupadd -g $GID -o devuser && \
    useradd -m -u $UID -g $GID -o -s /bin/bash devuser

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Change ownership of the app directory to our new user
RUN chown -R devuser:devuser /app

# Switch to our new user
USER devuser