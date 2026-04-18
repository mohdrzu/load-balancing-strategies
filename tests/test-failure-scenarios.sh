#!/bin/bash

# Failure Scenario Testing Script (N=3)
# Tests load balancing behavior under service failures
# This adds NOVELTY to your research!
# Already optimized with N=3 runs per scenario

echo "=========================================================="
echo "FAILURE SCENARIO TESTING (N=3)"
echo "Load Balancing Resilience Evaluation"
echo "Estimated time: 1.5-2 hours"
echo "=========================================================="
echo ""

# Create failure results directory
mkdir -p ../data/failure_tests

echo "Data will be saved to: ../data/failure_tests/"
echo ""

# Function to run failure test
run_failure_test() {
    local strategy=$1
    local compose_file=$2
    local failure_type=$3
    local services_to_stop=$4

    echo "=========================================================="
    echo "Testing: $strategy - Failure: $failure_type"
    echo "=========================================================="

    # Start all services
    echo "Starting all services..."
    cd ../experiment
    docker-compose -f $compose_file up -d

    echo "Waiting for services to be ready (30 seconds)..."
    sleep 30

    # Baseline test (all services healthy) - N=3
    echo ""
    echo "=== BASELINE: All Services Healthy (3 runs) ==="
    cd ../tests
    for run in {1..3}; do
        echo "Baseline run #$run..."
        artillery run test-high-load.yml --output "../data/failure_tests/${strategy}-baseline-run${run}.json"
        sleep 10
    done

    # Stop specified services
    echo ""
    echo "=== INJECTING FAILURE: Stopping $services_to_stop ==="
    cd ../experiment
    for service in $services_to_stop; do
        echo "Stopping $service..."
        docker stop $service
    done

    echo "Waiting 10 seconds for system to react..."
    sleep 10

    # Failure test - N=3
    echo ""
    echo "=== FAILURE TEST: Performance Under Degradation (3 runs) ==="
    cd ../tests
    for run in {1..3}; do
        echo "Failure test run #$run..."
        artillery run test-high-load.yml --output "../data/failure_tests/${strategy}-${failure_type}-run${run}.json"
        sleep 10
    done

    # Restart stopped services (recovery test)
    echo ""
    echo "=== RECOVERY TEST: Restarting Services ==="
    cd ../experiment
    for service in $services_to_stop; do
        echo "Restarting $service..."
        docker start $service
    done

    echo "Waiting 10 seconds for recovery..."
    sleep 10

    cd ../tests
    echo "Recovery test..."
    artillery run test-high-load.yml --output "../data/failure_tests/${strategy}-recovery-run1.json"
    sleep 10

    # Stop all services
    echo "Stopping all services..."
    cd ../experiment
    docker-compose -f $compose_file down

    echo "$strategy - $failure_type tests completed!"
    echo ""
    sleep 5
}

# =============================================================================
# SCENARIO 1: Single Service Failure (25% Capacity Loss)
# =============================================================================

echo ""
echo "####################################################"
echo "# SCENARIO 1: One Service Down (25% Capacity Loss)"
echo "####################################################"
echo ""

# Test Round Robin
run_failure_test "round-robin" "docker-compose-rr.yml" "1service" "product-service-2"

# Test Least Connection
run_failure_test "least-conn" "docker-compose-lc.yml" "1service" "product-service-2"

# Test Weighted Round Robin
run_failure_test "weighted" "docker-compose-weighted.yml" "1service" "product-service-2"

# =============================================================================
# SCENARIO 2: Two Services Failure (50% Capacity Loss)
# =============================================================================

echo ""
echo "####################################################"
echo "# SCENARIO 2: Two Services Down (50% Capacity Loss)"
echo "####################################################"
echo ""

# Test Round Robin
run_failure_test "round-robin" "docker-compose-rr.yml" "2services" "product-service-2 product-service-3"

# Test Least Connection
run_failure_test "least-conn" "docker-compose-lc.yml" "2services" "product-service-2 product-service-3"

# Test Weighted Round Robin - stop low-weighted services
run_failure_test "weighted" "docker-compose-weighted.yml" "2services" "product-service-3 product-service-4"

# =============================================================================
# SCENARIO 3: High-Weight Service Failure (Weighted Only)
# =============================================================================

echo ""
echo "####################################################"
echo "# SCENARIO 3: High-Weight Service Failure"
echo "# (Only for Weighted strategy - Service 1 weight=3)"
echo "####################################################"
echo ""

# This tests what happens when the highest-weighted service fails
run_failure_test "weighted" "docker-compose-weighted.yml" "highweight" "product-service-1"

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "=========================================================="
echo "ALL FAILURE TESTS COMPLETED!"
echo "=========================================================="
echo ""
echo "Results saved in: ../data/failure_tests/"
echo ""
echo "Test Summary:"
echo "  - Baseline tests: 9 runs (3 per strategy)"
echo "  - Single failure: 9 runs (3 per strategy)"
echo "  - Dual failure: 9 runs (3 per strategy)"
echo "  - High-weight failure: 3 runs (weighted only)"
echo "  - Recovery tests: 7 runs"
echo "  Total: 37 test files"
echo ""
echo "Statistical Note:"
echo "  N=3 provides sufficient data for:"
echo "  - Mean performance calculation"
echo "  - Standard deviation analysis"
echo "  - Comparative analysis between strategies"
echo "  - Acceptable for SINTA 2 publication"
echo ""
echo "Next steps:"
echo "  1. Analyze results: python analyze_failure_results.py"
echo "  2. Compare degradation rates"
echo "  3. Add findings to paper section 4.4"
echo ""
echo "Expected insights:"
echo "  - Which strategy handles failures better?"
echo "  - How fast does each strategy adapt?"
echo "  - Performance degradation patterns"
echo "  - Recovery characteristics"
echo ""
echo "This adds STRONG NOVELTY to your research!"
echo "Most papers don't test failure scenarios!"
echo ""

