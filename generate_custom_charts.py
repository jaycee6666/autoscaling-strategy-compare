import json
import matplotlib.pyplot as plt
import os
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid", context="paper", font="Times New Roman")

with open("experiments/results_round13_22_median.json", "r") as f:
    full_data = json.load(f)
    data = full_data["median_summary"]
    raw_data = full_data["raw"]

os.makedirs("docs", exist_ok=True)

# 1. Bar Chart: Latency Comparison (Median)
labels = ['Avg Latency', 'P95 Latency', 'P99 Latency']
cpu_metrics = [data['cpu_avg'], data['cpu_p95'], data['cpu_p99']]
req_metrics = [data['req_avg'], data['req_p95'], data['req_p99']]

x = range(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
rects1 = ax.bar([p - width/2 for p in x], cpu_metrics, width, label='CPU-based', color='#4C72B0', edgecolor='black', linewidth=0.5)
rects2 = ax.bar([p + width/2 for p in x], req_metrics, width, label='Workload-based', color='#DD8452', edgecolor='black', linewidth=0.5)

ax.set_ylabel('Latency (ms)')
ax.set_title('Median Latency Metrics (Rounds 13-22)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
ax.set_ylim(1000, 1080)
fig.tight_layout()
plt.savefig("docs/chart_latency_bar.png")
plt.close()

# 2. Boxplot: P95 and P99 Distribution
df_p95 = pd.DataFrame({
    'Strategy': ['CPU-based']*10 + ['Workload-based']*10,
    'Latency (ms)': raw_data['cpu_p95'] + raw_data['req_p95'],
    'Metric': ['P95']*20
})
df_p99 = pd.DataFrame({
    'Strategy': ['CPU-based']*10 + ['Workload-based']*10,
    'Latency (ms)': raw_data['cpu_p99'] + raw_data['req_p99'],
    'Metric': ['P99']*20
})
df_combined = pd.concat([df_p95, df_p99])

fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
sns.boxplot(data=df_combined, x='Metric', y='Latency (ms)', hue='Strategy', palette=['#4C72B0', '#DD8452'], ax=ax, linewidth=1.2, fliersize=4)
ax.set_title('Latency Distribution and Variance (10 Rounds)')
ax.set_ylabel('Latency (ms)')
ax.set_xlabel('')
fig.tight_layout()
plt.savefig("docs/chart_latency_box.png")
plt.close()

# 3. Bar Chart: Scaling Behavior
labels = ['Scale-out', 'Max Instances']
cpu_scaling = [data['cpu_scaleout'], data['cpu_maxcap']]
req_scaling = [data['req_scaleout'], data['req_maxcap']]
x_scaling = range(len(labels))

fig, ax = plt.subplots(figsize=(5, 4), dpi=300)
rects1 = ax.bar([p - width/2 for p in x_scaling], cpu_scaling, width, label='CPU-based', color='#4C72B0', edgecolor='black', linewidth=0.5)
rects2 = ax.bar([p + width/2 for p in x_scaling], req_scaling, width, label='Workload-based', color='#DD8452', edgecolor='black', linewidth=0.5)

ax.set_ylabel('Count')
ax.set_title('Scaling Behavior (Median per Round)')
ax.set_xticks(x_scaling)
ax.set_xticklabels(labels)
ax.legend()
fig.tight_layout()
plt.savefig("docs/chart_scaling.png")
plt.close()

# 4. Line Chart: Trend over rounds for P99
rounds = list(range(13, 23))
fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
ax.plot(rounds, raw_data['cpu_p99'], marker='o', linestyle='-', color='#4C72B0', label='CPU-based', linewidth=1.5)
ax.plot(rounds, raw_data['req_p99'], marker='s', linestyle='--', color='#DD8452', label='Workload-based', linewidth=1.5)
ax.set_title('P99 Latency Trend Across Experimental Rounds')
ax.set_xlabel('Experimental Round (13-22)')
ax.set_ylabel('P99 Latency (ms)')
ax.set_xticks(rounds)
ax.legend()
fig.tight_layout()
plt.savefig("docs/chart_p99_trend.png")
plt.close()

print("Enhanced charts generated successfully.")
