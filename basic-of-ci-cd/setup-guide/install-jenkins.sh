#!/bin/bash
# ============================================================
# Jenkins CI/CD Server Setup - Amazon Linux 2023
# ============================================================
# HYBRID BUILD STRATEGY:
#   Jenkins builds frontends (Ember/React) locally, then
#   transfers dist/ to target EC2 via scp.
#   Backends (Django/FastAPI) pull and deploy directly on
#   target EC2 via SSH — no build step on Jenkins.
#
# INSTALLS:
#   - Java 21       → required by Jenkins
#   - Jenkins LTS   → CI/CD orchestrator
#   - Node.js 22    → for building Ember.js / React frontends
#   - Git           → clone repos, detect branches
#   - Utilities     → curl, jq, wget, rsync
#
# DOES NOT INSTALL:
#   - Python        → not needed (Django/FastAPI build on target EC2)
#
# Run as: sudo bash install-jenkins.sh
# ============================================================

set -e

echo "=========================================="
echo "  Jenkins CI/CD Server Installation"
echo "  Amazon Linux 2023 (April 2026)"
echo "=========================================="

# ---- 1. System update ----
echo ""
echo "[1/6] Updating system packages..."
dnf update -y

# ---- 2. Install Java 21 (REQUIRED by Jenkins) ----
echo ""
echo "[2/6] Installing Java 21 (Amazon Corretto)..."
dnf install -y java-21-amazon-corretto-devel fontconfig
echo "  $(java -version 2>&1 | head -1)"

# ---- 3. Install Jenkins LTS ----
# Repo: /rpm-stable/ (unified RPM endpoint since 2026)
# Key:  jenkins.io-2026.key (new signing key since Jan 2026)
echo ""
echo "[3/6] Installing Jenkins LTS..."
wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/rpm-stable/jenkins.repo
rpm --import https://pkg.jenkins.io/rpm-stable/jenkins.io-2026.key
dnf install -y jenkins

systemctl daemon-reload
systemctl enable jenkins
systemctl start jenkins
echo "  Jenkins installed. Waiting for startup..."
sleep 15

# ---- 4. Install Node.js 22 LTS (for Ember/React builds) ----
# Node.js 22 LTS "Jod" - Active LTS, supported until Oct 2027
# Needed because: Jenkins builds frontend dist/ locally, then
# transfers to target EC2 via scp. Target EC2 only needs nginx.
echo ""
echo "[4/6] Installing Node.js 22 LTS..."
if dnf list available nodejs22 &>/dev/null; then
    dnf install -y nodejs22
elif dnf list available nodejs20 &>/dev/null; then
    echo "  nodejs22 not in repo, installing nodejs20..."
    dnf install -y nodejs20
else
    echo "  Installing via NodeSource..."
    curl -fsSL https://rpm.nodesource.com/setup_22.x | bash -
    dnf install -y nodejs
fi
echo "  Node: $(node --version), npm: $(npm --version)"

# ---- 5. Install Git ----
echo ""
echo "[5/6] Installing Git..."
dnf install -y git
echo "  $(git --version)"

# ---- 6. Install utilities ----
# rsync is useful for efficient file transfer to target EC2
echo ""
echo "[6/6] Installing utilities..."
dnf install -y jq curl wget rsync

# ---- Create workspace directory for Jenkins builds ----
mkdir -p /var/lib/jenkins/workspace
chown jenkins:jenkins /var/lib/jenkins/workspace

# ---- Print results ----
echo ""
echo "=========================================="
echo "  INSTALLATION COMPLETE!"
echo "=========================================="
echo ""
echo "Installed:"
echo "  Java:    $(java -version 2>&1 | head -1)"
echo "  Jenkins: $(rpm -q jenkins)"
echo "  Node.js: $(node --version)"
echo "  npm:     $(npm --version)"
echo "  Git:     $(git --version)"
echo "  rsync:   $(rsync --version | head -1)"
echo ""

PUBLIC_IP=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "<your-ec2-ip>")

echo "Jenkins URL:"
echo "  http://${PUBLIC_IP}:8080"
echo ""
echo "Initial admin password:"
echo "------------------------------------"
cat /var/lib/jenkins/secrets/initialAdminPassword
echo ""
echo "------------------------------------"
echo ""
echo "BUILD STRATEGY:"
echo "  Frontend (Ember/React): build on Jenkins → scp dist/ to target"
echo "  Backend (Django/FastAPI): SSH to target → pull + deploy there"
echo ""
echo "NEXT STEPS:"
echo "  1. Open Jenkins URL in browser"
echo "  2. Paste the admin password"
echo "  3. Choose 'Install suggested plugins'"
echo "  4. Create your admin user"
echo "  5. Run: sudo bash install-plugins.sh"
echo ""
