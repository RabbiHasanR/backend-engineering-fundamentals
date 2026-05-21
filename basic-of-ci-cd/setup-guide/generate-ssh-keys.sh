#!/bin/bash
# ============================================================
# Generate SSH Key Pairs for Jenkins Deployments
# ============================================================
# Creates SEPARATE key pairs for test and live environments.
# Separate keys = if test key is compromised, live is safe.
#
# Run as: sudo bash generate-ssh-keys.sh
#
# IMPORTANT: Your target EC2s may use different SSH users:
#   Amazon Linux 2023 → ec2-user
#   Ubuntu            → ubuntu
#   Custom AMI        → could be anything
# The script will ask you for the correct username.
# ============================================================

set -e

JENKINS_SSH_DIR="/var/lib/jenkins/.ssh"

echo "=========================================="
echo "  Generate Jenkins SSH Deploy Keys"
echo "=========================================="

# ---- Ask for SSH usernames on target servers ----
echo ""
echo "What SSH username do your TARGET EC2s use?"
echo "  (Amazon Linux = ec2-user, Ubuntu = ubuntu)"
echo ""
read -p "  SSH user for TEST servers [ec2-user]: " TEST_USER
TEST_USER=${TEST_USER:-ec2-user}

read -p "  SSH user for LIVE servers [ec2-user]: " LIVE_USER
LIVE_USER=${LIVE_USER:-ec2-user}

echo ""
echo "  Test servers SSH user: ${TEST_USER}"
echo "  Live servers SSH user: ${LIVE_USER}"

# ---- Create .ssh directory ----
mkdir -p "$JENKINS_SSH_DIR"

# ---- Generate test environment key ----
echo ""
echo "[1/3] Generating key pair for TEST environment..."
if [ -f "${JENKINS_SSH_DIR}/test-ec2-key" ]; then
    echo "  WARNING: test-ec2-key already exists."
    read -p "  Overwrite? (y/N): " OVERWRITE
    if [ "$OVERWRITE" != "y" ] && [ "$OVERWRITE" != "Y" ]; then
        echo "  Skipping test key generation."
    else
        ssh-keygen -t ed25519 -f "${JENKINS_SSH_DIR}/test-ec2-key" -N "" -C "jenkins-test-deploy" -q
        echo "  Generated new test key."
    fi
else
    ssh-keygen -t ed25519 -f "${JENKINS_SSH_DIR}/test-ec2-key" -N "" -C "jenkins-test-deploy" -q
    echo "  Generated test key."
fi

# ---- Generate live environment key ----
echo ""
echo "[2/3] Generating key pair for LIVE environment..."
if [ -f "${JENKINS_SSH_DIR}/live-ec2-key" ]; then
    echo "  WARNING: live-ec2-key already exists."
    read -p "  Overwrite? (y/N): " OVERWRITE
    if [ "$OVERWRITE" != "y" ] && [ "$OVERWRITE" != "Y" ]; then
        echo "  Skipping live key generation."
    else
        ssh-keygen -t ed25519 -f "${JENKINS_SSH_DIR}/live-ec2-key" -N "" -C "jenkins-live-deploy" -q
        echo "  Generated new live key."
    fi
else
    ssh-keygen -t ed25519 -f "${JENKINS_SSH_DIR}/live-ec2-key" -N "" -C "jenkins-live-deploy" -q
    echo "  Generated live key."
fi

# ---- Set permissions ----
echo ""
echo "[3/3] Setting permissions..."
chown -R jenkins:jenkins "$JENKINS_SSH_DIR"
chmod 700 "$JENKINS_SSH_DIR"
chmod 600 "${JENKINS_SSH_DIR}/test-ec2-key" 2>/dev/null || true
chmod 600 "${JENKINS_SSH_DIR}/live-ec2-key" 2>/dev/null || true
chmod 644 "${JENKINS_SSH_DIR}/test-ec2-key.pub" 2>/dev/null || true
chmod 644 "${JENKINS_SSH_DIR}/live-ec2-key.pub" 2>/dev/null || true

# Also create a known_hosts file so SSH doesn't prompt
touch "${JENKINS_SSH_DIR}/known_hosts"
chown jenkins:jenkins "${JENKINS_SSH_DIR}/known_hosts"
chmod 644 "${JENKINS_SSH_DIR}/known_hosts"

echo "  Permissions set."

# ---- Print public keys ----
echo ""
echo "=========================================="
echo "  Keys generated successfully!"
echo "=========================================="

echo ""
echo "================================================"
echo "  PUBLIC KEY FOR TEST EC2s (copy this)"
echo "================================================"
cat "${JENKINS_SSH_DIR}/test-ec2-key.pub"
echo ""

echo ""
echo "================================================"
echo "  PUBLIC KEY FOR LIVE EC2s (copy this)"
echo "================================================"
cat "${JENKINS_SSH_DIR}/live-ec2-key.pub"
echo ""

echo ""
echo "=========================================="
echo "  STEP A: Add public keys to target EC2s"
echo "=========================================="
echo ""
echo "For EACH test EC2, run:"
echo "  ssh ${TEST_USER}@<test-ec2-ip>"
echo "  echo '$(cat ${JENKINS_SSH_DIR}/test-ec2-key.pub)' >> ~/.ssh/authorized_keys"
echo ""
echo "For EACH live EC2, run:"
echo "  ssh ${LIVE_USER}@<live-ec2-ip>"
echo "  echo '$(cat ${JENKINS_SSH_DIR}/live-ec2-key.pub)' >> ~/.ssh/authorized_keys"
echo ""

echo "=========================================="
echo "  STEP B: Add private keys to Jenkins UI"
echo "=========================================="
echo ""
echo "1. Go to: Jenkins > Manage Jenkins > Credentials"
echo "   > System > Global credentials > Add Credentials"
echo ""
echo "2. For TEST key:"
echo "   Kind:        SSH Username with private key"
echo "   ID:          test-ec2-ssh-key"
echo "   Username:    ${TEST_USER}"
echo "   Private Key: Enter directly (paste below)"
echo ""
echo "3. For LIVE key:"
echo "   Kind:        SSH Username with private key"
echo "   ID:          live-ec2-ssh-key"
echo "   Username:    ${LIVE_USER}"
echo "   Private Key: Enter directly (paste below)"
echo ""

echo "=========================================="
echo "  STEP C: Test SSH connectivity"
echo "=========================================="
echo ""
echo "After adding public keys to target EC2s, test from here:"
echo ""
echo "  sudo -u jenkins ssh -i ${JENKINS_SSH_DIR}/test-ec2-key -o StrictHostKeyChecking=no ${TEST_USER}@<test-ec2-ip> hostname"
echo ""
echo "  sudo -u jenkins ssh -i ${JENKINS_SSH_DIR}/live-ec2-key -o StrictHostKeyChecking=no ${LIVE_USER}@<live-ec2-ip> hostname"
echo ""
echo "Both should print the target hostname with no password prompt."
echo ""

echo "=========================================="
echo "  To view private keys for pasting:"
echo "=========================================="
echo ""
echo "  sudo cat ${JENKINS_SSH_DIR}/test-ec2-key"
echo "  sudo cat ${JENKINS_SSH_DIR}/live-ec2-key"
echo ""
