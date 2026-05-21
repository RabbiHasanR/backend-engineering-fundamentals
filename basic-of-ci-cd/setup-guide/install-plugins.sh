#!/bin/bash
# ============================================================
# Jenkins Plugin Installation
# ============================================================
# Run AFTER:
#   1. Jenkins is running (sudo systemctl status jenkins)
#   2. You completed the setup wizard in browser
#   3. You created your admin user
#
# Run as: sudo bash install-plugins.sh
#
# NOTE: If jenkins-cli method fails, this script falls back
# to installing plugins directly into the plugins directory.
# ============================================================

set -e

JENKINS_URL="http://localhost:8080"
JENKINS_CLI="/tmp/jenkins-cli.jar"
JENKINS_PLUGIN_DIR="/var/lib/jenkins/plugins"

# List of required plugins
PLUGINS=(
    "git"                        # Git integration
    "gogs-webhook"               # Gogs webhook receiver
    "ssh-agent"                  # SSH key management for deploys
    "workflow-aggregator"        # Pipeline (Jenkinsfile support)
    "pipeline-stage-view"        # Pipeline visualization
    "credentials-binding"        # Credentials in pipelines
    "email-ext"                  # Extended email notifications
    "generic-webhook-trigger"    # Custom webhook notifications
    "blueocean"                  # Modern pipeline UI
    "pipeline-utility-steps"     # Utility steps for pipelines
    "timestamper"                # Timestamps in console output
    "ansicolor"                  # Color console output
)

echo "=========================================="
echo "  Jenkins Plugin Installation"
echo "=========================================="

# ---- Check Jenkins is running ----
echo ""
echo "[1/4] Checking Jenkins status..."
if ! systemctl is-active --quiet jenkins; then
    echo "ERROR: Jenkins is not running."
    echo "Start it with: sudo systemctl start jenkins"
    exit 1
fi
echo "  Jenkins is running."

# ---- Get credentials ----
echo ""
echo "[2/4] Enter your Jenkins admin credentials"
echo "  (the user you created in the setup wizard)"
echo ""
read -p "  Username: " JENKINS_USER
read -sp "  Password: " JENKINS_PASS
echo ""

# ---- Try CLI method first ----
echo ""
echo "[3/4] Downloading Jenkins CLI..."
if wget -q "${JENKINS_URL}/jnlpJars/jenkins-cli.jar" -O "$JENKINS_CLI" 2>/dev/null; then
    echo "  CLI downloaded successfully."

    echo ""
    echo "[4/4] Installing plugins via CLI..."
    FAILED=0

    for plugin in "${PLUGINS[@]}"; do
        echo -n "  Installing: ${plugin}... "
        if java -jar "$JENKINS_CLI" \
            -s "$JENKINS_URL" \
            -auth "${JENKINS_USER}:${JENKINS_PASS}" \
            install-plugin "$plugin" -deploy 2>/dev/null; then
            echo "OK"
        else
            echo "FAILED (may already be installed)"
            FAILED=$((FAILED + 1))
        fi
    done

    # Restart Jenkins to activate
    echo ""
    echo "Restarting Jenkins to activate plugins..."
    java -jar "$JENKINS_CLI" \
        -s "$JENKINS_URL" \
        -auth "${JENKINS_USER}:${JENKINS_PASS}" \
        safe-restart 2>/dev/null || sudo systemctl restart jenkins

    # Cleanup
    rm -f "$JENKINS_CLI"

    echo ""
    echo "=========================================="
    echo "  Plugins installed! Jenkins is restarting."
    echo "=========================================="

    if [ $FAILED -gt 0 ]; then
        echo ""
        echo "  ${FAILED} plugin(s) may have failed. This is usually"
        echo "  because they were already installed by the setup wizard."
        echo "  Check: Jenkins > Manage Jenkins > Plugins > Installed"
    fi

else
    # ---- Fallback: install via direct download ----
    echo "  CLI download failed. Using direct plugin install method."
    echo ""
    echo "[4/4] Installing plugins directly..."

    # Get Jenkins version for plugin compatibility
    JENKINS_VERSION=$(rpm -q jenkins --queryformat '%{VERSION}' 2>/dev/null || echo "latest")
    echo "  Jenkins version: ${JENKINS_VERSION}"

    for plugin in "${PLUGINS[@]}"; do
        echo -n "  Downloading: ${plugin}... "
        PLUGIN_URL="https://updates.jenkins.io/latest/${plugin}.hpi"

        if wget -q "$PLUGIN_URL" -O "${JENKINS_PLUGIN_DIR}/${plugin}.hpi" 2>/dev/null; then
            echo "OK"
        else
            echo "FAILED"
        fi
    done

    # Fix permissions
    chown -R jenkins:jenkins "$JENKINS_PLUGIN_DIR"

    # Restart Jenkins
    echo ""
    echo "Restarting Jenkins..."
    systemctl restart jenkins

    echo ""
    echo "=========================================="
    echo "  Plugins downloaded! Jenkins is restarting."
    echo "=========================================="
    echo ""
    echo "  NOTE: Some plugins may need dependencies."
    echo "  After restart, go to:"
    echo "    Jenkins > Manage Jenkins > Plugins"
    echo "  and check for any missing dependencies."
fi

echo ""
echo "Wait ~30-60 seconds for Jenkins to restart, then access:"
echo "  ${JENKINS_URL}"
echo ""
echo "VERIFY PLUGINS:"
echo "  Go to: Manage Jenkins > Plugins > Installed plugins"
echo "  Confirm these are listed:"
echo "    - Git"
echo "    - Gogs webhook"
echo "    - SSH Agent"
echo "    - Pipeline"
echo "    - Blue Ocean"
echo "    - Email Extension"
echo "    - Credentials Binding"
echo ""
echo "IF ANY PLUGIN IS MISSING:"
echo "  You can install it manually from the Jenkins UI:"
echo "  Manage Jenkins > Plugins > Available plugins > Search"
echo ""
echo "NEXT STEPS:"
echo "  1. Run: sudo bash generate-ssh-keys.sh"
echo "  2. Add credentials to Jenkins"
echo "  3. Create your first pipeline"
echo ""
