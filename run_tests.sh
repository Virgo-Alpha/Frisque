#!/bin/bash

# This script runs all pytest tests for the Frisque Django application
# inside the running Docker container.

# The 'set -e' command ensures that the script will exit immediately
# if any command fails, preventing unexpected behavior.
set -e

# --- Script Start ---
echo "Starting the test suite..."

# Run pytest inside the 'web' container.
# -v adds more verbose output.
docker-compose exec web pytest -v

echo "All tests passed successfully!"