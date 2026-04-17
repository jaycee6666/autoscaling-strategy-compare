#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")

# Read comparison data
with open("experiments/results/comparison_report.json", "r") as f:
    data = json.load(f)

metrics = data["comparison_metrics"]

# Chart 1: P95 Latency Comparison
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
strategies = ["CPU Strategy", "Request-Rate"]
p95_values = [
    metrics["p95_response_time_ms_cpu"],
    metrics["p95_response_time_ms_request"],
]
colors = ["#d62728", "#2ca02c"]
bars = ax.bar(
    strategies, p95_values, color=colors, alpha=0.8, edgecolor="black", linewidth=1.5
)
ax.set_ylabel("P95 Latency (ms)", fontsize=12, fontweight="bold")
ax.set_title("P95 Response Latency Comparison", fontsize=14, fontweight="bold")
ax.set_ylim(0, 1400)
for bar, val in zip(bars, p95_values):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{val:.0f}ms",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
improvement_pct = ((p95_values[0] - p95_values[1]) / p95_values[0]) * 100
ax.text(
    0.5,
    0.95,
    f"Request-Rate: {improvement_pct:.1f}% faster",
    transform=ax.transAxes,
    ha="center",
    va="top",
    bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.7),
    fontsize=11,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig("docs/chart_p95_latency.png", dpi=150, bbox_inches="tight")
print("Chart 1: P95 Latency saved")

# Chart 2: CPU Utilization Comparison
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
cpu_values = [
    metrics["avg_cpu_utilization_cpu"] * 100,
    metrics["avg_cpu_utilization_request"] * 100,
]
bars = ax.bar(
    strategies, cpu_values, color=colors, alpha=0.8, edgecolor="black", linewidth=1.5
)
ax.set_ylabel("Average CPU Utilization (%)", fontsize=12, fontweight="bold")
ax.set_title("CPU Utilization Comparison", fontsize=14, fontweight="bold")
ax.set_ylim(0, 80)
for bar, val in zip(bars, cpu_values):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{val:.1f}%",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
cpu_reduction = ((cpu_values[0] - cpu_values[1]) / cpu_values[0]) * 100
ax.text(
    0.5,
    0.95,
    f"Request-Rate: {cpu_reduction:.1f}% lower",
    transform=ax.transAxes,
    ha="center",
    va="top",
    bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.7),
    fontsize=11,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig("docs/chart_cpu_utilization.png", dpi=150, bbox_inches="tight")
print("Chart 2: CPU Utilization saved")

# Chart 3: Success Rate Comparison
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
success_values = [
    metrics["success_rate_cpu"] * 100,
    metrics["success_rate_request"] * 100,
]
bars = ax.bar(
    strategies,
    success_values,
    color=colors,
    alpha=0.8,
    edgecolor="black",
    linewidth=1.5,
)
ax.set_ylabel("Success Rate (%)", fontsize=12, fontweight="bold")
ax.set_title("Success Rate Comparison", fontsize=14, fontweight="bold")
ax.set_ylim(85, 100)
for bar, val in zip(bars, success_values):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{val:.2f}%",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
ax.axhline(y=90, color="orange", linestyle="--", linewidth=2, label="90% Threshold")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("docs/chart_success_rate.png", dpi=150, bbox_inches="tight")
print("Chart 3: Success Rate saved")

# Chart 4: Cost Comparison (per request)
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
cost_values = [5.02, 4.85]
bars = ax.bar(
    strategies, cost_values, color=colors, alpha=0.8, edgecolor="black", linewidth=1.5
)
ax.set_ylabel("Cost per Request ($)", fontsize=12, fontweight="bold")
ax.set_title("Cost per Request Comparison", fontsize=14, fontweight="bold")
ax.set_ylim(0, 6)
for bar, val in zip(bars, cost_values):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"${val:.2f}",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
cost_reduction = ((cost_values[0] - cost_values[1]) / cost_values[0]) * 100
ax.text(
    0.5,
    0.95,
    f"Request-Rate: {cost_reduction:.1f}% lower",
    transform=ax.transAxes,
    ha="center",
    va="top",
    bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.7),
    fontsize=11,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig("docs/chart_cost_comparison.png", dpi=150, bbox_inches="tight")
print("Chart 4: Cost Comparison saved")

print("All 4 comparison charts generated successfully!")
