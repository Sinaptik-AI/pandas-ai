#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Echo the Python path
echo "Python path: $(which python)"

# Activate the Poetry environment
source $(poetry env info --path)/bin/activate

make install

echo "Python path: $(which python)"

# Run database migrations
make migrate

# Start the server
make start
