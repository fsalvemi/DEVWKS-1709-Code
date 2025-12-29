#!/bin/bash
# =============================================================================
# Catalyst Center Environment Variables - Sample Configuration
# =============================================================================
# Copy this file and update with your Catalyst Center credentials:
#   cp CC_Env_Sample.sh CC_Env.sh
#
# Then source before running Terraform:
#   source CC_Env.sh
#   terraform plan
#   terraform apply
# =============================================================================

export CC_URL="https://10.x.x.x"
export CC_USERNAME="admin"
export CC_PASSWORD="your_password_here"
export CC_INSECURE="true"  # Set to "false" to enable SSL verification

echo "✅ Catalyst Center environment configured:"
echo "   URL: $CC_URL"
echo "   User: $CC_USERNAME"

