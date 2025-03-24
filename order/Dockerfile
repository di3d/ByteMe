# Use the official Python image as the base image
FROM python:3.9-slim

# # Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy requirements.txt to the container
COPY requirements.txt ./

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5002

# Ensure migrations run before starting the service
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=5002"]