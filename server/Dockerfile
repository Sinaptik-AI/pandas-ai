# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN poetry install --no-root

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Copy entrypoint script to the container
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Run the entrypoint script
CMD ["/startup.sh"]