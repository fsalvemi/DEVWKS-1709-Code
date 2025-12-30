# NAC Module - Simple Example

This folder demonstrates how to configure Cisco Catalyst Center using the **Network-as-Code (NAC) Module** with YAML-based declarative configuration. This approach simplifies infrastructure deployment by separating data from code.

## 🎯 What This Example Does

Deploys a complete network infrastructure to Catalyst Center using simple YAML files:

- **5 Areas**: United States, Golden Hills Campus, Lakefront Tower, Oceanfront Mansion, Desert Oasis Branch
- **4 Buildings**: Sunset Tower, Windy City Plaza, Art Deco Mansion, Desert Oasis Tower
- **6 Floors**: Multiple floors across different buildings
- **4 Global IP Pools**: US_CORP (10.201.0.0/16), US_TECH (10.202.0.0/16), US_GUEST (10.203.0.0/16), US_BYOD (10.204.0.0/16)
- **16 IP Pool Reservations**: 4 reservations per building (CORP, TECH, GUEST, BYOD)

**Total Resources Created**: 35

## 📁 File Structure

```
nac-catalystcenter-simple-example/
├── main.tf                  # Terraform config using NAC module (~22 lines)
├── CC_Env_dCloud.sh         # Environment config for dCloud lab (pre-configured)
├── CC_Env_Sample.sh         # Template for your own environment
├── data/
│   ├── sites.nac.yaml       # Site hierarchy (areas, buildings, floors)
│   └── ip_pools.nac.yaml    # IP pools and reservations
└── reference_configs/
    ├── initial_config/      # Base US-only configuration
    └── final_config/        # Complete configuration with Rome
```

## 🔐 Environment Configuration

The Catalyst Center Terraform provider reads credentials from environment variables. Shell scripts are provided to set these:

| File | Purpose |
|------|---------|
| `CC_Env_dCloud.sh` | **Lab-ready** - Pre-configured for dCloud environment |
| `CC_Env_Sample.sh` | **Template** - Copy and customize for your own Catalyst Center |

### Environment Variables Set

```bash
export CC_URL="https://198.18.129.100"
export CC_USERNAME="admin"
export CC_PASSWORD="C1sco12345"
export CC_INSECURE="true"
```

## 🚀 Quick Start

### 1. Configure Environment

```bash
cd nac-catalystcenter-simple-example

# Source the environment file (pre-configured for lab)
source CC_Env_dCloud.sh
```

### 2. Check Initial Status (Before Deployment)

Verify that Catalyst Center has no sites or IP pools configured:

**Via Catalyst Center GUI:**
- Navigate to **Design > Network Hierarchy** - Only "Global" should exist
- Navigate to **Design > Network Settings > IP Address Pools** - Should be empty

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Review Planned Changes

```bash
terraform plan
```

**Expected Output**: Plan to create 35 resources (areas, buildings, floors, IP pools, reservations).

### 5. Create Infrastructure

Deploy all sites, buildings, floors, and IP pools:

```bash
terraform apply
```

Type `yes` when prompted to confirm.

**Expected Output**: 
- ✅ All 35 resources created successfully

### 6. Verify Deployment

**Via Catalyst Center GUI:**
- Navigate to **Design > Network Hierarchy** - Verify the complete site hierarchy
- Navigate to **Design > Network Settings > IP Address Pools** - Verify 4 global pools and 16 reservations

**Via Terraform:**
```bash
terraform state list
```

---

## 🔄 Exercise: Adding New Sites and IP Pools

Now let's expand the infrastructure by adding a European office in Rome. This exercise demonstrates how easy it is to add new resources with the NAC module approach.

### 7. Add European Site Hierarchy

Edit `data/sites.nac.yaml` and add the following at the end of the `areas` section:

```yaml
      # NEW: European area hierarchy
      - name: Europe
        parent_name: Global
      - name: Italy
        parent_name: Global/Europe
      - name: Rome
        parent_name: Global/Europe/Italy
```

### 8. Add Rome Office Building

Edit `data/sites.nac.yaml` and add the following at the end of the `buildings` section:

```yaml
      # NEW: Rome office building
      - name: Rome Office
        latitude: 41.832002
        longitude: 12.491654
        address: Via Del Serafico 200, 00142 Roma Rome, Italy
        country: Italy
        parent_name: Global/Europe/Italy/Rome
        ip_pools_reservations:
          - ROM_CORP
```

### 9. Add Rome Office Floor

Edit `data/sites.nac.yaml` and add the following at the end of the `floors` section:

```yaml
      # NEW: Floor for Rome office
      - name: FLOOR_1
        floor_number: 1
        parent_name: Global/Europe/Italy/Rome/Rome Office
```

### 10. Add European IP Pool

Edit `data/ip_pools.nac.yaml` and add the following at the end of the `ip_pools` section:

```yaml
      # NEW: European corporate IP pool
      - name: EU_CORP
        ip_address_space: IPv4
        ip_pool_cidr: 10.205.0.0/16
        dns_servers:
          - 10.205.0.1
        dhcp_servers:
          - 10.205.0.1
        ip_pools_reservations:
          - name: ROM_CORP
            prefix_length: 24
            subnet: 10.205.1.0
```

### 11. Deploy the Changes

Review and apply the new configuration:

```bash
terraform plan
terraform apply
```

**Expected Output**: 
- ✅ 7 new resources added (3 areas, 1 building, 1 floor, 1 IP pool, 1 reservation)
- Total resources: 42

### 12. Verify the New Resources

**Via Catalyst Center GUI:**
- Navigate to **Design > Network Hierarchy** - Verify **Europe > Italy > Rome > Rome Office** hierarchy
- Navigate to **Design > Network Settings > IP Address Pools** - Verify **EU_CORP** pool with **ROM_CORP** reservation

### 13. Validate Your Configuration

Your files should now match the reference configuration:

```bash
diff data/sites.nac.yaml reference_configs/final_config/sites.nac.yaml
diff data/ip_pools.nac.yaml reference_configs/final_config/ip_pools.nac.yaml
```

If there are no differences, you've successfully completed the exercise!

---

### 14. Delete Infrastructure

Remove all created resources:

```bash
terraform destroy
```

Type `yes` when prompted to confirm.

**Expected Output**: All 42 resources destroyed.

### 15. Verify Cleanup

**Via Catalyst Center GUI:**
- Navigate to **Design > Network Hierarchy** - Only "Global" should remain
- Navigate to **Design > Network Settings > IP Address Pools** - Should be empty

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `source CC_Env_dCloud.sh` | Set environment variables for Catalyst Center |
| `terraform init` | Initialize Terraform and download providers/modules |
| `terraform plan` | Preview changes before applying |
| `terraform apply` | Create/update infrastructure |
| `terraform destroy` | Remove all infrastructure |
| `terraform state list` | List all managed resources |

## ✅ Key Benefits

This NAC module approach offers significant advantages:

### 1. **Simple YAML Configuration**
Human-readable configuration that mirrors your network hierarchy:
```yaml
buildings:
  - name: Sunset Tower
    parent_name: Global/United States/Golden Hills Campus
    ip_pools_reservations:
      - ST_CORP
```

### 2. **Automatic Dependencies**
The module handles resource creation order automatically - no need to specify dependencies.

### 3. **Data Model Validation**
The `.nac.yaml` suffix enables schema validation and IntelliSense in VS Code.

### 4. **Minimal Code**
Only ~22 lines of Terraform code vs 400+ lines for native Terraform approach.

### 5. **Version Stability**
NAC module abstracts provider changes - upgrading is typically seamless.

## 📊 Comparison with Other Approaches

| Aspect | NAC Module | Native Terraform | Native API |
|--------|-----------|-----------------|------------|
| **Lines of Code** | ~164 lines YAML | ~464 lines HCL | ~1200 lines Python |
| **Schema Knowledge** | Not required | Required | Required |
| **Error Handling** | Built-in | Manual | Manual |
| **Dependencies** | Automatic | ID-based references | Manual ordering |
| **Maintenance** | Low | High | High |

## 🔗 Related Examples

- **Native Terraform Approach**: `../native-terraform-simple-example/`
- **Native API Approach**: `../native-api-simple-example/`
- **Comprehensive NAC Example**: `../nac-catalystcenter-comprehensive-example/`

## 📚 Resources

- **NAC Module**: [terraform-catalystcenter-nac-catalystcenter](https://registry.terraform.io/modules/netascode/nac-catalystcenter/catalystcenter/latest)
- **Module Documentation**: [GitHub Repository](https://github.com/netascode/terraform-catalystcenter-nac-catalystcenter)
- **Data Model Documentation**: [netascode.cisco.com](https://netascode.cisco.com/)

## Suggested Learning Path

Follow the [Lab Guide](https://fsalvemi.github.io/DEVWKS-1709-Lab-Guide/)

