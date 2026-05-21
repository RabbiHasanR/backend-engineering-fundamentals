# CI/CD Pipeline Setup — Jenkins + Gogs (Phase 1: Test Server)

A runbook for setting up an automated test-server deployment pipeline using Jenkins and a self-hosted Gogs server, for projects deployed to dedicated EC2 instances without containers.

This document covers **Phase 1 only — automatic deploy to the test server on merge to the `test` branch**. Phase 2 (manual-approval deploy to live) will be added later.

---

## 1. Background

### Existing deployment (before CI/CD)

Each service runs on its own dedicated EC2:

- **Frontend (Ember.js):** built locally on the developer machine → `dist/` pushed to Gogs → pulled onto the frontend EC2 → served via nginx with SSL.
- **Backend (Django / FastAPI + PostgreSQL):** code pulled from Gogs onto the backend EC2 → run with gunicorn + uvicorn (or daphne for Django Channels) behind nginx as a reverse proxy.

Every update — even a one-line fix — requires SSH into the target EC2, pulling code, installing dependencies, restarting the service, and verifying. Across many services this is slow, error-prone, and pure repetition.

### Why CI/CD

Goals:

1. Remove manual deploy steps for routine changes.
2. Keep a QA gate before code reaches production.
3. Fit the existing infra — no migration to containers, no move to GitHub.

### Constraints that shaped the design

- **No Docker** — services run directly on EC2 with systemd + nginx.
- **No GitHub** — code lives in a self-hosted Gogs server.
- **Dedicated EC2 per service** — this model stays.
- **Jenkins** is chosen as the orchestrator: it fits a non-containerised, EC2-per-service model and integrates cleanly with Gogs via webhooks.

---

## 2. Pipeline design

### Flow

```text
developer ──► PR to `test` branch ──► merge
                                       │
                                       ▼
                          Gogs webhook → Jenkins
                                       │
                                       ▼
                    Jenkins SSHes into Test EC2
                                       │
                                       ▼
                  pull → install → migrate → restart → health-check
                                       │
                                       ▼
                              QA verifies on test
                                       │
                                       ▼
                       (Phase 2) manual deploy to live
```

### Branch model

| Branch | Purpose                                      |
|--------|----------------------------------------------|
| `test` | Merging here auto-deploys to the test server |
| `live` | Reserved for Phase 2 (manual deploy)         |

Feature branches → PR into `test` → merge triggers Jenkins.

### Infra layout

```text
┌──────────────┐        ┌──────────────┐
│   Gogs EC2   │──────► │  Jenkins EC2 │
│  (webhook)   │        │ (orchestrator)│
└──────────────┘        └──────┬───────┘
                               │ SSH
                               ▼
                        ┌──────────────┐
                        │   Test EC2   │
                        │ (all services│
                        │  for QA)     │
                        └──────────────┘
```

- One dedicated EC2 for Jenkins.
- For now, a **single shared test EC2** hosts all services in test (frontend + APIs) to keep cost and setup low. The pipeline does not assume this — each service's Jenkins job targets a host by IP, so individual services can be moved to their own dedicated test EC2 later without changing the overall design.
- Live EC2s remain dedicated per service (used in Phase 2).

---

## 3. One-time setup

Do these steps **once** when bringing up Jenkins. After this, onboarding a new service follows the per-service checklist in §4.

### 3.1 Linux distribution note

The setup scripts referenced in this guide (`install-jenkins.sh`, `install-plugins.sh`, `generate-ssh-keys.sh`) are written for **Amazon Linux 2023** and use `dnf`. The setup is identical in shape on Ubuntu, Debian, or other distros — only the package manager and a few package names differ:

| Concern | Amazon Linux 2023 | Ubuntu / Debian |
| --- | --- | --- |
| Package manager | `dnf install -y …` | `apt-get install -y …` |
| Java 21 | `java-21-amazon-corretto-devel` | `openjdk-21-jdk` |
| Jenkins repo | `pkg.jenkins.io/rpm-stable` | `pkg.jenkins.io/debian-stable` (add apt key + source list) |
| Default SSH user | `ec2-user` | `ubuntu` |

If you are on Ubuntu, adapt the install commands accordingly — the rest of the runbook (Jenkins config, SSH key generation, Gogs webhook, pipeline) is distro-independent.

### 3.2 Install Jenkins on the dedicated EC2

SSH into the Jenkins EC2 and run:

```bash
sudo bash install-jenkins.sh
```

What the script installs:

- **Java 21** — required by Jenkins.
- **Jenkins LTS** — enabled and started under systemd.
- **Node.js 22 LTS** — needed because frontend builds (Ember/React) run on the Jenkins EC2; the `dist/` folder is then transferred to the target.
- **Git, rsync, jq, curl, wget** — used throughout pipelines.

Python is **not** installed on Jenkins — Django/FastAPI builds run on the target EC2, not here.

After the script finishes, complete the setup wizard:

1. Open `http://<jenkins-public-ip>:8080`.
2. Retrieve the initial admin password: `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`.
3. Choose **Install suggested plugins**.
4. Create the admin user.
5. Set Jenkins URL to the **private IP**: `http://<jenkins-private-ip>:8080` (webhooks from Gogs use the private IP).

### 3.3 Install required plugins

```bash
sudo bash install-plugins.sh
```

The script installs the plugins needed by this pipeline:

| Plugin                     | Why it is needed                                |
|----------------------------|-------------------------------------------------|
| `git`                      | Clone Gogs repos                                |
| `gogs-webhook`             | Receive Gogs webhook payloads                   |
| `generic-webhook-trigger`  | Token-based webhook → pipeline mapping          |
| `ssh-agent`                | SSH into target EC2 using stored credentials    |
| `workflow-aggregator`      | Pipeline (Jenkinsfile) support                  |
| `credentials-binding`      | Use stored credentials inside pipelines         |
| `pipeline-stage-view`      | Pipeline visualisation                          |
| `timestamper`, `ansicolor` | Readable console logs                           |

The script will prompt for the Jenkins admin username/password created in §3.2, then restart Jenkins.

### 3.4 Generate SSH deploy keys

Jenkins needs SSH access to the test EC2 to deploy. Generate a dedicated key pair (separate from any personal keys, and separate per environment so a test-key leak does not affect live):

```bash
sudo bash generate-ssh-keys.sh
```

The script:

1. Asks **separately** for the SSH username on the test EC2s and on the live EC2s (default `ec2-user`). Test and live can use different users — e.g. test on Ubuntu (`ubuntu`), live on Amazon Linux (`ec2-user`) — the script stores each independently and uses them in the printed instructions.
2. Generates two ed25519 key pairs in `/var/lib/jenkins/.ssh/`:
   - `test-ec2-key` / `test-ec2-key.pub`
   - `live-ec2-key` / `live-ec2-key.pub` (kept for Phase 2)
3. Sets correct ownership (`jenkins:jenkins`) and permissions.
4. Prints the public keys and follow-up instructions.

> When registering the credentials in Jenkins (§3.6), the **Username** field on `test-ec2-ssh-key` must match the test SSH user, and the **Username** on `live-ec2-ssh-key` must match the live SSH user — they are stored as two separate credentials precisely so they can differ.

### 3.5 Authorise the public key on the test EC2

SSH into the test EC2 and append the Jenkins **test** public key to the deploy user's `authorized_keys`:

```bash
ssh <ssh-user>@<test-ec2-private-ip>
echo '<paste-test-ec2-key.pub-contents>' >> ~/.ssh/authorized_keys
```

Repeat for every test EC2 Jenkins must deploy to (in this setup there is one shared test EC2).

### 3.6 Register the private key as a Jenkins credential

In the Jenkins UI:

1. **Manage Jenkins → Credentials → System → Global credentials → Add Credentials**.
2. Set:
   - **Kind:** SSH Username with private key
   - **ID:** `test-ec2-ssh-key` *(used by the Jenkinsfile — keep this exact ID)*
   - **Username:** `ubuntu` or `ec2-user`, matching the target EC2
   - **Private Key:** *Enter directly* → paste the contents of `sudo cat /var/lib/jenkins/.ssh/test-ec2-key`

### 3.7 Verify SSH from Jenkins to the test EC2

From the Jenkins EC2:

```bash
sudo -u jenkins ssh \
  -i /var/lib/jenkins/.ssh/test-ec2-key \
  -o StrictHostKeyChecking=no \
  <ssh-user>@<test-ec2-private-ip> hostname
```

Expected: prints the target hostname, no password prompt.

### 3.8 Configure Gogs for private-IP webhooks

By default Gogs blocks webhook delivery to private network addresses. Edit `custom/conf/app.ini` on the Gogs server:

```ini
[security]
LOCAL_NETWORK_ALLOWLIST = <jenkins-private-ip>

[webhook]
DELIVER_TIMEOUT = 30
SKIP_TLS_VERIFY = false
```

Also ensure `ALLOWED_LOCAL_NETWORK_ADDRESSES = *` (or a more specific allowlist) is set under `[server]`.

Restart Gogs:

```bash
sudo systemctl restart gogs
```

### 3.9 Open the firewall

On the Jenkins EC2 security group, allow inbound TCP **8080** from the Gogs server's private IP. Without this the webhook will never reach Jenkins.

One-time setup is now complete.

---

## 4. Per-service onboarding (repeat for every new service)

This is the canonical checklist for adding a new service to the pipeline.

### 4.1 Prepare the test EC2 for the service

On the test EC2, create the service layout once:

- Application directory (e.g. `/opt/<service-name>`).
- `git clone` the repo on the `test` branch.
- For backend services: create a Python virtualenv, install dependencies, create a `systemd` unit for gunicorn/uvicorn/daphne, configure nginx as the reverse proxy.
- For frontend services: configure nginx to serve `/opt/<service-name>/dist`.

Keep this step scripted (e.g. `setup-service.sh`) so it is reproducible — that script is service-specific and lives in each repo.

### 4.2 Add the Jenkinsfile to the repo

Each repo carries its own `Jenkinsfile` at the root, on the `test` branch.

- **Backend services:** the Jenkinsfile SSHes into the test EC2 and runs `git pull → pip install → migrate → systemctl restart → health-check`. On any failure it rolls back to the previous commit and restarts.
- **Frontend services:** the Jenkinsfile checks out on Jenkins, runs `npm ci && npm run build`, then `rsync`s the `dist/` folder to the test EC2 — nginx is reloaded if its config changed.

### 4.3 Create the Jenkins pipeline job

In the Jenkins UI:

1. **New Item → enter `<service-name>` → Pipeline → OK**.
2. **Build Triggers → Generic Webhook Trigger**, add two post-content parameters:
   - `ref` ← `$.ref` (JSONPath)
   - `repo_name` ← `$.repository.name` (JSONPath)
3. **Token:** `<service-name>-deploy-token` (any unique string — must be unique per service).
4. **Optional filter:**
   - Text: `$ref`
   - Expression: `^refs/heads/test$`
   This ensures only pushes to the `test` branch trigger the pipeline.
5. **Pipeline → Pipeline script from SCM:**
   - SCM: Git
   - Repository URL: `https://gogs.company.com/<org>/<repo>.git`
   - Credentials: add `Username with password` for Gogs if the repo is private (ID `gogs-repo-credentials`).
   - Branch Specifier: `*/test`
   - Script Path: `Jenkinsfile`
6. **Save**.

### 4.4 Add the Gogs webhook

In Gogs: **Repo → Settings → Webhooks → Add Webhook → Gogs**.

| Field | Value |
| --- | --- |
| Payload URL | `http://<jenkins-private-ip>:8080/generic-webhook-trigger/invoke?token=<service-name>-deploy-token` |
| Content Type | `application/json` |
| Secret | *(leave empty for now)* |
| Events | Push events only |
| Active | checked |

The token in the URL must match exactly the token from §4.3 step 3.

Click **Add Webhook**, then **Test Delivery** — Gogs should report HTTP 200 and a build should appear in Jenkins (it may fail on the test payload; that is fine — the goal is to confirm receipt).

### 4.5 End-to-end verification

1. On a feature branch, make a trivial change (e.g. bump a version string).
2. Push and open a PR into `test` in Gogs.
3. Merge the PR.
4. Watch the Jenkins job — a new build appears within seconds.
5. On the test EC2:

   ```bash
   systemctl status <service-name>
   curl http://localhost:<port>/health
   ```

The change should be live.

---

## 5. What the backend pipeline does

| # | Step | Action |
| --- | --- | --- |
| 1 | Save rollback point | Record the current commit hash on the target |
| 2 | Pull code | `git pull origin test` on the target |
| 3 | Install deps | `venv/bin/pip install -r requirements.txt` |
| 4 | Run migrations | `venv/bin/alembic upgrade head` (or `manage.py migrate`) |
| 5 | Restart service | `systemctl restart <service>` |
| 6 | Health check | `curl /health` — expect HTTP 200, retry up to 3 times |

If any step fails, the pipeline **rolls back**: checks out the saved commit, reinstalls its dependencies, restarts the service. The test server returns to its previous working state.

Frontend pipelines do not run migrations — they build on Jenkins, `rsync` to the target, and reload nginx.

---

## 6. Troubleshooting

### Webhook fires in Gogs but no build appears in Jenkins

- Confirm the security group on the Jenkins EC2 allows inbound 8080 from the Gogs server's private IP.
- Confirm the token in the webhook URL exactly matches the token in the Jenkins job.
- Check `Manage Jenkins → System Log` for webhook errors.
- Confirm `LOCAL_NETWORK_ALLOWLIST` in Gogs `app.ini` includes the Jenkins private IP.

### Jenkins build starts but SSH to the test EC2 fails

- Re-run the manual SSH test from §3.7.
- Confirm the credential ID in the Jenkinsfile matches `test-ec2-ssh-key`.
- Confirm the public key is in `~/.ssh/authorized_keys` on the test EC2 for the correct user.
- Confirm permissions: `~/.ssh` is `700`, `authorized_keys` is `600`.

### Health check fails and pipeline rolls back

- Check `journalctl -u <service-name> -n 100` on the test EC2.
- Confirm the service binds to the expected port and `/health` endpoint exists.
- Confirm migrations did not fail silently (re-run step 4 manually on the target).

### Build appears in Jenkins but is triggered on every branch push

- The Optional Filter (`^refs/heads/test$`) is missing or incorrect on the job.

---

## 7. Adding more services later

Once the first service is live, every subsequent service follows §4 verbatim. The only things that change per service:

- Service name (used in the Jenkins job name, systemd unit, deploy directory).
- Webhook token (must be unique per service).
- The repo's `Jenkinsfile` (frontend vs backend template).
- The per-service `setup-service.sh` on the test EC2 (one-time).

The Jenkins EC2, the SSH keys, the Gogs `app.ini` changes, and the plugin set are all set up once and shared.

---

## 8. Phase 2 (not in this document)

Phase 2 will add:

- A `live` branch per repo.
- Manual-approval Jenkins stage (button-click promotion from test to live).
- Live-environment SSH credential (`live-ec2-ssh-key`) — the key pair is already generated in §3.4.
- Per-service live EC2 onboarding.

That will be appended here when implemented.
