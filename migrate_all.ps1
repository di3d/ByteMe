# Define the list of microservice directories
$microservices = @("customer", "order", "recommendation", "delivery")

# Loop through each microservice directory
foreach ($service in $microservices) {
    Write-Host "Processing $service..."
    
    # Enter the microservice directory
    if (Test-Path $service) {
        Set-Location $service
        Write-Host "Entered directory: $service"
        
        # Check if the expected Python file exists
        $serviceFile = "$service.py"
        if (Test-Path $serviceFile) {
            Write-Host "Found Flask application: $serviceFile"

            # Activate virtual environment if available
            if (Test-Path "venv/Scripts/Activate.ps1") {
                & "venv/Scripts/Activate.ps1"
                Write-Host "Activated virtual environment"
            }
            
            # Set FLASK_APP environment variable
            $env:FLASK_APP = $serviceFile
            Write-Host "Set FLASK_APP to $serviceFile"
            
            # Set environment variable to skip AMQP setup
            $env:SKIP_AMQP_SETUP = "1"
            
            # Run Flask migration commands
            if (-Not (Test-Path "migrations")) {
                flask db init
            }
            flask db migrate -m "Auto migration"
            flask db upgrade

            # Deactivate virtual environment
            if (Test-Path "venv/Scripts/Activate.ps1") {
                & "venv/Scripts/Deactivate.ps1"
                Write-Host "Deactivated virtual environment"
            }
        } else {
            Write-Host "No Flask application found in $service, skipping..."
        }
        
        # Return to the main directory
        Set-Location ..
        Write-Host "Returned to main directory"
    } else {
        Write-Host "Directory $service not found, skipping..."
    }
}

Write-Host "Migration process completed!"