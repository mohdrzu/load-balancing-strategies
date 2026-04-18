#!/usr/bin/env python3
"""
Generate Publication-Quality Figures for Research Paper
Creates all required graphs for SINTA 2 journal article

Data is automatically extracted from actual experiment results in data/performance_tests/
"""

import json
import glob
import os
import statistics
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style for publication quality
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'

# Create output directory
output_dir = Path('figures')
output_dir.mkdir(exist_ok=True)

# Shared label bbox styles to avoid overlap
_label_bbox = dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='none')
_dark_bbox = dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.55)


def load_real_data(data_dir='data/performance_tests'):
    """
    Automatically load and aggregate real experiment data from Artillery JSON files.
    Returns a structured dict ready for figure generation.
    """
    results = {}

    json_files = sorted(glob.glob(os.path.join(data_dir, '*.json')))
    if not json_files:
        print(f"[ERROR] No JSON files found in {data_dir}/")
        print("Please run the performance tests first.")
        exit(1)

    print(f"[OK] Loading {len(json_files)} result files from {data_dir}/")

    for f in json_files:
        with open(f) as fh:
            d = json.load(fh)

        agg = d['aggregate']
        counters = agg['counters']
        summaries = agg['summaries']['http.response_time']

        name = os.path.basename(f).replace('.json', '')
        parts = name.split('-')

        if parts[0] == 'round':
            strategy = 'Round Robin'
            load_level = parts[2]
        elif parts[0] == 'least':
            strategy = 'Least Connection'
            load_level = parts[2]
        elif parts[0] == 'weighted':
            strategy = 'Weighted RR'
            load_level = parts[1]
        else:
            continue

        # Calculate actual throughput
        first_ts = agg['firstCounterAt']
        last_ts = agg['lastCounterAt']
        duration_s = (last_ts - first_ts) / 1000
        total_req = counters.get('http.requests', 0)
        actual_rps = total_req / duration_s if duration_s > 0 else 0

        success_200 = counters.get('http.codes.200', 0)
        success_rate = (success_200 / total_req * 100) if total_req > 0 else 0

        key = (strategy, load_level)
        if key not in results:
            results[key] = []

        results[key].append({
            'median': summaries['median'],
            'mean': summaries['mean'],
            'p95': summaries['p95'],
            'p99': summaries['p99'],
            'min': summaries['min'],
            'max': summaries['max'],
            'rps': actual_rps,
            'total_requests': total_req,
            'success_rate': success_rate,
        })

    # Aggregate into the format needed for figures
    strategies = ['Round Robin', 'Least Connection', 'Weighted RR']
    load_map = {'low': 'low_load', 'medium': 'medium_load', 'high': 'high_load'}

    data = {'strategies': strategies}

    for load_key, data_key in load_map.items():
        medians, stds, p95s, p95_stds, p99s, p99_stds = [], [], [], [], [], []
        rpss, rps_stds, success_rates = [], [], []

        for strategy in strategies:
            runs = results.get((strategy, load_key), [])
            if runs:
                m = [r['median'] for r in runs]
                p95 = [r['p95'] for r in runs]
                p99 = [r['p99'] for r in runs]
                rps = [r['rps'] for r in runs]
                sr = [r['success_rate'] for r in runs]

                medians.append(statistics.mean(m))
                stds.append(statistics.stdev(m) if len(m) > 1 else 0)
                p95s.append(statistics.mean(p95))
                p95_stds.append(statistics.stdev(p95) if len(p95) > 1 else 0)
                p99s.append(statistics.mean(p99))
                p99_stds.append(statistics.stdev(p99) if len(p99) > 1 else 0)
                rpss.append(statistics.mean(rps))
                rps_stds.append(statistics.stdev(rps) if len(rps) > 1 else 0)
                success_rates.append(statistics.mean(sr))
            else:
                medians.append(0)
                stds.append(0)
                p95s.append(0)
                p95_stds.append(0)
                p99s.append(0)
                p99_stds.append(0)
                rpss.append(0)
                rps_stds.append(0)
                success_rates.append(0)

        data[data_key] = {
            'median': medians,
            'std': stds,
            'p95': p95s,
            'p95_std': p95_stds,
            'p99': p99s,
            'p99_std': p99_stds,
            'rps': rpss,
            'rps_std': rps_stds,
            'success_rate': success_rates,
        }

    return data


# Load real experiment data
data = load_real_data()


def figure1_response_time_comparison():
    """
    Figure 1: Median Response Time Comparison Across Load Levels
    Grouped bar chart with error bars
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    strategies = data['strategies']
    x = np.arange(len(strategies))
    width = 0.25

    low = data['low_load']['median']
    low_std = data['low_load']['std']
    medium = data['medium_load']['median']
    medium_std = data['medium_load']['std']
    high = data['high_load']['median']
    high_std = data['high_load']['std']

    bars1 = ax.bar(x - width, low, width, yerr=low_std,
                   label='Low Load (100 users)', capsize=5,
                   color='#3498db', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x, medium, width, yerr=medium_std,
                   label='Medium Load (500 users)', capsize=5,
                   color='#e74c3c', edgecolor='black', linewidth=0.5)
    bars3 = ax.bar(x + width, high, width, yerr=high_std,
                   label='High Load (1000 users)', capsize=5,
                   color='#2ecc71', edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Strategi Load Balancing', fontsize=12, fontweight='bold')
    ax.set_ylabel('Median Response Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Perbandingan Median Response Time pada Berbagai Tingkat Beban',
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.legend(loc='upper left', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Adjust y-axis — leave room for error bars at top
    all_vals = low + medium + high
    all_stds = low_std + medium_std + high_std
    y_min = min(all_vals) - 15
    y_max = max(v + s for v, s in zip(all_vals, all_stds)) + 12
    ax.set_ylim([max(0, y_min), y_max])

    # Place value labels INSIDE bars so they never collide with error bars
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height - 3,
                    f'{height:.1f}',
                    ha='center', va='top', fontsize=7, fontweight='bold',
                    color='white', bbox=_dark_bbox)

    autolabel(bars1)
    autolabel(bars2)
    autolabel(bars3)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_response_time.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'figure1_response_time.pdf', bbox_inches='tight')
    print("✅ Figure 1 created: Median Response Time Comparison")
    plt.close()


def figure2_tail_latency_high_load():
    """
    Figure 2: P95 and P99 Tail Latency at High Load
    Grouped bar chart — this is where real differences appear
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    strategies = data['strategies']
    x = np.arange(len(strategies))
    width = 0.3

    p95 = data['high_load']['p95']
    p95_std = data['high_load']['p95_std']
    p99 = data['high_load']['p99']
    p99_std = data['high_load']['p99_std']

    bars1 = ax.bar(x - width / 2, p95, width, yerr=p95_std,
                   label='P95 Latency', capsize=5,
                   color='#f39c12', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width / 2, p99, width, yerr=p99_std,
                   label='P99 Latency', capsize=5,
                   color='#e74c3c', edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Strategi Load Balancing', fontsize=12, fontweight='bold')
    ax.set_ylabel('Response Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Perbandingan Tail Latency (P95 & P99) pada High Load',
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.legend(loc='upper right', frameon=True, shadow=True, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Place labels ABOVE the error-bar caps (height + std + gap)
    def autolabel(bars, stds):
        for bar, sd in zip(bars, stds):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + sd + 10,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=8, fontweight='bold',
                    bbox=_label_bbox)

    autolabel(bars1, p95_std)
    autolabel(bars2, p99_std)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_tail_latency_high.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'figure2_tail_latency_high.pdf', bbox_inches='tight')
    print("✅ Figure 2 created: Tail Latency at High Load (P95 & P99)")
    plt.close()


def figure3_p99_across_loads():
    """
    Figure 3: P99 Latency Trends Across All Load Levels
    Line chart with error bars — shows how differences emerge at high load
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    load_levels = ['Low\n(100 users)', 'Medium\n(500 users)', 'High\n(1000 users)']
    x_pos = np.arange(len(load_levels))

    rr_p99 = [data['low_load']['p99'][0],
              data['medium_load']['p99'][0],
              data['high_load']['p99'][0]]
    lc_p99 = [data['low_load']['p99'][1],
              data['medium_load']['p99'][1],
              data['high_load']['p99'][1]]
    wrr_p99 = [data['low_load']['p99'][2],
               data['medium_load']['p99'][2],
               data['high_load']['p99'][2]]

    rr_std = [data['low_load']['p99_std'][0],
              data['medium_load']['p99_std'][0],
              data['high_load']['p99_std'][0]]
    lc_std = [data['low_load']['p99_std'][1],
              data['medium_load']['p99_std'][1],
              data['high_load']['p99_std'][1]]
    wrr_std = [data['low_load']['p99_std'][2],
               data['medium_load']['p99_std'][2],
               data['high_load']['p99_std'][2]]

    ax.errorbar(x_pos, rr_p99, yerr=rr_std, marker='o', linewidth=2.5, markersize=10,
                label='Round Robin', color='#3498db', capsize=5)
    ax.errorbar(x_pos, lc_p99, yerr=lc_std, marker='s', linewidth=2.5, markersize=10,
                label='Least Connection', color='#e74c3c', capsize=5)
    ax.errorbar(x_pos, wrr_p99, yerr=wrr_std, marker='^', linewidth=2.5, markersize=10,
                label='Weighted RR', color='#2ecc71', capsize=5)

    ax.set_xlabel('Tingkat Beban', fontsize=12, fontweight='bold')
    ax.set_ylabel('P99 Response Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Tren P99 Latency pada Berbagai Tingkat Beban',
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(load_levels)
    ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')

    # Smart value labels — stagger vertically when points are close together
    for i, (rr, lc, wrr) in enumerate(zip(rr_p99, lc_p99, wrr_p99)):
        items = sorted([(rr, '#3498db'), (lc, '#e74c3c'), (wrr, '#2ecc71')],
                       key=lambda t: t[0], reverse=True)
        spread = items[0][0] - items[-1][0]

        if spread < 15:
            # Values too close — stagger: above / at / below
            offsets = [20, 4, -18]
        else:
            offsets = [12, 12, 12]

        for (val, color), off in zip(items, offsets):
            ax.text(i + 0.08, val + off, f'{val:.1f}',
                    fontsize=8, color=color, fontweight='bold',
                    bbox=_label_bbox)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_p99_trend.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'figure3_p99_trend.pdf', bbox_inches='tight')
    print("✅ Figure 3 created: P99 Latency Trends Across Load Levels")
    plt.close()


def figure4_throughput_comparison():
    """
    Figure 4: Throughput (RPS) Comparison
    Shows that all strategies achieve similar throughput — an important finding
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    load_levels = ['Low\n(100 users)', 'Medium\n(500 users)', 'High\n(1000 users)']
    x_pos = np.arange(len(load_levels))

    rr_rps = [data['low_load']['rps'][0],
              data['medium_load']['rps'][0],
              data['high_load']['rps'][0]]
    lc_rps = [data['low_load']['rps'][1],
              data['medium_load']['rps'][1],
              data['high_load']['rps'][1]]
    wrr_rps = [data['low_load']['rps'][2],
               data['medium_load']['rps'][2],
               data['high_load']['rps'][2]]

    ax.plot(x_pos, rr_rps, marker='o', linewidth=2.5, markersize=10,
            label='Round Robin', color='#3498db')
    ax.plot(x_pos, lc_rps, marker='s', linewidth=2.5, markersize=10,
            label='Least Connection', color='#e74c3c')
    ax.plot(x_pos, wrr_rps, marker='^', linewidth=2.5, markersize=10,
            label='Weighted RR', color='#2ecc71')

    ax.set_xlabel('Tingkat Beban', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (Requests per Second)', fontsize=12, fontweight='bold')
    ax.set_title('Perbandingan Throughput pada Berbagai Tingkat Beban',
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(load_levels)
    ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')

    # Smart labels — stagger horizontally + vertically when values overlap
    for i, (rr, lc, wrr) in enumerate(zip(rr_rps, lc_rps, wrr_rps)):
        spread = max(rr, lc, wrr) - min(rr, lc, wrr)
        if spread < 1:
            # Values essentially identical — fan labels out
            ax.text(i - 0.18, rr + 2.5, f'{rr:.1f}', ha='center', fontsize=8,
                    color='#3498db', fontweight='bold', bbox=_label_bbox)
            ax.text(i + 0.18, lc - 5, f'{lc:.1f}', ha='center', fontsize=8,
                    color='#e74c3c', fontweight='bold', bbox=_label_bbox)
            ax.text(i + 0.40, wrr + 2.5, f'{wrr:.1f}', ha='center', fontsize=8,
                    color='#2ecc71', fontweight='bold', bbox=_label_bbox)
        else:
            ax.text(i, rr + 2.5, f'{rr:.1f}', ha='center', fontsize=8,
                    color='#3498db', fontweight='bold', bbox=_label_bbox)
            ax.text(i, lc - 5, f'{lc:.1f}', ha='center', fontsize=8,
                    color='#e74c3c', fontweight='bold', bbox=_label_bbox)
            ax.text(i, wrr + 2.5, f'{wrr:.1f}', ha='center', fontsize=8,
                    color='#2ecc71', fontweight='bold', bbox=_label_bbox)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure4_throughput.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'figure4_throughput.pdf', bbox_inches='tight')
    print("✅ Figure 4 created: Throughput Comparison")
    plt.close()


def figure5_performance_radar():
    """
    Figure 5: Overall Performance Radar Chart (High Load)
    Multi-dimensional comparison using normalized scores from real data
    """
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    categories = ['Response Time\n(Lower=Better)',
                  'Tail Latency P99\n(Lower=Better)',
                  'Consistency\n(Lower SD=Better)',
                  'Throughput\n(Higher=Better)',
                  'Reliability\n(Higher=Better)']
    N = len(categories)

    # High load data: [RR, LC, WRR]
    medians = data['high_load']['median']
    p99s = data['high_load']['p99']
    p99_stds = data['high_load']['p99_std']
    rpss = data['high_load']['rps']
    success = data['high_load']['success_rate']

    def normalize_lower_better(vals):
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx - mn > 0 else 1
        return [60 + 40 * (1 - (v - mn) / rng) for v in vals]

    def normalize_higher_better(vals):
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx - mn > 0 else 1
        return [60 + 40 * ((v - mn) / rng) for v in vals]

    rt_scores = normalize_lower_better(medians)
    p99_scores = normalize_lower_better(p99s)
    consistency_scores = normalize_lower_better(p99_stds)
    throughput_scores = normalize_higher_better(rpss)
    reliability_scores = normalize_higher_better(success)

    rr_scores = [rt_scores[0], p99_scores[0], consistency_scores[0],
                 throughput_scores[0], reliability_scores[0]]
    lc_scores = [rt_scores[1], p99_scores[1], consistency_scores[1],
                 throughput_scores[1], reliability_scores[1]]
    wrr_scores = [rt_scores[2], p99_scores[2], consistency_scores[2],
                  throughput_scores[2], reliability_scores[2]]

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    rr_scores += rr_scores[:1]
    lc_scores += lc_scores[:1]
    wrr_scores += wrr_scores[:1]
    angles += angles[:1]

    ax.plot(angles, rr_scores, 'o-', linewidth=2, label='Round Robin', color='#3498db')
    ax.fill(angles, rr_scores, alpha=0.15, color='#3498db')

    ax.plot(angles, lc_scores, 's-', linewidth=2, label='Least Connection', color='#e74c3c')
    ax.fill(angles, lc_scores, alpha=0.15, color='#e74c3c')

    ax.plot(angles, wrr_scores, '^-', linewidth=2, label='Weighted RR', color='#2ecc71')
    ax.fill(angles, wrr_scores, alpha=0.15, color='#2ecc71')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], size=8)
    ax.set_title('Perbandingan Performa Keseluruhan pada High Load (Radar Chart)',
                 fontsize=13, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=True, shadow=True)
    ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure5_radar.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'figure5_radar.pdf', bbox_inches='tight')
    print("✅ Figure 5 created: Performance Radar Chart (High Load)")
    plt.close()


def figure6_fault_tolerance():
    """
    Figure 6: Fault Tolerance — P99 Latency Under Failure Scenarios
    This is the KEY finding: RR degrades catastrophically, LC and WRR remain stable
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Load failure test data
    fail_dir = 'data/failure_tests'
    fail_files = sorted(glob.glob(os.path.join(fail_dir, '*.json')))

    fail_results = {}
    for f in fail_files:
        with open(f) as fh:
            d = json.load(fh)
        agg = d['aggregate']
        summaries = agg['summaries']['http.response_time']

        name = os.path.basename(f).replace('.json', '')
        parts = name.split('-')
        if parts[0] == 'round':
            strategy = 'Round Robin'
            rest = '-'.join(parts[2:])
        elif parts[0] == 'least':
            strategy = 'Least Connection'
            rest = '-'.join(parts[2:])
        elif parts[0] == 'weighted':
            strategy = 'Weighted RR'
            rest = '-'.join(parts[1:])
        else:
            continue

        for scenario in ['baseline', '1service', '2services']:
            if rest.startswith(scenario):
                key = (strategy, scenario)
                if key not in fail_results:
                    fail_results[key] = []
                fail_results[key].append({
                    'p99': summaries['p99'],
                    'mean': summaries['mean'],
                    'median': summaries['median'],
                })
                break

    strategies = ['Round Robin', 'Least Connection', 'Weighted RR']
    scenarios = ['baseline', '1service', '2services']
    scenario_labels = ['Baseline\n(All Healthy)', 'Single Failure\n(25% Loss)', 'Dual Failure\n(50% Loss)']
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    markers = ['o', 's', '^']

    x_pos = np.arange(len(scenarios))

    for i, strategy in enumerate(strategies):
        p99_vals = []
        for scenario in scenarios:
            runs = fail_results.get((strategy, scenario), [])
            if runs:
                p99_vals.append(statistics.mean([r['p99'] for r in runs]))
            else:
                p99_vals.append(0)

        ax.plot(x_pos, p99_vals, marker=markers[i], linewidth=2.5, markersize=10,
                label=strategy, color=colors[i])

        # Add value labels with smart offsets
        for j, val in enumerate(p99_vals):
            if strategy == 'Round Robin' and j > 0:
                offset_y = 80
            elif strategy == 'Least Connection':
                offset_y = -80
            elif strategy == 'Weighted RR':
                offset_y = 50
            else:
                offset_y = -60
            ax.text(j + 0.05, val + offset_y, f'{val:.0f} ms',
                    fontsize=9, color=colors[i], fontweight='bold',
                    bbox=_label_bbox)

    ax.set_xlabel('Skenario Failure', fontsize=12, fontweight='bold')
    ax.set_ylabel('P99 Response Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('P99 Latency Under Failure Scenarios\n(Temuan Utama: RR Degradasi Katastrofik)',
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(scenario_labels)
    ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')

    # Add annotation for the dramatic spike
    rr_dual = fail_results.get(('Round Robin', '2services'), [])
    if rr_dual:
        rr_dual_p99 = statistics.mean([r['p99'] for r in rr_dual])
        rr_bl = fail_results.get(('Round Robin', 'baseline'), [])
        rr_bl_p99 = statistics.mean([r['p99'] for r in rr_bl]) if rr_bl else 284
        pct = ((rr_dual_p99 - rr_bl_p99) / rr_bl_p99) * 100
        ax.annotate(f'+{pct:.0f}% spike!',
                    xy=(2, rr_dual_p99), xytext=(1.4, rr_dual_p99 + 200),
                    fontsize=11, color='red', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='red', lw=2))

    plt.tight_layout()
    plt.savefig(output_dir / 'figure6_fault_tolerance.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'figure6_fault_tolerance.pdf', bbox_inches='tight')
    print("✅ Figure 6 created: Fault Tolerance P99 Under Failure Scenarios")
    plt.close()


def figure7_fault_tolerance_mean():
    """
    Figure 7: Mean Response Time Under Failure Scenarios
    Complements Figure 6 with mean RT perspective
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    fail_dir = 'data/failure_tests'
    fail_files = sorted(glob.glob(os.path.join(fail_dir, '*.json')))

    fail_results = {}
    for f in fail_files:
        with open(f) as fh:
            d = json.load(fh)
        agg = d['aggregate']
        summaries = agg['summaries']['http.response_time']
        name = os.path.basename(f).replace('.json', '')
        parts = name.split('-')
        if parts[0] == 'round':
            strategy = 'Round Robin'
            rest = '-'.join(parts[2:])
        elif parts[0] == 'least':
            strategy = 'Least Connection'
            rest = '-'.join(parts[2:])
        elif parts[0] == 'weighted':
            strategy = 'Weighted RR'
            rest = '-'.join(parts[1:])
        else:
            continue

        for scenario in ['baseline', '1service', '2services']:
            if rest.startswith(scenario):
                key = (strategy, scenario)
                if key not in fail_results:
                    fail_results[key] = []
                fail_results[key].append({
                    'mean': summaries['mean'],
                })
                break

    strategies = ['Round Robin', 'Least Connection', 'Weighted RR']
    x = np.arange(len(strategies))
    width = 0.25

    baseline_vals = []
    single_vals = []
    dual_vals = []
    for strategy in strategies:
        bl = fail_results.get((strategy, 'baseline'), [])
        s1 = fail_results.get((strategy, '1service'), [])
        s2 = fail_results.get((strategy, '2services'), [])
        baseline_vals.append(statistics.mean([r['mean'] for r in bl]) if bl else 0)
        single_vals.append(statistics.mean([r['mean'] for r in s1]) if s1 else 0)
        dual_vals.append(statistics.mean([r['mean'] for r in s2]) if s2 else 0)

    bars1 = ax.bar(x - width, baseline_vals, width, label='Baseline (All Healthy)',
                   color='#27ae60', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x, single_vals, width, label='Single Failure (25% Loss)',
                   color='#f39c12', edgecolor='black', linewidth=0.5)
    bars3 = ax.bar(x + width, dual_vals, width, label='Dual Failure (50% Loss)',
                   color='#e74c3c', edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Strategi Load Balancing', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Response Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Mean Response Time Under Failure Scenarios',
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height - 3,
                    f'{height:.1f}',
                    ha='center', va='top', fontsize=7, fontweight='bold',
                    color='white', bbox=_dark_bbox)

    autolabel(bars1)
    autolabel(bars2)
    autolabel(bars3)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure7_fault_mean_rt.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'figure7_fault_mean_rt.pdf', bbox_inches='tight')
    print("✅ Figure 7 created: Mean Response Time Under Failure Scenarios")
    plt.close()


def print_data_summary():
    """Print summary of loaded data for verification"""
    print()
    print("[DATA] Summary (from real experiment results):")
    print()
    for load_name, load_key in [('Low', 'low_load'), ('Medium', 'medium_load'), ('High', 'high_load')]:
        print(f"  {load_name} Load:")
        for i, s in enumerate(data['strategies']):
            m = data[load_key]['median'][i]
            sd = data[load_key]['std'][i]
            p95 = data[load_key]['p95'][i]
            p99 = data[load_key]['p99'][i]
            rps = data[load_key]['rps'][i]
            sr = data[load_key]['success_rate'][i]
            print(f"    {s:<18} median={m:.1f}±{sd:.1f}ms  P95={p95:.1f}ms  P99={p99:.1f}ms  RPS={rps:.1f}  SR={sr:.2f}%")
    print()


def create_all_figures():
    """Generate all figures for the paper"""
    print("=" * 60)
    print("Generating Publication-Quality Figures")
    print("=" * 60)

    print_data_summary()

    figure1_response_time_comparison()
    figure2_tail_latency_high_load()
    figure3_p99_across_loads()
    figure4_throughput_comparison()
    figure5_performance_radar()
    figure6_fault_tolerance()
    figure7_fault_tolerance_mean()

    print()
    print("=" * 60)
    print("All figures created successfully!")
    print(f"Output directory: {output_dir.absolute()}")
    print("=" * 60)
    print()
    print("Files created:")
    for file in sorted(output_dir.glob('figure*.png')):
        print(f"  📄 {file.name}")
    print()
    print("Next steps:")
    print("1. Review figures in figures/ directory")
    print("2. Insert figures into your paper (draft-article-original.md)")
    print("3. Add captions and references in text")


if __name__ == '__main__':
    create_all_figures()

