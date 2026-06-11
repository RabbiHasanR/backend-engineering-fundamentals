## AWS CodeDeploy — Quick Summary

**What it is:** A deployment automation service that pushes your application to EC2, on-premises servers, Lambda functions, or ECS containers.

---

### Where it deploys (Compute Platforms)
- **EC2 / On-Premises** — traditional servers, supports both in-place and blue/green
- **AWS Lambda** — deploys new function versions, blue/green only
- **Amazon ECS** — deploys containerized apps as task sets, blue/green only

---

### Deployment Types
- **In-place** — stops the old app, installs new one on the same instance. EC2 only.
- **Blue/Green** — spins up a new environment, shifts traffic to it, then tears down the old one. Safer, easier to roll back.

---

### Key Concepts
| Term | Meaning |
|---|---|
| **Application** | Top-level grouping in CodeDeploy |
| **Deployment Group** | The set of instances/functions to deploy to |
| **Revision** | Your app code + AppSpec file bundled together |
| **AppSpec file** | YAML/JSON file that tells CodeDeploy *how* to deploy |
| **Deployment Config** | Controls speed — canary, linear, or all-at-once |

---

### Traffic Shifting Options (Lambda & ECS)
- **All-at-once** — instant switch
- **Canary** — small % first, then the rest
- **Linear** — gradual equal increments

---

### Why use it?
Automated, scalable deployments with rollback support, minimal downtime, and integrates with your existing CI/CD tools like Jenkins or GitHub Actions.