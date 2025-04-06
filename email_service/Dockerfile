FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY email_service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY email_service email_service/
COPY amqp amqp/

# Set environment variables
ENV PYTHONPATH=/app

# For debugging
RUN ls -la /app/email_service
RUN python -c "import sys; print(sys.path)"

# Run the application
CMD ["python", "-m", "email_service.app"]