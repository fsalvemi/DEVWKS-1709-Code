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

**Lines of Code**: ~487 (vs ~164 for NAC module)

## 🚀 Quick Start

### 1. Configure Credentials

Copy the example configuration file and update with your Catalyst Center credentials:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your environment details:

```hcl
catalyst_center_url      = "https://10.x.x.x"
catalyst_center_username = "admin"
catalyst_center_password = "your_password"
catalyst_center_insecure = true
```

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
- Provider expects: `ip_subnet` (with CIDR like `10.201.0.0/16`)
- API/Documentation uses: `ip_pool_cidr`
- Reality: You must memorize exact provider schema differences

### 2. **You need to discover and configure Required Attributes**
For `catalystcenter_floor`, you must provide non-obvious attributes:
- `rf_model` - Radio Frequency model (not obvious)
- `width` - Floor width in feet/meters
- `height` - Floor height
- `length` - Floor length

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

### 5. **Manual Dependency Management**
Every resource requires explicit `depends_on` declarations (25+ in this example) to ensure proper creation order.

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
# 1. Create the building
resource "catalystcenter_building" "new_tech_hub" {
  name        = "New Tech Hub"
  parent_name = "Global/United States/Golden Hills Campus"
  address     = "123 Market St, San Francisco, CA 94103"
  latitude    = 37.774
  longitude   = -122.419
  country     = "United States"
  depends_on  = [catalystcenter_area.golden_hills_campus]
}

# 2. Create the floor with all required attributes
resource "catalystcenter_floor" "new_tech_hub_floor_1" {
  name         = "Floor 1"
  parent_name  = "Global/United States/Golden Hills Campus/New Tech Hub"
  floor_number = 1
  rf_model     = "Cubes And Walled Offices"  # Required but not obvious
  width        = 100.0                        # Required but not obvious
  height       = 10.0                         # Required but not obvious
  length       = 100.0                        # Required but not obvious
  depends_on   = [catalystcenter_building.new_tech_hub]
}

# 3. Create IP pool reservation
resource "catalystcenter_reserve_ip_subpool" "nth_corp" {
  site_id            = catalystcenter_building.new_tech_hub.id
  name               = "NTH_CORP"
  type               = "Generic"
  ipv6_address_space = false
  ipv4_global_pool   = "10.201.0.0/16"
  ipv4_prefix        = true
  ipv4_prefix_length = 24
  ipv4_subnet        = "10.201.5.0"
  depends_on         = [catalystcenter_ip_pool.us_corp]
}
```

**Lines Added**: 34 lines of HCL
**Dependencies**: 3 manual `depends_on` declarations
**IP Pool**: Must know exact attribute names (`ipv4_global_pool`, `ipv4_subnet`, etc.)
**Schema Knowledge**: Critical - must know `rf_model`, dimensions, and exact IP pool attributes

### **Summary**:
- **NAC**: 12 lines, intuitive, no dependencies to manage
- **Native Terraform**: 34 lines (3x more), requires schema knowledge, manual dependency tracking

## 🔍 Real-World Development Experience

This implementation required **5 debugging iterations** to fix:
1. Missing CIDR notation on `ip_subnet` (needed `/16`)
2. Gateway and DHCP server IP conflicts
3. Missing floor attributes (`rf_model`, `width`, `height`, `length`)
4. Case sensitivity issues (`Generic` vs `generic`)
5. Missing `ipv4_global_pool` on reservations

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

**Native Terraform (HCL)** - Verbose, imperative:
```hcl
resource "catalystcenter_building" "sunset_tower" {
  name        = "Sunset Tower"
  parent_name = "Global/United States/Golden Hills Campus"
  address     = "8358 Sunset Blvd, Los Angeles, CA 90069"
  latitude    = 34.099
  longitude   = -118.366
  country     = "United States"
  depends_on  = [catalystcenter_area.golden_hills_campus]
}

resource "catalystcenter_floor" "sunset_tower_floor_1" {
  name         = "FLOOR_1"
  parent_name  = "Global/United States/Golden Hills Campus/Sunset Tower"
  floor_number = 1
  rf_model     = "Cubes And Walled Offices"  # Required, not obvious
  width        = 100                          # Required, not obvious
  height       = 10                           # Required, not obvious
  length       = 100                          # Required, not obvious
  depends_on   = [catalystcenter_building.sunset_tower]
}
```

## 🎓 Key Takeaways

This working example demonstrates why native implementations are challenging:

1. **More verbose** - 3x more code (487 vs 164 lines)
2. **Requires deep knowledge** - Must know exact provider schema
3. **Error-prone** - Took 5 iterations to get working
4. **Maintenance burden** - Schema changes require code updates
5. **Manual dependencies** - 25+ explicit `depends_on` declarations
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

This folder contains a **fully working implementation** that demonstrates real-world complexity. While it successfully deploys all 35 resources, it required significant debugging and deep schema knowledge. The NAC module approach achieves the same result with 3x less code, automatic dependency management, and worked on the first try.

## 📚 Learning Path

**[← Back to Main README](README.md)** to continue your learning