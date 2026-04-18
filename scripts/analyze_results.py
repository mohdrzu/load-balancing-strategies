#!/usr/bin/env python3
"""
Artillery Test Results Analyzer
Automatically extracts metrics from JSON files in data/performance_tests/
and generates analysis summary for the research paper.
"""

import json
import glob
import os
from pathlib import Path
import statistics

def parse_filename(filename):
    """Extract strategy, load, and run number from filename"""
    basename = os.path.basename(filename).replace('.json', '')
    parts = basename.split('-')

    if parts[0] == 'round':
        strategy = 'round-robin'
        load = parts[2]
        run = parts[3].replace('run', '')
    elif parts[0] == 'least':
        strategy = 'least-conn'
        load = parts[2]
        run = parts[3].replace('run', '')
    elif parts[0] == 'weighted':
        strategy = 'weighted'
        load = parts[1]
        run = parts[2].replace('run', '')
    else:
        strategy = parts[0]
        load = parts[1]
        run = parts[-1].replace('run', '')

    return strategy, load, run

def extract_metrics(json_file):
    """Extract key metrics from Artillery JSON output"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        aggregate = data.get('aggregate', {})
        counters = aggregate.get('counters', {})
        summaries = aggregate.get('summaries', {})
        response_time = summaries.get('http.response_time', {})

        total_requests = counters.get('http.requests', 0)
        success_200 = counters.get('http.codes.200', 0)
        failed = counters.get('vusers.failed', 0)
        success_rate = (success_200 / total_requests * 100) if total_requests > 0 else 0

        # Calculate actual RPS from timestamps
        first_ts = aggregate.get('firstCounterAt', 0)
        last_ts = aggregate.get('lastCounterAt', 0)
        duration_s = (last_ts - first_ts) / 1000 if (last_ts - first_ts) > 0 else 1
        actual_rps = total_requests / duration_s

        return {
            'requests': total_requests,
            'success': success_200,
            'failures': failed,
            'success_rate': success_rate,
            'min_latency': response_time.get('min', 0),
            'max_latency': response_time.get('max', 0),
            'mean_latency': response_time.get('mean', 0),
            'median_latency': response_time.get('median', 0),
            'p95_latency': response_time.get('p95', 0),
            'p99_latency': response_time.get('p99', 0),
            'rps': actual_rps,
            'duration_s': duration_s,
        }
    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return None

def analyze_results(data_dir='data/performance_tests'):
    """Main analysis function"""
    print("=" * 60)
    print("Artillery Test Results Analysis")
    print("=" * 60)
    print()

    # Find all JSON files
    json_files = glob.glob(os.path.join(data_dir, '*.json'))

    if not json_files:
        print(f"No JSON files found in {data_dir}/")
        return

    print(f"Found {len(json_files)} test result files")
    print()

    # Organize data by strategy and load
    results = {}

    for json_file in sorted(json_files):
        strategy, load, run = parse_filename(json_file)
        metrics = extract_metrics(json_file)

        if metrics:
            key = (strategy, load)
            if key not in results:
                results[key] = []
            results[key].append(metrics)

    # Print summary table
    print("=" * 110)
    print(f"{'Strategy':<15} {'Load':<10} {'Runs':<6} {'Avg Median (ms)':<18} {'Avg P95 (ms)':<16} {'Avg P99 (ms)':<16} {'Avg RPS':<12} {'Success %':<12}")
    print("=" * 110)

    summary_data = []

    for (strategy, load), runs in sorted(results.items()):
        if not runs:
            continue

        avg_median = statistics.mean([r['median_latency'] for r in runs])
        std_median = statistics.stdev([r['median_latency'] for r in runs]) if len(runs) > 1 else 0

        avg_p95 = statistics.mean([r['p95_latency'] for r in runs])
        std_p95 = statistics.stdev([r['p95_latency'] for r in runs]) if len(runs) > 1 else 0

        avg_p99 = statistics.mean([r['p99_latency'] for r in runs])
        std_p99 = statistics.stdev([r['p99_latency'] for r in runs]) if len(runs) > 1 else 0

        avg_rps = statistics.mean([r['rps'] for r in runs])
        std_rps = statistics.stdev([r['rps'] for r in runs]) if len(runs) > 1 else 0

        avg_success = statistics.mean([r['success_rate'] for r in runs])

        print(f"{strategy:<15} {load:<10} {len(runs):<6} "
              f"{avg_median:>6.1f} ± {std_median:<6.1f}   "
              f"{avg_p95:>6.1f} ± {std_p95:<6.1f}  "
              f"{avg_p99:>6.1f} ± {std_p99:<6.1f}  "
              f"{avg_rps:>6.1f} ± {std_rps:<4.1f}  "
              f"{avg_success:>8.4f}%")

        summary_data.append({
            'strategy': strategy,
            'load': load,
            'runs': len(runs),
            'avg_median': avg_median,
            'std_median': std_median,
            'avg_p95': avg_p95,
            'std_p95': std_p95,
            'avg_p99': avg_p99,
            'std_p99': std_p99,
            'avg_rps': avg_rps,
            'std_rps': std_rps,
            'avg_success': avg_success
        })

    print("=" * 110)
    print()

    # Detailed comparison by load level
    load_levels = set([load for _, load in results.keys()])

    for load_level in sorted(load_levels):
        print(f"\n{load_level.upper()} LOAD DETAILED COMPARISON")
        print("-" * 80)

        for (strategy, load), runs in sorted(results.items()):
            if load != load_level or not runs:
                continue

            median_values = [r['median_latency'] for r in runs]
            p95_values = [r['p95_latency'] for r in runs]
            p99_values = [r['p99_latency'] for r in runs]
            rps_values = [r['rps'] for r in runs]

            print(f"\n{strategy.upper()}:")
            print(f"  Median Response Time: {statistics.mean(median_values):.1f} ms "
                  f"(min: {min(median_values):.1f}, max: {max(median_values):.1f})")
            print(f"  P95 Latency: {statistics.mean(p95_values):.1f} ms "
                  f"(min: {min(p95_values):.1f}, max: {max(p95_values):.1f})")
            print(f"  P99 Latency: {statistics.mean(p99_values):.1f} ms "
                  f"(min: {min(p99_values):.1f}, max: {max(p99_values):.1f})")
            print(f"  Throughput: {statistics.mean(rps_values):.1f} req/s "
                  f"(min: {min(rps_values):.1f}, max: {max(rps_values):.1f})")

    print("\n" + "=" * 80)
    print("\n✅ Analysis complete!")
    print()

    # Export to CSV
    try:
        import csv
        output_file = os.path.join(data_dir, 'analysis_summary.csv')

        with open(output_file, 'w', newline='') as f:
            fieldnames = ['strategy', 'load', 'runs', 'avg_median', 'std_median',
                         'avg_p95', 'std_p95', 'avg_p99', 'std_p99',
                         'avg_rps', 'std_rps', 'avg_success']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)

        print(f"📊 Summary exported to: {output_file}")
        print()
    except Exception as e:
        print(f"Could not export CSV: {e}")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = 'data/performance_tests'

    if not os.path.exists(data_dir):
        print(f"❌ Directory {data_dir}/ not found!")
        print("Please run the performance tests first.")
    else:
        analyze_results(data_dir)
