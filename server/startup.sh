#!/bin/bash

# Function to log messages
log() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    log "Loading environment variables from .env file"
    export $(cat .env | sed 's/#.*//g' | xargs)
else
    log ".env file not found, skipping"
fi

# Echo the Python path
log "Python path before activating Poetry environment: $(which python)"

# Activate the Poetry environment
log "Activating Poetry environment"
source $(poetry env info --path)/bin/activate

# Echo the Python path after activating Poetry environment
log "Python path after activating Poetry environment: $(which python)"

# Update Poetry lock file
log "Updating Poetry lock file"
poetry lock --no-update

# Install dependencies
log "Installing dependencies"
make install

# Run database migrations
log "Running database migrations"
make migrate

# Start the server in the background
log "Starting the server"
make start
