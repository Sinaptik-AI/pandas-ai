#!/bin/bash


# Load environment variables from .env file if it exists
if [ -f .env ]; then
    log "Loading environment variables from .env file"
    export $(cat .env | sed 's/#.*//g' | xargs)
else
    log ".env file not found, skipping"
fi

source $(poetry env info --path)/bin/activate


poetry lock --no-update

make install

/bin/sh wait-for-it.sh

# Run database migrations
make migrate

# Start the server in the background
make start
