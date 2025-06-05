#!/bin/bash
# Test script to run docker-compose up and check backend and frontend health

set -e

echo "Starting docker-compose up..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 8

echo "Checking backend /health endpoint..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

echo "Checking frontend / route..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)

echo "Stopping and removing containers..."
docker-compose down

if [ "$BACKEND_STATUS" -eq 200 ] && [ "$FRONTEND_STATUS" -eq 200 ]; then
  echo "SUCCESS: Both backend and frontend are up and healthy."
  exit 0
else
  echo "FAIL: Backend status: $BACKEND_STATUS, Frontend status: $FRONTEND_STATUS"
  exit 1
fi
