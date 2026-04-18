#!/bin/bash

# Quick Test Script - For validation (not full experiment)
# Use this to verify your setup is working before running full tests

echo "Quick Load Balancing Test"
echo "=========================="
echo ""

# Start Round Robin configuration
echo "Starting Round Robin configuration..."
cd ../experiment
docker-compose -f docker-compose-rr.yml up -d

echo "Waiting for services to start (20 seconds)..."
sleep 20

# Quick test
echo ""
echo "Running quick load test..."
cd ../tests
artillery quick --count 50 --num 10 http://localhost:8080/api/products

echo ""
echo "Test complete!"
echo ""
echo "Check the output above for response times and success rate."
echo ""
echo "To stop services, run:"
echo "cd ../experiment && docker-compose -f docker-compose-rr.yml down"

