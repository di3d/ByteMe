FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY ./scenario3/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./scenario3 .
COPY ./amqp ./amqp

# Set Python path
ENV PYTHONPATH=/app

# For debugging - list installed packages
RUN pip list

CMD ["python", "makeRefunds.py"]