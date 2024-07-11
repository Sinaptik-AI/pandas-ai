# #!/bin/bash
# # Load environment variables from .env file if it exists
# if [ -f .env ]; then
#     log "Loading environment variables from .env file"
#     export $(cat .env | sed 's/#.*//g' | xargs)
# else
#     log ".env file not found, skipping"
# fi

# source $(poetry env info --path)/Scripts/activate


# poetry lock --no-update

# make install

# /bin/sh wait-for-it.sh

# # Run database migrations
# make migrate

# # Start the server in the background
# make start



#!/bin/bash

log() {
    echo "$1"
}

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    log "Loading environment variables from .env file"
    export $(cat .env | sed 's/#.*//g' | xargs)
else
    log ".env file not found, skipping"
fi

# Activate the Poetry environment
source $(poetry env info --path)/bin/activate

# Ensure dependencies are locked and installed
poetry lock --no-update
poetry install --no-root

# Run the wait-for-it script to ensure PostgreSQL is ready
/wait-for-it.sh db_host:5432 -- echo "PostgreSQL is up"

# Run database migrations
make migrate

# Start the server
make start
