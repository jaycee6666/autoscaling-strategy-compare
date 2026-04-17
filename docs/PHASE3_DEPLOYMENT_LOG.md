# Phase 3 Deployment Log

## Scope

- Task 2: Deploy Flask test app to EC2 instances behind ALB
- Task 3: Verify load generator connectivity to ALB
- Task 4: Document deployment workflow and troubleshooting

## Deployment Metadata

- **Date (UTC):** 2026-04-17
- **Region:** us-east-1
- **ALB DNS:** `experiment-alb-1466294824.us-east-1.elb.amazonaws.com`
- **ASGs:** `asg-cpu`, `asg-request`
- **Launch templates:** `app-cpu-lt`, `app-request-lt`

## Task 2 Execution Log (Flask App Deployment)

### What was deployed

- Added `deployment/deploy_app.py` (boto3-only orchestrator)
- Added `deployment/__init__.py`
- Reused Flask app source from `apps/test_app/app.py`
- Generated launch template version updates with embedded user data to:
  - install Python + Flask + boto3 + requests
  - place app at `/opt/test_app/app.py`
  - create/start `test-app.service`

### Runtime notes

- Existing private subnets had **no default route (`0.0.0.0/0`)** and no NAT path.
- To complete app bootstrap reliably without adding new infrastructure, deployment script:
  - detected missing private subnet egress
  - updated ASGs to existing public subnets from `network-config.json`
  - triggered instance refresh for both ASGs

### Recorded deployment outputs

- Output report: `deployment/deploy_app_report.json`
- Latest successful report highlights:
  - `private_route_has_default_egress`: `false`
  - `subnet_updates`: applied to both ASGs
  - ALB health probe: `15/20` successful (`HTTP 200` after refresh stabilization)
  - Active listener target group healthy: `1/1`

### Health verification

- Endpoint tested: `http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health`
- Result: **HTTP 200 OK**
- Sample response:

```json
{
  "status": "healthy",
  "timestamp": "2026-04-17T07:04:11.610906",
  "version": "1.0"
}
```

## Task 3 Execution Log (Load Generator Connectivity)

### What was deployed

- Added `deployment/test_load_generator.py`
- Added report output `deployment/load_generator_test_report.json`

### Verification run

- Command:

```bash
venv/Scripts/python.exe deployment/test_load_generator.py --request-rate 6 --duration-seconds 30 --success-threshold 0.8
```

- Result summary:
  - Total requests: `180`
  - Successful: `180`
  - Failed: `0`
  - Success rate: `100%`
  - Threshold check (>= 80%): **PASS**

## Cost Snapshot (Approximate)

Current active resources relevant to Phase 3:

- 1 Application Load Balancer
- 2 ASGs (combined 3 running `t3.micro` instances observed during final verification)
- Associated EBS volumes and CloudWatch metrics

Estimated hourly cost (rough, region-dependent):

- ALB: ~`$0.025 - $0.035`/hour (plus LCU usage)
- EC2 t3.micro x3: ~`$0.03 - $0.04`/hour total
- **Total rough range:** `~$0.06 - $0.09`/hour

## Cleanup Reminder

Infrastructure intentionally remains running for Phase 4-5 experiments.

After experiments, clean up in this order:

1. Delete/scale down ASGs (removes instances)
2. Delete ALB listeners and ALB
3. Delete target groups
4. Delete launch templates
5. Delete security groups
6. Delete route tables, subnets, IGW, then VPC

Use boto3 scripts for cleanup to remain consistent with project constraints.
