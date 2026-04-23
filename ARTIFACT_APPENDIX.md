# Artifact Appendix - Group 55

This appendix provides all necessary details to understand, install, and evaluate the artifacts for the project: "Comparative Analysis of Resource-based and Workload-based Autoscaling Strategies in Cloud Computing Environments".

## 1. Artifact Overview

*   **Repository URL:** [https://github.com/jaycee6666/autoscaling-strategy-compare](https://github.com/jaycee6666/autoscaling-strategy-compare)
*   **Primary Artifacts:**
    1.  **Infrastructure as Code (IaC):** A suite of Python scripts using the Boto3 SDK to provision a full AWS environment.
    2.  **Automated Experiment Pipeline:** A master orchestration script that executes the comparative tests from end-to-end.
    3.  **Data & Analysis:** Pre-run, stabilized datasets from rounds 13-22 and visualization scripts.

## 2. Portable Workflow Framework

To simplify evaluation, the entire project is containerized using Docker, which standardizes the environment and all dependencies.

### Prerequisites
*   Docker Desktop installed and running.
*   AWS credentials configured on your host machine (e.g., via `~/.aws/credentials`).

### Build and Run with Docker
1.  **Build the Docker Image:**
    ```bash
    docker build -t autoscaling-artifact .
    ```
2.  **Run the Container:**
    Mount your AWS credentials directory into the container to provide access.
    ```bash
    docker run -it -v C:\Users\YourUser\.aws:/root/.aws autoscaling-artifact
    ```
3.  **Execute Experiments within the Container:**
    Once inside the container shell, you can execute the full pipeline.

## 3. Step-by-Step Instructions

### Step 1: Environment Setup
Inside the Docker container, all Python dependencies are pre-installed. You only need to verify your AWS connection.
```bash
# Verify credentials are mounted and working
aws sts get-caller-identity
```

### Step 2: Infrastructure Provisioning
```bash
python scripts/deploy_all.py
```
**Expected Outcome:** A complete AWS stack (VPC, ALB, two ASGs) is provisioned in `us-east-1`. The terminal will log the creation of each resource.

### Step 3: Application Deployment & Verification
```bash
# Inject Flask code into running instances
python deployment/deploy_app.py

# Verify health checks
python experiments/01_verify_infrastructure.py
```
**Expected Outcome:** The verification script will return `passed: true` for all target groups, confirming the Flask application is responding correctly.

### Step 4: Run Full Experiment Pipeline
```bash
python scripts/run_all_experiments.py
```
**Expected Outcome:** This will run the full 70-minute test suite. Since this is time-consuming, you can review the pre-existing results.

## 4. Evidence of Verification

The repository includes a complete, pre-run dataset for validation, which is consistent with the results presented in our report.

### Key Datasets and Outputs:
*   `experiments/results_round13_22_median.json`: Contains the aggregated median results showing the P99 latency reduction and scaling behavior.
*   `experiments/results/cpu_strategy_metrics.json` & `request_rate_experiment_metrics.json`: Raw data logs for each strategy.
*   `docs/*.png`: Generated charts, including the Boxplot that visually confirms the stability gains of the workload-based strategy.
*   `infrastructure/deployment-log.json`: A log file providing evidence of a successful infrastructure deployment.

These artifacts are complete, runnable, and provide verifiable evidence that directly supports the conclusions drawn in the project report.
