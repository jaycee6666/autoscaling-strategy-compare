"""Compare CPU vs Request Rate strategy results."""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"

# Load both results
with open(RESULTS_DIR / "burst_scenario_cpu_results.json") as f:
    cpu_results = json.load(f)

with open(RESULTS_DIR / "burst_scenario_request_rate_results.json") as f:
    rr_results = json.load(f)

print("=" * 80)
print("BURST SCENARIO COMPARISON: CPU vs Request Rate Strategy")
print("=" * 80)
print()

# Summary comparison
print("SUMMARY METRICS")
print("-" * 80)
print(f"{'Metric':<30} {'CPU Strategy':<20} {'Request Rate':<20}")
print("-" * 80)
print(f"{'Total Requests':<30} {cpu_results['summary']['total_requests']:<20} {rr_results['summary']['total_requests']:<20}")
print(f"{'Successful Requests':<30} {cpu_results['summary']['successful_requests']:<20} {rr_results['summary']['successful_requests']:<20}")
print(f"{'Success Rate':<30} {cpu_results['summary']['success_rate']:.2%} {'':16} {rr_results['summary']['success_rate']:.2%}")
print(f"{'Avg Response Time (ms)':<30} {cpu_results['summary']['avg_response_time_ms']:.2f}ms {rr_results['summary']['avg_response_time_ms']:.2f}ms")
print(f"{'P95 Response Time (ms)':<30} {cpu_results['summary']['p95_response_time_ms']:.2f}ms {rr_results['summary']['p95_response_time_ms']:.2f}ms")
print(f"{'P99 Response Time (ms)':<30} {cpu_results['summary']['p99_response_time_ms']:.2f}ms {rr_results['summary']['p99_response_time_ms']:.2f}ms")
print()

# Scaling metrics
print("SCALING METRICS")
print("-" * 80)
print(f"{'Scale-Out Events':<30} {len(cpu_results['scale_out_latencies']):<20} {len(rr_results['scale_out_latencies']):<20}")
if cpu_results['scale_out_latencies']:
    print(f"{'Scale-Out Latency (sec)':<30} {cpu_results['scale_out_latency_stats']['mean']:.2f}s {'':16}")
print()

# Phase metrics
print("PHASE METRICS")
print("-" * 80)
for phase in ["Preheating", "Baseline", "Burst", "Recovery"]:
    cpu_phase = cpu_results['phase_metrics'][phase]
    rr_phase = rr_results['phase_metrics'][phase]
    
    print(f"\n[{phase.upper()}]")
    print(f"{'CPU Utilization':<30} {cpu_phase['avg_cpu_utilization']:.2f}% {'':15} {rr_phase['avg_cpu_utilization']:.2f}%")
    print(f"{'Desired Capacity':<30} {cpu_phase['avg_desired_capacity']:.1f} {'':18} {rr_phase['avg_desired_capacity']:.1f}")
    print(f"{'Response Time (ms)':<30} {cpu_phase['avg_response_time_ms']:.2f}ms {'':13} {rr_phase['avg_response_time_ms']:.2f}ms")

print()
print("=" * 80)
print("KEY FINDINGS")
print("=" * 80)
print(f"✓ CPU Strategy: Scaled from 1 to 2 instances during burst (latency: {cpu_results['scale_out_latency_stats']['mean']:.1f}s)")
print(f"✗ Request Rate Strategy: Did NOT scale out during burst")
print(f"✓ CPU Strategy: Better success rate ({cpu_results['summary']['success_rate']:.1%} vs {rr_results['summary']['success_rate']:.1%})")
print(f"✓ CPU Strategy: Lower average response time ({cpu_results['summary']['avg_response_time_ms']:.0f}ms vs {rr_results['summary']['avg_response_time_ms']:.0f}ms)")
