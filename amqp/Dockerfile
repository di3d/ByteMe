# Use the official Python image as the base image
FROM python:3.9-slim

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy requirements.txt to the container
COPY requirements.txt ./

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5672

# Command to run the application
CMD ["python", "amqp_setup.py"]