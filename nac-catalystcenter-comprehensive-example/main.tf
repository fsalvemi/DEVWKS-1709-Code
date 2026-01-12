terraform {
  required_providers {
    catalystcenter = {
      source  = "CiscoDevNet/catalystcenter"
      version = "0.4.6"
    }
  }
}

# Credentials are read from environment variables:
# CC_URL, CC_USERNAME, CC_PASSWORD, CC_INSECURE
# Source the environment file before running: source CC_Env_dCloud.sh
provider "catalystcenter" {
  # Environment variables are automatically used
}

module "catalyst_center" {
  source  = "netascode/nac-catalystcenter/catalystcenter"
  version = "0.3.0"

  yaml_directories      = ["data/"]
  templates_directories = ["data/templates/"]

  use_bulk_api = true
}