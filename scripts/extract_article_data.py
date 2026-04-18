#!/usr/bin/env python3
"""
Extract all real data needed for the article tables.
Produces exact numbers for Tables 4-16 in the article.
"""

import json
import glob
import os
import statistics
import math

def extract_metrics(json_file):
    """Extract key metrics from Artillery JSON output"""
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
    error_rate = 100.0 - success_rate

    first_ts = aggregate.get('firstCounterAt', 0)
    last_ts = aggregate.get('lastCounterAt', 0)
    duration_s = (last_ts - first_ts) / 1000 if (last_ts - first_ts) > 0 else 1
    actual_rps = total_requests / duration_s

    return {
        'requests': total_requests,
        'success': success_200,
        'failures': failed,
        'success_rate': success_rate,
        'error_rate': error_rate,
        'error_count': total_requests - success_200,
        'min_latency': response_time.get('min', 0),
        'max_latency': response_time.get('max', 0),
        'mean_latency': response_time.get('mean', 0),
        'median_latency': response_time.get('median', 0),
        'p95_latency': response_time.get('p95', 0),
        'p99_latency': response_time.get('p99', 0),
        'rps': actual_rps,
        'duration_s': duration_s,
    }

def parse_perf_filename(filename):
    basename = os.path.basename(filename).replace('.json', '')
    parts = basename.split('-')
    if parts[0] == 'round':
        return 'round-robin', parts[2], parts[3].replace('run', '')
    elif parts[0] == 'least':
        return 'least-conn', parts[2], parts[3].replace('run', '')
    elif parts[0] == 'weighted':
        return 'weighted', parts[1], parts[2].replace('run', '')
    return parts[0], parts[1], parts[-1].replace('run', '')

def parse_failure_filename(filename):
    basename = os.path.basename(filename).replace('.json', '')
    parts = basename.split('-')
    if parts[0] == 'round':
        strategy = 'round-robin'
        rest = '-'.join(parts[2:])
    elif parts[0] == 'least':
        strategy = 'least-conn'
        rest = '-'.join(parts[2:])
    elif parts[0] == 'weighted':
        strategy = 'weighted'
        rest = '-'.join(parts[1:])
    else:
        strategy = parts[0]
        rest = '-'.join(parts[1:])

    # Extract scenario and run
    for scenario in ['baseline', '1service', '2services', 'highweight', 'recovery']:
        if rest.startswith(scenario):
            run = rest.replace(scenario + '-', '').replace('run', '')
            return strategy, scenario, run
    return strategy, rest, '1'

def mean_std(values):
    m = statistics.mean(values)
    s = statistics.stdev(values) if len(values) > 1 else 0
    return m, s

def main():
    # ========== PERFORMANCE TESTS ==========
    print("=" * 80)
    print("PERFORMANCE TEST DATA FOR ARTICLE")
    print("=" * 80)

    perf_dir = 'data/performance_tests'
    perf_files = glob.glob(os.path.join(perf_dir, '*.json'))

    perf_results = {}
    for f in sorted(perf_files):
        strategy, load, run = parse_perf_filename(f)
        metrics = extract_metrics(f)
        key = (strategy, load)
        if key not in perf_results:
            perf_results[key] = []
        perf_results[key].append(metrics)

    # Table 4: Response Time Comparison
    print("\n" + "=" * 80)
    print("TABLE 4: Response Time Comparison (ms)")
    print("=" * 80)
    strategy_names = {'round-robin': 'Round Robin', 'least-conn': 'Least Connection', 'weighted': 'Weighted RR'}
    load_order = ['low', 'medium', 'high']
    strategy_order = ['round-robin', 'least-conn', 'weighted']

    print(f"{'Strategy':<20} {'Load':<10} {'Median ± SD':<18} {'P95 ± SD':<18} {'P99 ± SD':<18}")
    print("-" * 84)

    for strategy in strategy_order:
        for load in load_order:
            key = (strategy, load)
            if key not in perf_results:
                continue
            runs = perf_results[key]
            med_m, med_s = mean_std([r['median_latency'] for r in runs])
            p95_m, p95_s = mean_std([r['p95_latency'] for r in runs])
            p99_m, p99_s = mean_std([r['p99_latency'] for r in runs])
            print(f"{strategy_names[strategy]:<20} {load.capitalize():<10} {med_m:.1f} ± {med_s:.1f}     {p95_m:.1f} ± {p95_s:.1f}     {p99_m:.1f} ± {p99_s:.1f}")

    # Table 5: Throughput Comparison
    print("\n" + "=" * 80)
    print("TABLE 5: Throughput Comparison (RPS)")
    print("=" * 80)
    print(f"{'Strategy':<20} {'Load':<10} {'Mean RPS ± SD':<18} {'Max RPS':<12} {'Min RPS':<12}")
    print("-" * 72)

    for strategy in strategy_order:
        for load in load_order:
            key = (strategy, load)
            if key not in perf_results:
                continue
            runs = perf_results[key]
            rps_values = [r['rps'] for r in runs]
            rps_m, rps_s = mean_std(rps_values)
            print(f"{strategy_names[strategy]:<20} {load.capitalize():<10} {rps_m:.1f} ± {rps_s:.1f}       {max(rps_values):.1f}       {min(rps_values):.1f}")

    # Table 6: Success Rate Comparison
    print("\n" + "=" * 80)
    print("TABLE 6: Success Rate / Reliability Comparison")
    print("=" * 80)
    print(f"{'Strategy':<20} {'Load':<10} {'Success Rate':<15} {'Avg Errors':<15} {'Error Rate':<12}")
    print("-" * 72)

    for strategy in strategy_order:
        for load in load_order:
            key = (strategy, load)
            if key not in perf_results:
                continue
            runs = perf_results[key]
            sr_m = statistics.mean([r['success_rate'] for r in runs])
            err_avg = statistics.mean([r['error_count'] for r in runs])
            er_m = statistics.mean([r['error_rate'] for r in runs])
            print(f"{strategy_names[strategy]:<20} {load.capitalize():<10} {sr_m:.4f}%       {err_avg:.1f}           {er_m:.4f}%")

    # High load comparisons
    print("\n" + "=" * 80)
    print("HIGH LOAD DETAILED COMPARISON (for article text)")
    print("=" * 80)

    rr_high = perf_results.get(('round-robin', 'high'), [])
    lc_high = perf_results.get(('least-conn', 'high'), [])
    wr_high = perf_results.get(('weighted', 'high'), [])

    if rr_high and lc_high and wr_high:
        rr_med = statistics.mean([r['median_latency'] for r in rr_high])
        lc_med = statistics.mean([r['median_latency'] for r in lc_high])
        wr_med = statistics.mean([r['median_latency'] for r in wr_high])

        rr_p99 = statistics.mean([r['p99_latency'] for r in rr_high])
        lc_p99 = statistics.mean([r['p99_latency'] for r in lc_high])
        wr_p99 = statistics.mean([r['p99_latency'] for r in wr_high])

        rr_rps = statistics.mean([r['rps'] for r in rr_high])
        lc_rps = statistics.mean([r['rps'] for r in lc_high])
        wr_rps = statistics.mean([r['rps'] for r in wr_high])

        print(f"\nMedian RT: RR={rr_med:.1f}, LC={lc_med:.1f}, WRR={wr_med:.1f}")
        print(f"LC vs RR median diff: {((rr_med - lc_med) / rr_med * 100):.1f}% lower")
        print(f"WRR vs RR median diff: {((rr_med - wr_med) / rr_med * 100):.1f}% lower")
        print(f"LC vs WRR median diff: {((wr_med - lc_med) / wr_med * 100):.1f}% lower")

        print(f"\nP99 RT: RR={rr_p99:.1f}, LC={lc_p99:.1f}, WRR={wr_p99:.1f}")
        print(f"LC vs RR P99 diff: {((rr_p99 - lc_p99) / rr_p99 * 100):.1f}% lower")

        print(f"\nRPS: RR={rr_rps:.1f}, LC={lc_rps:.1f}, WRR={wr_rps:.1f}")

    # Low load comparison
    print("\n" + "=" * 80)
    print("LOW LOAD COMPARISON")
    print("=" * 80)
    rr_low = perf_results.get(('round-robin', 'low'), [])
    lc_low = perf_results.get(('least-conn', 'low'), [])
    wr_low = perf_results.get(('weighted', 'low'), [])
    if rr_low and lc_low and wr_low:
        rr_med = statistics.mean([r['median_latency'] for r in rr_low])
        lc_med = statistics.mean([r['median_latency'] for r in lc_low])
        wr_med = statistics.mean([r['median_latency'] for r in wr_low])
        print(f"Median RT: RR={rr_med:.1f}, LC={lc_med:.1f}, WRR={wr_med:.1f}")
        print(f"Max diff: {max(rr_med, lc_med, wr_med) - min(rr_med, lc_med, wr_med):.1f} ms")

    # Medium load comparison
    print("\n" + "=" * 80)
    print("MEDIUM LOAD COMPARISON")
    print("=" * 80)
    rr_med_load = perf_results.get(('round-robin', 'medium'), [])
    lc_med_load = perf_results.get(('least-conn', 'medium'), [])
    wr_med_load = perf_results.get(('weighted', 'medium'), [])
    if rr_med_load and lc_med_load and wr_med_load:
        rr_m = statistics.mean([r['median_latency'] for r in rr_med_load])
        lc_m = statistics.mean([r['median_latency'] for r in lc_med_load])
        wr_m = statistics.mean([r['median_latency'] for r in wr_med_load])
        print(f"Median RT: RR={rr_m:.1f}, LC={lc_m:.1f}, WRR={wr_m:.1f}")
        print(f"LC vs RR diff: {((rr_m - lc_m) / rr_m * 100):.1f}%")

    # ========== FAILURE TESTS ==========
    print("\n\n" + "=" * 80)
    print("FAILURE TEST DATA FOR ARTICLE")
    print("=" * 80)

    fail_dir = 'data/failure_tests'
    fail_files = glob.glob(os.path.join(fail_dir, '*.json'))

    fail_results = {}
    for f in sorted(fail_files):
        strategy, scenario, run = parse_failure_filename(f)
        metrics = extract_metrics(f)
        key = (strategy, scenario)
        if key not in fail_results:
            fail_results[key] = []
        fail_results[key].append(metrics)

    # Print all failure scenarios
    print("\n" + "=" * 80)
    print("TABLE 12: Performance Under Single Service Failure (25% Capacity Loss)")
    print("=" * 80)
    print(f"{'Strategy':<20} {'Baseline RPS':<15} {'Failure RPS':<15} {'Degrad %':<12} {'BL Success%':<15} {'Fail Success%':<15} {'Error Incr':<12}")
    print("-" * 104)

    for strategy in strategy_order:
        bl_key = (strategy, 'baseline')
        f1_key = (strategy, '1service')
        if bl_key in fail_results and f1_key in fail_results:
            bl = fail_results[bl_key]
            f1 = fail_results[f1_key]
            bl_rps = statistics.mean([r['rps'] for r in bl])
            f1_rps = statistics.mean([r['rps'] for r in f1])
            bl_sr = statistics.mean([r['success_rate'] for r in bl])
            f1_sr = statistics.mean([r['success_rate'] for r in f1])
            degrad = (bl_rps - f1_rps) / bl_rps * 100 if bl_rps > 0 else 0
            err_incr = bl_sr - f1_sr
            print(f"{strategy_names[strategy]:<20} {bl_rps:.1f}         {f1_rps:.1f}         {degrad:.1f}%        {bl_sr:.4f}%       {f1_sr:.4f}%       {err_incr:+.4f}pp")

    print("\n" + "=" * 80)
    print("TABLE 12 DETAIL: Response Time Under Single Service Failure")
    print("=" * 80)
    print(f"{'Strategy':<20} {'BL Median':<12} {'Fail Median':<12} {'BL P95':<10} {'Fail P95':<10} {'BL P99':<10} {'Fail P99':<10} {'BL Mean':<10} {'Fail Mean':<10}")
    print("-" * 106)

    for strategy in strategy_order:
        bl_key = (strategy, 'baseline')
        f1_key = (strategy, '1service')
        if bl_key in fail_results and f1_key in fail_results:
            bl = fail_results[bl_key]
            f1 = fail_results[f1_key]
            bl_med = statistics.mean([r['median_latency'] for r in bl])
            f1_med = statistics.mean([r['median_latency'] for r in f1])
            bl_p95 = statistics.mean([r['p95_latency'] for r in bl])
            f1_p95 = statistics.mean([r['p95_latency'] for r in f1])
            bl_p99 = statistics.mean([r['p99_latency'] for r in bl])
            f1_p99 = statistics.mean([r['p99_latency'] for r in f1])
            bl_mean = statistics.mean([r['mean_latency'] for r in bl])
            f1_mean = statistics.mean([r['mean_latency'] for r in f1])
            print(f"{strategy_names[strategy]:<20} {bl_med:.1f}      {f1_med:.1f}      {bl_p95:.1f}    {f1_p95:.1f}    {bl_p99:.1f}    {f1_p99:.1f}    {bl_mean:.1f}    {f1_mean:.1f}")

    print("\n" + "=" * 80)
    print("TABLE 13: Performance Under Dual Service Failure (50% Capacity Loss)")
    print("=" * 80)
    print(f"{'Strategy':<20} {'Baseline RPS':<15} {'Failure RPS':<15} {'Degrad %':<12} {'BL Success%':<15} {'Fail Success%':<15} {'Error Incr':<12}")
    print("-" * 104)

    for strategy in strategy_order:
        bl_key = (strategy, 'baseline')
        f2_key = (strategy, '2services')
        if bl_key in fail_results and f2_key in fail_results:
            bl = fail_results[bl_key]
            f2 = fail_results[f2_key]
            bl_rps = statistics.mean([r['rps'] for r in bl])
            f2_rps = statistics.mean([r['rps'] for r in f2])
            bl_sr = statistics.mean([r['success_rate'] for r in bl])
            f2_sr = statistics.mean([r['success_rate'] for r in f2])
            degrad = (bl_rps - f2_rps) / bl_rps * 100 if bl_rps > 0 else 0
            err_incr = bl_sr - f2_sr
            print(f"{strategy_names[strategy]:<20} {bl_rps:.1f}         {f2_rps:.1f}         {degrad:.1f}%        {bl_sr:.4f}%       {f2_sr:.4f}%       {err_incr:+.4f}pp")

    print("\n" + "=" * 80)
    print("TABLE 13 DETAIL: Response Time Under Dual Service Failure")
    print("=" * 80)
    print(f"{'Strategy':<20} {'BL Median':<12} {'Fail Median':<12} {'BL P95':<10} {'Fail P95':<10} {'BL P99':<10} {'Fail P99':<10} {'BL Mean':<10} {'Fail Mean':<10}")
    print("-" * 106)

    for strategy in strategy_order:
        bl_key = (strategy, 'baseline')
        f2_key = (strategy, '2services')
        if bl_key in fail_results and f2_key in fail_results:
            bl = fail_results[bl_key]
            f2 = fail_results[f2_key]
            bl_med = statistics.mean([r['median_latency'] for r in bl])
            f2_med = statistics.mean([r['median_latency'] for r in f2])
            bl_p95 = statistics.mean([r['p95_latency'] for r in bl])
            f2_p95 = statistics.mean([r['p95_latency'] for r in f2])
            bl_p99 = statistics.mean([r['p99_latency'] for r in bl])
            f2_p99 = statistics.mean([r['p99_latency'] for r in f2])
            bl_mean = statistics.mean([r['mean_latency'] for r in bl])
            f2_mean = statistics.mean([r['mean_latency'] for r in f2])
            print(f"{strategy_names[strategy]:<20} {bl_med:.1f}      {f2_med:.1f}      {bl_p95:.1f}    {f2_p95:.1f}    {bl_p99:.1f}    {f2_p99:.1f}    {bl_mean:.1f}    {f2_mean:.1f}")

    # High-weight failure (weighted only)
    hw_key = ('weighted', 'highweight')
    if hw_key in fail_results:
        print("\n" + "=" * 80)
        print("TABLE 14: Weighted Strategy Under High-Weight Failure")
        print("=" * 80)
        bl = fail_results[('weighted', 'baseline')]
        hw = fail_results[hw_key]
        bl_rps = statistics.mean([r['rps'] for r in bl])
        hw_rps = statistics.mean([r['rps'] for r in hw])
        bl_sr = statistics.mean([r['success_rate'] for r in bl])
        hw_sr = statistics.mean([r['success_rate'] for r in hw])
        hw_degrad = (bl_rps - hw_rps) / bl_rps * 100 if bl_rps > 0 else 0
        hw_err = bl_sr - hw_sr

        # Also get 1service for comparison
        f1 = fail_results[('weighted', '1service')]
        f1_rps = statistics.mean([r['rps'] for r in f1])
        f1_sr = statistics.mean([r['success_rate'] for r in f1])
        f1_degrad = (bl_rps - f1_rps) / bl_rps * 100 if bl_rps > 0 else 0
        f1_err = bl_sr - f1_sr

        print(f"Normal failure (1 service):   RPS={f1_rps:.1f}, Degrad={f1_degrad:.1f}%, Error Incr={f1_err:+.4f}pp")
        print(f"High-weight failure (svc-1):  RPS={hw_rps:.1f}, Degrad={hw_degrad:.1f}%, Error Incr={hw_err:+.4f}pp")

        # Response times
        hw_med = statistics.mean([r['median_latency'] for r in hw])
        hw_p95 = statistics.mean([r['p95_latency'] for r in hw])
        hw_p99 = statistics.mean([r['p99_latency'] for r in hw])
        hw_mean_rt = statistics.mean([r['mean_latency'] for r in hw])
        print(f"High-weight RT: median={hw_med:.1f}, p95={hw_p95:.1f}, p99={hw_p99:.1f}, mean={hw_mean_rt:.1f}")

    # Recovery
    print("\n" + "=" * 80)
    print("TABLE 15: Recovery Behavior")
    print("=" * 80)
    for strategy in strategy_order:
        rec_key = (strategy, 'recovery')
        bl_key = (strategy, 'baseline')
        if rec_key in fail_results and bl_key in fail_results:
            bl = fail_results[bl_key]
            rec = fail_results[rec_key]
            bl_rps = statistics.mean([r['rps'] for r in bl])
            rec_rps = statistics.mean([r['rps'] for r in rec])
            bl_med = statistics.mean([r['median_latency'] for r in bl])
            rec_med = statistics.mean([r['median_latency'] for r in rec])
            bl_sr = statistics.mean([r['success_rate'] for r in bl])
            rec_sr = statistics.mean([r['success_rate'] for r in rec])
            print(f"{strategy_names[strategy]:<20} BL_RPS={bl_rps:.1f} REC_RPS={rec_rps:.1f}  BL_Med={bl_med:.1f} REC_Med={rec_med:.1f}  BL_SR={bl_sr:.4f}% REC_SR={rec_sr:.4f}%")

    # Print all individual runs for failure tests
    print("\n" + "=" * 80)
    print("ALL FAILURE TEST INDIVIDUAL RUNS")
    print("=" * 80)
    for key in sorted(fail_results.keys()):
        strategy, scenario = key
        runs = fail_results[key]
        print(f"\n{strategy} - {scenario} ({len(runs)} runs):")
        for i, r in enumerate(runs):
            print(f"  Run {i+1}: RPS={r['rps']:.1f}, Median={r['median_latency']:.1f}, P95={r['p95_latency']:.1f}, P99={r['p99_latency']:.1f}, Mean={r['mean_latency']:.1f}, Success={r['success_rate']:.4f}%, Errors={r['error_count']}")

    # Total requests info
    print("\n" + "=" * 80)
    print("TOTAL REQUESTS PER TEST")
    print("=" * 80)
    for key in sorted(perf_results.keys()):
        strategy, load = key
        runs = perf_results[key]
        for i, r in enumerate(runs):
            print(f"{strategy} {load} run{i+1}: {r['requests']} requests, duration={r['duration_s']:.0f}s")

if __name__ == '__main__':
    main()

