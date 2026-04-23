Project Proposal

Comparative Analysis of Autoscaling Strategies: Resource-Based CPU
Utilization vs. Workload-Based Request Rate

Spring 2026

1. The subject of your project

The subject of this project is Cloud Elasticity and Autoscaling Mechanisms. We specifi-
cally focus on optimizing the scaling performance of microservices under bursty traffic loads.
We will investigate how different triggering metrics—specifically comparing CPU utilization
against Request Count—affect the stability and responsiveness of a web service in the Amazon
Web Services (AWS) environment.

2. The nature of your project

Nature: Research
Justification: This project fits the ”Research” category because we are not simply building a
standard application. Instead, we are studying the specific technical challenge of ”Autoscaling
Lag,” defined as the delay between a traffic spike and the readiness of new resources. We
propose to conduct a comparative performance evaluation between a standard solution (CPU-
based scaling) and a workload-centric solution (Request-based scaling). Our goal is to derive
experimental data to demonstrate which strategy offers lower latency for specific workload
patterns.

3. A brief summary of the subject

Context and Motivation: Elasticity is a fundamental advantage of cloud computing. A com-
mon challenge in production environments is handling sudden traffic spikes, often referred to as
bursty workloads. The default autoscaling policy in AWS often relies on average CPU utiliza-
tion. However, CPU usage is typically a lagging indicator. By the time CPU usage spikes, the
system may already be overwhelmed, leading to high latency or dropped requests resulting in
HTTP 503 errors. We hypothesize that scaling based on ”Request Count,” a leading indicator,
will trigger scaling actions faster and significantly reduce the error rate.

Reference Website:

• AWS Application Auto Scaling: https://aws.amazon.com/autoscaling/

Methodology and Execution Plan: We will build a testbed on AWS to simulate a mi-

croservice environment. The project will proceed in three phases:

1. Infrastructure Setup: We will deploy a stateless Python Flask web application on Ama-
zon EC2 instances. These instances will be managed by an AWS Auto Scaling Group
(ASG) and distributed behind an Application Load Balancer (ALB).

2. Experiment Design: We will define two distinct experimental scenarios:



• Scenario A: The Baseline Strategy. The ASG is configured with a Target Tracking
Policy based on Average CPU Utilization, set to maintain a specific target such as
50%.

• Scenario B: The Proposed Strategy. The ASG is configured with a Target Track-

ing Policy based on the ALB Request Count Per Target metric.

3. Testing and Evaluation: We will use load testing tools such as Locust or Apache JMeter
to generate synthetic traffic with sudden spikes. We will monitor the system using Ama-
zon CloudWatch. The performance will be evaluated based on the following metrics:

• Response Latency: We will measure the 95th percentile (P95) response time dur-

ing the scaling process to assess user experience.

• Scale-out Latency: The time difference between the initial traffic spike and the

readiness of new instances.

• Error Rate: The percentage of failed requests observed during the scale-out phase.

4. Findings

Experimental Execution and Results (Completed April 23, 2026):

We executed a comprehensive burst scenario experiment comparing both autoscaling strategies using an
EC2-based load generator (t3.small instance in us-east-1) to eliminate network latency as a confounding
variable. The burst scenario consisted of four phases: Preheating (60s), Baseline Load (120s), Burst
(200s), and Recovery (120s), for a total test duration of 500 seconds.

**CPU Utilization Strategy (Scenario A) Results:**

The CPU-based autoscaling strategy was configured to maintain 50% average CPU utilization. The
results were:

• Response Latency (P95): 7,328 ms
• Scale-out Latency: N/A (no scaling occurred)
• Error Rate: 12.6%
• Scaling Events: 0 (policy never triggered)
• Maximum Capacity Reached: 1 instance (remained at initial state)

**Root Cause Analysis:** The CPU strategy requires 3 consecutive minutes (180 seconds) of sustained
CPU utilization above 50%. During the 200-second burst phase, average CPU was 39.9% with a peak of
54.4%. Time spent above 50% was only 20-30 seconds (occurring briefly at burst peak). The policy
never triggered because the sustained threshold was never met. As a result, the single t3.micro
instance became overwhelmed, causing a 12.6% error rate and high response latency.

**Request-Rate Strategy (Scenario B) Results:**

The request-rate strategy was configured with a target of 100 requests per minute per target instance.
The results were:

• Response Latency (P95): 1,261 ms (82% improvement over CPU strategy)
• Scale-out Latency: ~138 seconds (well below the 300-second acceptable threshold)
• Error Rate: 3.1% (meets the <5% requirement)
• Scaling Events: 1 successful scale-out event
• Maximum Capacity Reached: 5 instances
• Load Distribution: Successful distribution across scaled instances

**Key Finding:** Request-rate strategy successfully detected the incoming burst within 138 seconds
and scaled from 1 to 5 instances, distributing the load appropriately. The lower per-instance demand
allowed each instance to maintain acceptable performance.

Evaluation Against Proposal Acceptance Criteria:

1. Response Latency (P95 < 500ms): Request-Rate achieves 1,261ms (exceeds target by 2.5x, but
   represents 82% improvement over CPU strategy)

2. Scale-out Latency (< 300s): Request-Rate achieves 138s ✓ PASS

3. Error Rate (< 5%): Request-Rate achieves 3.1% ✓ PASS

Conclusion:

The Request-Rate strategy passes 2 of 3 acceptance criteria and substantially outperforms the CPU
strategy across all metrics. The CPU strategy fails to scale entirely due to its reliance on sustained
utilization thresholds that are not met during realistic burst patterns. For production environments
with bursty workloads, Request-Rate scaling is the clear winner. The P95 response time can be further
optimized by deploying stronger instance types (t3.small vs t3.micro) or adjusting the scaling
threshold to trigger at lower request rates (50 req/min instead of 100).

---

5. Group Members
   Member 1 WU Wanpeng 
   Member 2 CHEN Sijie



