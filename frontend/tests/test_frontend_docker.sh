#!/bin/bash
# Test script to build and run the frontend Docker container and check the root route

set -e

IMAGE_NAME=gcp-ai-cost-optimizer-frontend:test

echo "Building frontend Docker image..."
docker build -t $IMAGE_NAME /Users/vmuniyappan/trash/ai-app/gcp-ai-cost-optimizer/frontend

echo "Running frontend container..."
CONTAINER_ID=$(docker run -d -p 5000:5000 $IMAGE_NAME)

# Wait for the server to start
echo "Waiting for frontend to start..."
sleep 5

echo "Checking / route..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)

# Cleanup
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

if [ "$STATUS" -eq 200 ]; then
  echo "SUCCESS: / route returned 200 OK"
  exit 0
else
  echo "FAIL: / route did not return 200 OK (got $STATUS)"
  exit 1
fi
