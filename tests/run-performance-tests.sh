#!/bin/bash

# Performance Test Execution Script (N=3)
# Optimized version with 3 runs per configuration
# Estimated time: 3-4 hours (vs 6-8 hours for N=5)
# N=3 is statistically acceptable for SINTA 2 journals

echo "=========================================================="
echo "Load Balancing Performance Test Suite (N=3)"
echo "Optimized for faster execution while maintaining validity"
echo "=========================================================="
echo ""

# Create data directory
mkdir -p ../data/performance_tests

echo "Data will be saved to: ../data/performance_tests/"
echo ""

# Function to run tests for a specific configuration
run_tests() {
    local strategy=$1
    local compose_file=$2

    echo "=========================================================="
    echo "Testing: $strategy Strategy"
    echo "=========================================================="

    # Start services
    echo "Starting services..."
    cd ../experiment
    docker-compose -f $compose_file up -d

    # Wait for services to be ready
    echo "Waiting for services to be ready (30 seconds)..."
    sleep 30

    # Run tests
    cd ../tests

    for run in {1..3}; do
        echo ""
        echo "Run #$run of 3"
        echo "----------------"

        # Low load test
        echo "Running LOW load test..."
        artillery run test-low-load.yml --output "../data/performance_tests/${strategy}-low-run${run}.json"
        sleep 10

        # Medium load test
        echo "Running MEDIUM load test..."
        artillery run test-medium-load.yml --output "../data/performance_tests/${strategy}-medium-run${run}.json"
        sleep 10

        # High load test
        echo "Running HIGH load test..."
        artillery run test-high-load.yml --output "../data/performance_tests/${strategy}-high-run${run}.json"
        sleep 10
    done

    # Stop services
    echo "Stopping services..."
    cd ../experiment
    docker-compose -f $compose_file down

    echo "$strategy tests completed!"
    echo ""
    sleep 5
}

# Run tests for each strategy
echo "Starting test execution..."
echo "Estimated total time: 3-4 hours"
echo ""

run_tests "round-robin" "docker-compose-rr.yml"
run_tests "least-conn" "docker-compose-lc.yml"
run_tests "weighted" "docker-compose-weighted.yml"

echo "=========================================================="
echo "All tests completed!"
echo "=========================================================="
echo ""
echo "Results saved in: ../data/performance_tests/"
echo ""
echo "Test Summary:"
echo "  - Strategies tested: 3 (Round-Robin, Least-Connection, Weighted)"
echo "  - Load levels: 3 (Low, Medium, High)"
echo "  - Replications: 3 (N=3)"
echo "  - Total files: 27 JSON files"
echo ""
echo "Statistical Note:"
echo "  N=3 provides sufficient statistical validity for:"
echo "  - Mean calculation"
echo "  - Standard deviation"
echo "  - Confidence intervals (with appropriate disclaimer)"
echo "  - Acceptable for SINTA 2 journals"
echo ""
echo "Next steps:"
echo "  1. Run failure tests: ./test-failure-scenarios-n3.sh"
echo "  2. Analyze data: python analyze_results.py"
echo "  3. Generate figures: python generate_figures.py"
echo ""

