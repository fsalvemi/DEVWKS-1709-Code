# =============================================================================
# Catalyst Center Provider Variables
# =============================================================================

variable "catalyst_center_url" {
  description = "URL of the Catalyst Center instance (e.g., https://10.x.x.x)"
  type        = string
}

variable "catalyst_center_username" {
  description = "Username for Catalyst Center authentication"
  type        = string
}

variable "catalyst_center_password" {
  description = "Password for Catalyst Center authentication"
  type        = string
  sensitive   = true
}

variable "catalyst_center_insecure" {
  description = "Skip SSL certificate verification (set to true for self-signed certs)"
  type        = bool
  default     = true
}

variable "max_timeout" {
  description = "Maximum timeout in seconds for API operations"
  type        = number
  default     = 600
}

