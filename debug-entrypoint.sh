#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Configure logging
export PYTHONUNBUFFERED=1
export LOG_LEVEL=DEBUG

# Redirect stdout and stderr to a log file
exec > >(tee -a /app/logs/app.log) 2>&1

echo "Starting AI Trailer Generator in debug mode at $(date)"

# Run the application
exec "$@"
