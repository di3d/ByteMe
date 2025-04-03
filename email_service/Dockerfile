# Use a Python base image
FROM python:3.9-slim

# Set the working directory to the root of the project
WORKDIR /app

# Copy the entire ByteMe project into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r email_service/requirements.txt

# Set the PYTHONPATH to the root directory
ENV PYTHONPATH=/app

# Run the email_service as a module from the root
CMD ["python", "-m", "email_service.app"]
