# Native Terraform Implementation - Complexity Demonstration

This folder contains a native Terraform HCL implementation that demonstrates the complexity challenges when working directly with the Catalyst Center provider without an abstraction layer like the NAC module.

## 🎯 What This Example Does

This is a **fully working** implementation that deploys the same network infrastructure as the NAC example:
- **5 Areas**: United States, Golden Hills Campus, Lakefront Tower, Oceanfront Mansion, Desert Oasis Branch
- **4 Buildings**: Sunset Tower, Windy City Plaza, Art Deco Mansion, Desert Oasis Tower  
- **6 Floors**: Multiple floors across different buildings
- **4 Global IP Pools**: US_CORP (10.201.0.0/16), US_TECH (10.202.0.0/16), US_GUEST (10.203.0.0/16), US_BYOD (10.204.0.0/16)
- **16 IP Pool Reservations**: 4 reservations per building (CORP, TECH, GUEST, BYOD)

**Total Resources Created**: 35

**Lines of Code**: ~464 

## 🚀 Quick Start

### 1. Credentials (Pre-configured for Lab)

The `terraform.tfvars` file is **already configured** for the lab environment - no changes required!

```hcl
# terraform.tfvars (pre-configured)
catalyst_center_url      = "https://198.18.129.100"
catalyst_center_username = "admin"
catalyst_center_password = "C1sco12345"
catalyst_center_insecure = true
```

> **Note:** This file externalizes the Catalyst Center credentials as Terraform variables, keeping the main configuration (`main.tf`) clean and reusable. For different environments, simply update this file with your target Catalyst Center details.

### 2. Initialize and Deploy

```bash
terraform init    # Download provider
terraform plan    # Review changes
terraform apply   # Deploy to Catalyst Center
```

### 3. Destroy (Cleanup)

```bash
terraform destroy  # Remove all created resources
```

## 📁 Configuration Files

| File | Purpose |
|------|---------|
| `main.tf` | Infrastructure resources (sites, pools, reservations) |
| `variables.tf` | Variable definitions with descriptions and defaults |
| `terraform.tfvars` | **Lab credentials** - pre-configured, no changes needed |
| `terraform.tfvars.example` | Template for other environments |

## ⚠️ Security Note for Production

This lab example includes `terraform.tfvars` for convenience. In production environments:

- **Do NOT commit `terraform.tfvars` with real credentials to version control**
- Add `*.tfvars` to `.gitignore`
- Use environment variables: `TF_VAR_catalyst_center_password`
- Use HashiCorp Vault or other secrets management solutions
- Use Terraform Cloud/Enterprise with secure variable storage

## ⚠️ Complexity Challenges

While this implementation works, it demonstrates several challenges:

### 1. **You need to discover how API objects are mapped to TF Attribute Names**
- Provider expects: `address_space_subnet` + `address_space_prefix_length` (separate fields)
- API/Documentation uses: `ip_pool_cidr` (combined CIDR notation)
- Reality: You must memorize exact provider schema differences

### 2. **You need to discover and configure Required Attributes**
For `catalystcenter_floor`, you must provide non-obvious attributes:
- `rf_model` - Radio Frequency model (not obvious)
- `width` - Floor width in feet/meters
- `height` - Floor height
- `length` - Floor length
- `units_of_measure` - Must specify "feet" or "meters"

These aren't intuitive without extensive documentation review.

### 3. **No Abstraction Layer**
- Every attribute must be explicitly specified
- No sensible defaults
- No simplified patterns for common configurations

### 4. **Schema Discovery Required**
To understand the required attributes, you need to:
```bash
terraform providers schema -json | jq '.provider_schemas."registry.terraform.io/ciscodevnet/catalystcenter".resource_schemas'
```

Then manually match each attribute to the correct name and type.

### 5. **ID-Based References Required**
Resources require `parent_id` instead of human-readable `parent_name`. You must use resource references (e.g., `parent_id = catalystcenter_area.united_states.id`) or data sources to look up IDs, adding complexity compared to simple name-based references.

## 📝 Adding a New Site - Complexity Comparison

To demonstrate the complexity difference, let's add a new building with a floor to both approaches.

### **NAC Module Approach** - Add to `data/sites.nac.yaml`:

```yaml
buildings:
  - name: New Tech Hub
    latitude: 37.774
    longitude: -122.419
    address: 123 Market St, San Francisco, CA 94103
    country: United States
    parent_name: Global/United States/Golden Hills Campus
    ip_pools_reservations:
      - NTH_CORP

floors:
  - name: Floor 1
    parent_name: Global/United States/Golden Hills Campus/New Tech Hub
    floor_number: 1
```

**Lines Added**: 12 lines of simple, readable YAML
**Dependencies**: Automatic
**IP Pool**: Just reference by name
**Schema Knowledge**: Not required

### **Native Terraform Approach** - Add to `main.tf`:

```hcl
# 1. Create the building (requires parent_id, not parent_name)
resource "catalystcenter_building" "new_tech_hub" {
  name      = "New Tech Hub"
  parent_id = catalystcenter_area.golden_hills_campus.id  # Must use ID reference
  address   = "123 Market St, San Francisco, CA 94103"
  latitude  = 37.774
  longitude = -122.419
  country   = "United States"
}

# 2. Create the floor with all required attributes
resource "catalystcenter_floor" "new_tech_hub_floor_1" {
  name             = "Floor 1"
  parent_id        = catalystcenter_building.new_tech_hub.id  # Must use ID reference
  floor_number     = 1
  rf_model         = "Cubes And Walled Offices"  # Required but not obvious
  width            = 100                          # Required but not obvious
  height           = 10                           # Required but not obvious
  length           = 100                          # Required but not obvious
  units_of_measure = "feet"                       # Required in 0.4.5
}

# 3. Create IP pool reservation (requires pool ID, not CIDR string)
resource "catalystcenter_ip_pool_reservation" "nth_corp" {
  site_id             = catalystcenter_building.new_tech_hub.id
  name                = "NTH_CORP"
  pool_type           = "Generic"
  ipv4_global_pool_id = catalystcenter_ip_pool.us_corp.id  # Must use pool ID
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.201.5.0"
  ipv4_dhcp_servers   = ["10.201.0.2"]
  ipv4_dns_servers    = ["10.201.0.2"]
  ipv4_gateway        = "10.201.5.1"
}
```

**Lines Added**: 35 lines of HCL
**ID References**: Must use resource IDs instead of human-readable names
**IP Pool**: Must know exact attribute names (`ipv4_global_pool_id`, `ipv4_subnet`, etc.)
**Schema Knowledge**: Critical - must know `rf_model`, dimensions, `units_of_measure`, and exact IP pool attributes

### **Summary**:
- **NAC**: 12 lines, intuitive, uses human-readable names
- **Native Terraform**: 35 lines (3x more), requires schema knowledge, ID-based references

## 🔍 Real-World Development Experience

This implementation required **multiple debugging iterations** to fix:
1. Schema changes between provider versions (0.3.3 → 0.4.5 required complete rewrite)
2. `parent_name` replaced with `parent_id` requiring ID lookups/references
3. `ip_subnet` split into `address_space_subnet` + `address_space_prefix_length`
4. Missing floor attribute `units_of_measure` (new requirement in 0.4.5)
5. `ipv4_global_pool` (CIDR string) replaced with `ipv4_global_pool_id` (UUID reference)

**Development Time**: 30-45 minutes for someone familiar with the provider
**NAC Module Time**: 5 minutes - worked on first try

## 📊 Comparison with NAC Module

**NAC Module (YAML)** - Simple, declarative:
```yaml
buildings:
  - name: Sunset Tower
    latitude: 34.099
    longitude: -118.366
    address: 8358 Sunset Blvd, Los Angeles, CA 90069
    parent_name: Global/United States/Golden Hills Campus
```

**Native Terraform (HCL)** - Verbose, ID-based references:
```hcl
resource "catalystcenter_building" "sunset_tower" {
  name      = "Sunset Tower"
  parent_id = catalystcenter_area.golden_hills_campus.id  # ID reference required
  address   = "8358 Sunset Blvd, Los Angeles, CA 90069"
  latitude  = 34.099
  longitude = -118.366
  country   = "United States"
}

resource "catalystcenter_floor" "sunset_tower_floor_1" {
  name             = "FLOOR_1"
  parent_id        = catalystcenter_building.sunset_tower.id  # ID reference required
  floor_number     = 1
  rf_model         = "Cubes And Walled Offices"  # Required, not obvious
  width            = 100                          # Required, not obvious
  height           = 10                           # Required, not obvious
  length           = 100                          # Required, not obvious
  units_of_measure = "feet"                       # Required in 0.4.5
}
```

## 🎓 Key Takeaways

This working example demonstrates why native implementations are challenging:

1. **More verbose** - 3x more code (464 vs 164 lines)
2. **Requires deep knowledge** - Must know exact provider schema
3. **Breaking changes** - Provider version upgrades may require complete rewrites
4. **Maintenance burden** - Schema changes require code updates
5. **ID-based references** - Must use resource IDs instead of human-readable names
6. **No guardrails** - Errors only discovered at runtime

## 🔗 For Comparison

See the working NAC module implementation:
```
../nac-catalystcenter-simple-example/
```

Review the full comparison in the repository root:
```
../README.md
```

---

## Conclusion

This folder contains a **fully working implementation** using Catalyst Center Terraform provider v0.4.5 that demonstrates real-world complexity. While it successfully deploys all 35 resources, it required significant debugging, deep schema knowledge, and a complete rewrite when upgrading from provider v0.3.3. The NAC module approach achieves the same result with 3x less code, human-readable names, and automatic dependency management.

## 📚 Learning Path

**[← Back to Main README](README.md)** to continue your learning