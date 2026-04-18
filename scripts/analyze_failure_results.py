#!/usr/bin/env python3
"""
Analyze Failure Scenario Test Results
Calculates degradation rates, recovery metrics, and resilience scores.
Reads from data/failure_tests/ directory.
"""

import json
import glob
import os
from pathlib import Path
import statistics

def analyze_failure_scenarios(data_dir='data/failure_tests'):
    """Analyze failure test results"""
    
    print("=" * 70)
    print("FAILURE SCENARIO ANALYSIS")
    print("Evaluating Load Balancing Resilience")
    print("=" * 70)
    print()
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory {data_dir}/ not found!")
        print("Run test-failure-scenarios.sh first")
        return

    json_files = glob.glob(os.path.join(data_dir, '*.json'))
    if not json_files:
        print(f"❌ No JSON files found in {data_dir}/")
        print("Run test-failure-scenarios.sh first")
        return

    print(f"📁 Found {len(json_files)} failure test result files")
    print()

    results = {}
    
    # Parse all JSON files
    for json_file in sorted(json_files):
        try:
            with open(json_file) as f:
                data = json.load(f)
            
            filename = os.path.basename(json_file).replace('.json', '')
            parts = filename.split('-')
            
            # Parse strategy name
            if parts[0] == 'round':
                strategy = 'round-robin'
                scenario = parts[2]  # baseline, 1service, 2services, etc.
            elif parts[0] == 'least':
                strategy = 'least-conn'
                scenario = parts[2]
            elif parts[0] == 'weighted':
                strategy = 'weighted'
                scenario = parts[1]
            else:
                strategy = parts[0]
                scenario = parts[1]

            # Extract metrics from aggregate.summaries
            aggregate = data.get('aggregate', {})
            counters = aggregate.get('counters', {})
            summaries = aggregate.get('summaries', {})
            response_time = summaries.get('http.response_time', {})

            # Calculate actual RPS from timestamps
            first_ts = aggregate.get('firstCounterAt', 0)
            last_ts = aggregate.get('lastCounterAt', 0)
            duration_s = (last_ts - first_ts) / 1000 if (last_ts - first_ts) > 0 else 1
            total_req = counters.get('http.requests', 0)
            actual_rps = total_req / duration_s

            key = (strategy, scenario)
            if key not in results:
                results[key] = []
            
            results[key].append({
                'median': response_time.get('median', 0),
                'mean': response_time.get('mean', 0),
                'p95': response_time.get('p95', 0),
                'p99': response_time.get('p99', 0),
                'rps': actual_rps,
                'success': counters.get('http.codes.200', 0),
                'total': total_req,
                'failed': counters.get('vusers.failed', 0),
            })
            
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
    
    if not results:
        print("❌ No valid results found!")
        return

    # Calculate statistics
    print("=" * 70)
    print("RESILIENCE ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    strategies = set([s for s, _ in results.keys()])
    
    for strategy in sorted(strategies):
        print(f"\n{'='*70}")
        print(f"STRATEGY: {strategy.upper()}")
        print(f"{'='*70}")
        
        # Get baseline
        baseline_key = (strategy, 'baseline')
        if baseline_key not in results:
            print(f"⚠️  No baseline data for {strategy}")
            continue
        
        baseline_metrics = results[baseline_key]
        baseline_median = statistics.mean([m['median'] for m in baseline_metrics])
        baseline_rps = statistics.mean([m['rps'] for m in baseline_metrics])
        baseline_success = sum([m['success'] for m in baseline_metrics])
        baseline_total = sum([m['total'] for m in baseline_metrics])
        baseline_rate = (baseline_success / baseline_total * 100) if baseline_total > 0 else 0
        
        print(f"\nBASELINE (All Services Healthy):")
        print(f"  Median Response Time: {baseline_median:.1f} ms")
        print(f"  Throughput: {baseline_rps:.1f} req/s")
        print(f"  Success Rate: {baseline_rate:.2f}%")
        
        # Analyze failure scenarios
        scenarios = ['1service', '2services', 'highweight', 'recovery']
        
        for scenario in scenarios:
            failure_key = (strategy, scenario)
            if failure_key not in results:
                continue
            
            failure_metrics = results[failure_key]
            failure_median = statistics.mean([m['median'] for m in failure_metrics])
            failure_rps = statistics.mean([m['rps'] for m in failure_metrics])
            failure_success = sum([m['success'] for m in failure_metrics])
            failure_total = sum([m['total'] for m in failure_metrics])
            failure_rate = (failure_success / failure_total * 100) if failure_total > 0 else 0
            
            # Calculate degradation
            median_degradation = ((failure_median - baseline_median) / baseline_median * 100)
            rps_degradation = ((baseline_rps - failure_rps) / baseline_rps * 100) if baseline_rps > 0 else 0
            success_degradation = (baseline_rate - failure_rate)
            
            # Resilience score (lower is better)
            resilience_score = (abs(median_degradation) + abs(rps_degradation) + abs(success_degradation)) / 3

            print(f"\n{scenario.upper()} Scenario:")
            print(f"  Median RT: {failure_median:.1f} ms ({median_degradation:+.1f}%)")
            print(f"  Throughput: {failure_rps:.1f} req/s (↓{rps_degradation:.1f}%)")
            print(f"  Success Rate: {failure_rate:.2f}% ({-success_degradation:+.2f}pp)")
            print(f"  Resilience Score: {resilience_score:.2f} (lower = better)")
    
    # Comparative Analysis
    print(f"\n{'='*70}")
    print("COMPARATIVE RESILIENCE ANALYSIS")
    print(f"{'='*70}")
    
    for scenario_name, scenario_key in [("1-Service Failure (25% Capacity Loss)", "1service"),
                                         ("2-Services Failure (50% Capacity Loss)", "2services")]:
        print(f"\n{scenario_name}:")
        print(f"{'Strategy':<15} {'Perf Drop':<15} {'Error Increase':<15} {'Resilience':<15}")
        print("-" * 70)

        for strategy in sorted(strategies):
            baseline_key = (strategy, 'baseline')
            failure_key = (strategy, scenario_key)

            if baseline_key not in results or failure_key not in results:
                continue

            baseline = results[baseline_key]
            failure = results[failure_key]

            baseline_rps = statistics.mean([m['rps'] for m in baseline])
            failure_rps = statistics.mean([m['rps'] for m in failure])

            baseline_sr = sum([m['success'] for m in baseline]) / max(sum([m['total'] for m in baseline]), 1) * 100
            failure_sr = sum([m['success'] for m in failure]) / max(sum([m['total'] for m in failure]), 1) * 100

            perf_drop = (baseline_rps - failure_rps) / baseline_rps * 100 if baseline_rps > 0 else 0
            error_increase = baseline_sr - failure_sr
            resilience = (abs(perf_drop) + abs(error_increase)) / 2

            print(f"{strategy:<15} {perf_drop:>6.1f}% ↓{'':<6} {error_increase:>6.2f}pp ↑{'':<6} {resilience:>6.2f}")

    # Key Insights
    print(f"\n{'='*70}")
    print("KEY INSIGHTS FOR PAPER")
    print(f"{'='*70}")
    print("""
1. GRACEFUL DEGRADATION:
   Which strategy shows the least performance drop under failures?

2. ADAPTATION SPEED:
   How fast does each strategy redistribute load?
   → Least Connection: Automatic (< 1s)
   → Round Robin: No adaptation (static)
   → Weighted: Depends on configuration

3. ERROR PATTERN:
   How do errors increase with capacity loss?

4. RECOVERY BEHAVIOR:
   How does performance recover when services restart?

Add these findings to Article Section 4.4 (Fault Tolerance)
""")
    
    print("\n✅ Analysis complete!")
    print()

if __name__ == '__main__':
    analyze_failure_scenarios()
