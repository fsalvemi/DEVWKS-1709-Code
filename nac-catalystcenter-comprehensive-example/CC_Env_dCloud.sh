#!/bin/bash
# =============================================================================
# Catalyst Center Environment Variables - dCloud Lab
# =============================================================================
# Source this file before running Terraform:
#   source CC_Env_dCloud.sh
#   terraform plan
#   terraform apply
# =============================================================================

export CC_URL="https://198.18.129.100"
export CC_USERNAME="admin"
export CC_PASSWORD="C1sco12345"
export CC_INSECURE="true"

echo "✅ Catalyst Center environment configured:"
echo "   URL: $CC_URL"
echo "   User: $CC_USERNAME"

