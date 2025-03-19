#!/bin/bash

# Define the list of microservice directories
MICROSERVICES=("customer" "order" "recommendation" "delivery")

# Loop through each microservice directory
for SERVICE in "${MICROSERVICES[@]}"; do
    echo "Processing $SERVICE..."
    
    # Enter the microservice directory
    if [ -d "$SERVICE" ]; then
        cd "$SERVICE" || exit
        echo "Entered directory: $SERVICE"
        
        # Check if the expected Python file exists
        SERVICE_FILE="${SERVICE^}.py"  # Capitalize the first letter
        if [ -f "$SERVICE_FILE" ]; then
            echo "Found Flask application: $SERVICE_FILE"

            # Activate virtual environment if available
            if [ -f "venv/bin/activate" ]; then
                source venv/bin/activate
                echo "Activated virtual environment"
            fi
            
            # Set FLASK_APP environment variable
            export FLASK_APP="$SERVICE_FILE"
            echo "Set FLASK_APP to $SERVICE_FILE"
            
            # Run Flask migration commands
            flask db init || echo "Database already initialized."
            flask db migrate -m "Auto migration"
            flask db upgrade

            # Deactivate virtual environment
            if [ -f "venv/bin/activate" ]; then
                deactivate
                echo "Deactivated virtual environment"
            fi
        else
            echo "No Flask application found in $SERVICE, skipping..."
        fi
        
        # Return to the main directory
        cd ..
        echo "Returned to main directory"
    else
        echo "Directory $SERVICE not found, skipping..."
    fi
done

echo "Migration process completed!"
