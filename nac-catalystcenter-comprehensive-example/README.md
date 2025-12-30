# NAC Module - Comprehensive Example

This folder demonstrates a **full SD-Access fabric deployment** using the Network-as-Code (NAC) Module. Unlike the simple example, this configuration includes fabric sites, virtual networks, border devices, edge nodes, and network profiles.

## 🎯 What This Example Does

Deploys a complete SD-Access fabric infrastructure to Catalyst Center:

### Site Hierarchy
- **1 Area**: Poland → Krakow
- **1 Building**: Bld A
- **2 Floors**: FLOOR_1, FLOOR_2

### Network Settings
- **1 Global IP Pool**: Overlay (192.168.0.0/16)
- **4 IP Pool Reservations**: CampusVN, GuestVN, PrintersVN, BYOD
- **1 AAA Server Configuration**: ISE integration

### SD-Access Fabric
- **4 Virtual Networks (VNs)**: Campus, Guest, Printers, BYOD
- **1 IP Transit**: BGP65002
- **1 Fabric Site**: Krakow with anycast gateways
- **4 Anycast Gateways**: One per VN

### Devices
- **1 Border Router**: BR10 (Control Plane + Border Node)
- **2 Edge Nodes**: EDGE01, EDGE02 with port assignments

### Templates & Profiles
- **1 Day-N Template**: ACL_Block
- **1 Network Profile**: VirtualCat9k

## 📁 File Structure

```
nac-catalystcenter-comprehensive-example/
├── main.tf                      # Terraform config using NAC module
├── CC_Env_dCloud.sh             # Environment config for dCloud lab
├── CC_Env_Sample.sh             # Template for your own environment
└── data/
    ├── sites.nac.yaml           # Site hierarchy and IP pool reservations
    ├── network_settings.nac.yaml # AAA servers and IP pools
    ├── fabric.nac.yaml          # VNs, fabric sites, border devices
    ├── devices.nac.yaml         # Device inventory and fabric roles
    ├── network_profiles.nac.yaml # Switching profiles
    ├── templates.nac.yaml       # Day-N template definitions
    └── templates/
        └── ACL_Block.j2         # Jinja2 template for ACL configuration
```

## 🔐 Environment Configuration

The Catalyst Center Terraform provider reads credentials from environment variables:

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
cd nac-catalystcenter-comprehensive-example

# Source the environment file (pre-configured for lab)
source CC_Env_dCloud.sh
```

### 2. Check Initial Status (Before Deployment)

**Via Catalyst Center GUI:**
- Navigate to **Design > Network Hierarchy** - Only "Global" should exist
- Navigate to **Provision > Fabric Sites** - No fabric sites configured
- Navigate to **Provision > Inventory** - Devices should be in "Unassigned" state

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Review Planned Changes

```bash
terraform plan
```

**Expected Output**: Plan to create multiple resources including sites, IP pools, fabric configuration, and device provisioning.

### 5. Create Infrastructure

Deploy the complete SD-Access fabric:

```bash
terraform apply
```

Type `yes` when prompted to confirm.

> **Note**: This deployment takes longer than the simple example due to fabric provisioning and device configuration.

**Expected Output**: 
- ✅ Site hierarchy created
- ✅ IP pools and reservations configured
- ✅ AAA settings applied
- ✅ Virtual networks created
- ✅ Fabric site configured with anycast gateways
- ✅ Devices provisioned with fabric roles

### 6. Verify Deployment

**Via Catalyst Center GUI:**

1. **Site Hierarchy**: Navigate to **Design > Network Hierarchy**
   - Verify Poland → Krakow → Bld A hierarchy

2. **IP Pools**: Navigate to **Design > Network Settings > IP Address Pools**
   - Verify Overlay pool and 4 reservations

3. **Fabric Sites**: Navigate to **Provision > Fabric Sites**
   - Verify Krakow fabric site exists
   - Check Virtual Networks (Campus, Guest, Printers, BYOD)

4. **Devices**: Navigate to **Provision > Inventory**
   - At this stage, devices are still in `INIT` state
   - Devices are **not yet assigned to a site or provisioned** - this is expected
   - We will provision devices in the next exercise

---

## 🔄 Exercise: Device Provisioning

The devices in `data/devices.nac.yaml` are configured with `state: INIT`, which means the fabric infrastructure is created but **devices are not yet provisioned**. This allows you to verify the fabric configuration before provisioning devices.

### 7. Provision Border Router (BR10)

Edit `data/devices.nac.yaml` and change the BR10 device state from `INIT` to `PROVISIONED`:

```yaml
    devices:
      - name: BR10
        fqdn_name: BR10.cisco.eu
        device_ip: 198.18.130.10
        pid: C9KV-UADP-8P
        state: PROVISIONED    # Changed from INIT
        device_role: BORDER ROUTER
        # ... rest of configuration
```

Apply the change:

```bash
terraform apply
```

**Verify in Catalyst Center GUI:**
- Navigate to **Provision > Inventory**
- Verify BR10 shows as "Provisioned" with Border/Control Plane roles

### 8. Provision Edge Nodes (EDGE01, EDGE02)

Edit `data/devices.nac.yaml` and change both edge devices from `INIT` to `PROVISIONED`:

```yaml
      - name: EDGE01
        # ...
        state: PROVISIONED    # Changed from INIT
        # ...

      - name: EDGE02
        # ...
        state: PROVISIONED    # Changed from INIT
        # ...
```

Apply the change:

```bash
terraform apply
```

**Verify in Catalyst Center GUI:**
- Navigate to **Provision > Inventory**
- Verify EDGE01 and EDGE02 show as "Provisioned" with Edge Node roles
- Check port assignments are configured correctly

---

### 9. Delete Infrastructure

Remove all created resources:

```bash
terraform destroy
```

Type `yes` when prompted to confirm.

> **Note**: Fabric teardown may take several minutes.

### 10. Verify Cleanup

**Via Catalyst Center GUI:**
- Navigate to **Design > Network Hierarchy** - Only "Global" should remain
- Navigate to **Provision > Fabric Sites** - No fabric sites
- Navigate to **Provision > Inventory** - Devices unassigned

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `source CC_Env_dCloud.sh` | Set environment variables for Catalyst Center |
| `terraform init` | Initialize Terraform and download providers/modules |
| `terraform plan` | Preview changes before applying |
| `terraform apply` | Create/update infrastructure |
| `terraform destroy` | Remove all infrastructure |
| `terraform state list` | List all managed resources |

## 📊 YAML Configuration Files

### sites.nac.yaml
Defines the site hierarchy with areas, buildings, and floors. Also includes IP pool reservation assignments per site.

### network_settings.nac.yaml
Configures AAA server settings (ISE) and IP pools with reservations including gateway, DNS, and DHCP servers.

### fabric.nac.yaml
Defines the SD-Access fabric configuration:
- L3 Virtual Networks
- IP Transit settings
- Fabric site with authentication and VN assignments
- Anycast gateway configurations
- Border device L3 handoff settings

### devices.nac.yaml
Specifies device inventory including:
- Device IP addresses and roles
- Site and fabric site assignments
- Fabric roles (Border, Control Plane, Edge)
- Port assignments for edge nodes

### templates.nac.yaml & network_profiles.nac.yaml
Day-N templates and network profiles for device configuration automation.

## ✅ Key Benefits

### 1. **Complete Fabric Deployment**
Deploy an entire SD-Access fabric from YAML configuration files.

### 2. **Declarative Approach**
Define the desired state - the module handles the complex API orchestration.

### 3. **Bulk API Support**
Uses `use_bulk_api = true` for optimized deployment performance. Instead of making individual API calls for each resource, the bulk API batches multiple operations into a single request, significantly reducing deployment time for large configurations.

> **Learn More**: [NAC Module Variables](https://github.com/netascode/terraform-catalystcenter-nac-catalystcenter#inputs) | [Catalyst Center Bulk APIs](https://developer.cisco.com/docs/dna-center/)

### 4. **Template Integration**
Supports Jinja2 templates for Day-N device configurations.

## 🔗 Related Examples

- **Simple NAC Example**: `../nac-catalystcenter-simple-example/`
- **Native Terraform Approach**: `../native-terraform-simple-example/`
- **Native API Approach**: `../native-api-simple-example/`

## 📚 Resources

- **NAC Module**: [terraform-catalystcenter-nac-catalystcenter](https://registry.terraform.io/modules/netascode/nac-catalystcenter/catalystcenter/latest)
- **Data Model Documentation**: [netascode.cisco.com](https://netascode.cisco.com/)
- **Fabric Configuration**: [Fabric Data Model](https://netascode.cisco.com/docs/data_models/catalyst_center/fabric/)

## Suggested Learning Path

Follow the [Lab Guide](https://fsalvemi.github.io/DEVWKS-1709-Lab-Guide/)

