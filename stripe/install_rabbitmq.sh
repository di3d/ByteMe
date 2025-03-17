#!/bin/bash

# RabbitMQ installation helper script
# This script helps install RabbitMQ on different operating systems

echo "RabbitMQ Installation Helper"
echo "==========================="

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install RabbitMQ
    echo "Installing RabbitMQ using Homebrew..."
    brew install rabbitmq
    
    echo "Starting RabbitMQ service..."
    brew services start rabbitmq
    
    echo ""
    echo "RabbitMQ has been installed and started!"
    echo "Management plugin available at: http://localhost:15672"
    echo "Default username and password: guest / guest"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Detected Linux"
    
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        echo "Detected Debian/Ubuntu distribution"
        
        echo "Adding RabbitMQ signing key..."
        curl -fsSL https://packages.erlang-solutions.com/ubuntu/erlang_solutions.asc | sudo apt-key add -
        
        echo "Adding RabbitMQ repository..."
        sudo apt-get install apt-transport-https
        sudo apt-add-repository "deb https://dl.bintray.com/rabbitmq/debian $(lsb_release -sc) main"
        
        echo "Updating package lists..."
        sudo apt-get update
        
        echo "Installing RabbitMQ..."
        sudo apt-get install -y rabbitmq-server
        
        echo "Starting RabbitMQ service..."
        sudo systemctl start rabbitmq-server
        sudo systemctl enable rabbitmq-server
        
        echo "Enabling management plugin..."
        sudo rabbitmq-plugins enable rabbitmq_management
        
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS/Fedora
        echo "Detected RHEL/CentOS/Fedora distribution"
        
        echo "Installing necessary packages..."
        sudo yum install -y epel-release
        
        echo "Adding RabbitMQ repository..."
        curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.rpm.sh | sudo bash
        
        echo "Installing RabbitMQ and dependencies..."
        sudo yum install -y rabbitmq-server
        
        echo "Starting RabbitMQ service..."
        sudo systemctl start rabbitmq-server
        sudo systemctl enable rabbitmq-server
        
        echo "Enabling management plugin..."
        sudo rabbitmq-plugins enable rabbitmq_management
    else
        echo "Unsupported Linux distribution. Please install RabbitMQ manually."
        exit 1
    fi
    
    echo ""
    echo "RabbitMQ has been installed and started!"
    echo "Management plugin available at: http://localhost:15672"
    echo "Default username and password: guest / guest"
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "Detected Windows"
    echo "Please download and install RabbitMQ from: https://www.rabbitmq.com/install-windows.html"
    echo ""
    echo "After installation, you can access the management plugin at: http://localhost:15672"
    echo "Default username and password: guest / guest"
    
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Please install RabbitMQ manually from: https://www.rabbitmq.com/download.html"
fi
