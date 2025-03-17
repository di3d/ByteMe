#!/bin/bash

echo "Setting up Python virtual environment for ByteMe Stripe service..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment in .venv..."
  python3 -m venv .venv
else
  echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install requirements from the correct location
echo "Installing requirements..."
pip install -r stripe/requirements.txt

echo "Installation complete! Virtual environment is now active."
echo "To deactivate the environment, type 'deactivate'"
echo "To activate the environment again, run 'source .venv/bin/activate'"

# Display installed packages
echo ""
echo "Installed packages:"
pip list
