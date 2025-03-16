# Use the official Python image as the base image
FROM python:3-slim

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy requirements.txt to the container
COPY requirements.txt ./

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Install Firebase CLI
RUN apt-get update && apt-get install -y curl && \
    curl -sL https://firebase.tools | bash

# Copy the rest of the application code
COPY ./Customer.py .

# Expose the port the app runs on (if applicable)
# EXPOSE 5000

# Command to run the application
CMD ["python", "./Customer.py"]
