# Phase 3 Deployment Guide

This guide covers Tasks 2-4 of Phase 3:

1. Deploy Flask test app to existing EC2/ASG infrastructure
2. Verify load generator connectivity to ALB
3. Record deployment operations and troubleshooting workflow

All steps below use **Python + boto3**, with no AWS CLI subprocess requirement.

---

## 1) Prerequisites

- Python 3.9+ available
- Virtual environment prepared at `venv/`
- boto3/requests/flask installed in venv
- Phase 3 Task 1 infrastructure already deployed
- Working directory:

```text
C:\project\CS5296\project3\autoscaling-strategy-compare
```

---

## 2) Key Inputs

These config files are required:

- `infrastructure/alb-config.json`
- `infrastructure/asg-config.json`
- `infrastructure/launch-templates-config.json`
- `infrastructure/network-config.json`
- `apps/test_app/app.py`

Primary ALB endpoint:

- `experiment-alb-1466294824.us-east-1.elb.amazonaws.com`

---

## 3) Deploy Flask App to EC2 via ASG Launch Templates

Run:

```bash
venv/Scripts/python.exe deployment/deploy_app.py --region us-east-1
```

What this script does:

1. Reads infra config + Flask app source
2. Builds user data that installs dependencies and starts `test-app.service`
3. Creates new launch template versions for CPU/request ASGs
4. Updates ASGs to new launch template versions
5. Triggers instance refresh and waits for healthy in-service instances
6. Waits for target health on active listener target group
7. Probes `http://{ALB_DNS}/health` repeatedly and writes JSON report

Output artifact:

- `deployment/deploy_app_report.json`

### Important environment behavior

If private subnets have no egress route, the script automatically falls back by updating ASG subnet placement to existing public subnets from `network-config.json` so bootstrap package installation can complete.

---

## 4) Verify App Health Through ALB

Minimum check:

```text
GET http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health
```

Success criteria:

- HTTP status `200`
- JSON body includes `status: healthy`

---

## 5) Verify Load Generator Connectivity

Run:

```bash
venv/Scripts/python.exe deployment/test_load_generator.py --request-rate 6 --duration-seconds 30 --success-threshold 0.8
```

What this script does:

1. Loads ALB DNS from `infrastructure/alb-config.json`
2. Runs `scripts.load_generator.LoadGenerator` against `/health`
3. Computes success rate and threshold pass/fail
4. Writes report JSON

Output artifact:

- `deployment/load_generator_test_report.json`

Acceptance threshold:

- Initial requirement: >80% success rate
- Observed run: 100% (180/180)

---

## 6) Python Validation and Type-Safe Workflow

Before finalizing, run:

```bash
venv/Scripts/python.exe -m py_compile deployment/deploy_app.py deployment/test_load_generator.py apps/test_app/app.py
```

Optional targeted tests:

```bash
python -m pytest tests/test_deploy_app.py tests/test_phase3_load_generator_check.py -q
```

---

## 7) Troubleshooting

### A) ALB returns 502

Likely causes:

- Instance user data failed before app start
- Target group has no healthy registered targets

Actions:

1. Inspect `deployment/deploy_app_report.json` (`target_group_health`, `alb_health_probe`)
2. Check instance lifecycle and health in ASG details from report
3. Re-run deploy script after launch template update

### B) User data bootstrap fails with package repo timeout

Symptom:

- Console log shows `Cannot find a valid baseurl for repo` / mirror timeout

Cause:

- No outbound internet path from subnet (private route table missing default route/NAT)

Action used in this phase:

- Script automatically moved ASG subnet mapping to public subnets (safe for experiment staging)

### C) `InstanceRefreshInProgress` error

Action:

- Script now detects in-progress refresh and reuses current refresh ID instead of failing hard

### D) Load generator script cannot import project modules

Action:

- Script prepends project root to `sys.path` for cross-platform direct execution

---

## 8) Cost Awareness (Keep Running for Experiments)

Infrastructure should stay active for Phase 4-5 experiments.

Approximate active cost range during this phase:

- ALB + 3x t3.micro + storage/metrics: `~$0.06 - $0.09` per hour (rough)

After experiments, cleanup all resources to avoid ongoing charges.

---

## 9) Cleanup Steps (Post-Experiment)

Recommended order:

1. Scale ASGs to 0 / delete ASGs
2. Delete ALB listener(s) and ALB
3. Delete target groups
4. Delete launch templates
5. Delete security groups
6. Delete route tables/subnets/IGW/VPC

Prefer boto3 scripts for cleanup for consistency and reproducibility.
