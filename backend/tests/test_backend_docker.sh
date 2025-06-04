#!/bin/bash
# Test script to build and run the backend Docker container and check the /health endpoint

set -e

IMAGE_NAME=gcp-ai-cost-optimizer-backend:test

echo "Building Docker image..."
docker build -t $IMAGE_NAME /Users/vmuniyappan/trash/ai-app/gcp-ai-cost-optimizer

echo "Running backend container..."
CONTAINER_ID=$(docker run -d -p 8000:8000 $IMAGE_NAME)

# Wait for the server to start
echo "Waiting for backend to start..."
sleep 5

echo "Checking /health endpoint..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

# Cleanup
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

if [ "$STATUS" -eq 200 ]; then
  echo "SUCCESS: /health endpoint returned 200 OK"
  exit 0
else
  echo "FAIL: /health endpoint did not return 200 OK (got $STATUS)"
  exit 1
fi
