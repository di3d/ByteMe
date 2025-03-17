#!/bin/bash

echo "Checking RabbitMQ status..."

# Check if RabbitMQ is running (this works on macOS with Homebrew)
if brew services list | grep rabbitmq | grep started > /dev/null; then
    echo "✅ RabbitMQ is running"
else
    echo "⚠️ RabbitMQ is not running. Attempting to start..."
    brew services start rabbitmq
    
    # Wait a moment for RabbitMQ to start
    echo "Waiting for RabbitMQ to initialize (10 seconds)..."
    sleep 10
    
    # Check again
    if brew services list | grep rabbitmq | grep started > /dev/null; then
        echo "✅ RabbitMQ started successfully"
    else
        echo "❌ Failed to start RabbitMQ. Your application will run with limited functionality."
    fi
fi

# Check if RabbitMQ port is accessible
echo "Checking if RabbitMQ port is accessible..."
if nc -z localhost 5672 >/dev/null 2>&1; then
    echo "✅ RabbitMQ port (5672) is accessible"
else
    echo "❌ RabbitMQ port (5672) is not accessible. Check if another service is using this port."
    echo "  The application will run with limited functionality."
fi

# Activate virtual environment
echo "Activating Python virtual environment..."
source .venv/bin/activate

# Set environment variables for better error messages
export PYTHONUNBUFFERED=1

# Start the application
echo "Starting Stripe payment service..."
python stripe/app.py
