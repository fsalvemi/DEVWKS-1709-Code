# Native API Implementation - Simple Example

This folder demonstrates how to configure Cisco Catalyst Center using **direct REST API calls** with Python. This approach gives you full control over API interactions but requires more code and deeper knowledge of the API structure.

## 🎯 What This Example Does

Deploys a complete network infrastructure to Catalyst Center using native REST API calls:

- **5 Areas**: United States, Golden Hills Campus, Lakefront Tower, Oceanfront Mansion, Desert Oasis Branch
- **4 Buildings**: Sunset Tower, Windy City Plaza, Art Deco Mansion, Desert Oasis Tower
- **6 Floors**: Multiple floors across different buildings
- **4 Global IP Pools**: US_CORP (10.201.0.0/16), US_TECH (10.202.0.0/16), US_GUEST (10.203.0.0/16), US_BYOD (10.204.0.0/16)
- **16 IP Pool Reservations**: 4 reservations per building (CORP, TECH, GUEST, BYOD)

**Total Resources Created**: 35

## 📁 File Structure

```
native-api-simple-example/
├── native_api_simple.py     # Main script with create/delete/status commands
├── CC_Env_dCloud.yml        # Environment config for dCloud lab (pre-configured)
├── CC_Env_Sample.yml        # Template for your own environment
├── requirements.txt         # Python dependencies
└── venv/                    # Python virtual environment
```

## 🔐 Environment Configuration

The script reads Catalyst Center credentials from a YAML configuration file.

| File | Purpose |
|------|---------|
| `CC_Env_dCloud.yml` | **Lab-ready** - Pre-configured for dCloud environment |
| `CC_Env_Sample.yml` | **Template** - Copy and customize for your own Catalyst Center |

### Configuration File Format

```yaml
CC_IP: 198.18.129.100
CC_USERNAME: admin
CC_PASSWORD: C1sco12345
CC_INSECURE: true
```

## 🚀 Quick Start

### 1. Set Up Python Environment

```bash
cd native-api-simple-example

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Check Initial Status (Before Deployment)

Verify that Catalyst Center has no sites or IP pools configured:

```bash
python native_api_simple.py status --config CC_Env_dCloud.yml
```

**Expected Output**: No sites (except Global) and no IP pools should be listed.

You can also verify in the Catalyst Center GUI:
- Navigate to **Design > Network Hierarchy** - Only "Global" should exist
- Navigate to **Design > Network Settings > IP Address Pools** - Should be empty

### 3. Create Infrastructure

Deploy all sites, buildings, floors, and IP pools:

```bash
python native_api_simple.py create --config CC_Env_dCloud.yml
```

**Expected Output**: 
- ✅ 4 Global IP Pools created
- ✅ 5 Areas created
- ✅ 4 Buildings created
- ✅ 6 Floors created
- ✅ 16 IP Pool Reservations created

### 4. Verify Deployment

Check that all resources were created:

```bash
python native_api_simple.py status --config CC_Env_dCloud.yml
```

**Expected Output**: All 35 resources should be listed.

Verify in the Catalyst Center GUI:
- Navigate to **Design > Network Hierarchy** - Verify the site hierarchy exists
- Navigate to **Design > Network Settings > IP Address Pools** - Verify 4 global pools and 16 reservations

### 5. Delete Infrastructure

Remove all created resources:

```bash
python native_api_simple.py delete --config CC_Env_dCloud.yml --force
```

> **Note**: The `--force` flag skips the confirmation prompt.

**Expected Output**: All resources deleted in reverse order (reservations → floors → buildings → areas → pools).

### 6. Verify Cleanup

Confirm all resources have been removed:

```bash
python native_api_simple.py status --config CC_Env_dCloud.yml
```

**Expected Output**: No sites (except Global) and no IP pools.

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `python native_api_simple.py status --config <file>` | Show current sites and IP pools |
| `python native_api_simple.py create --config <file>` | Create all infrastructure |
| `python native_api_simple.py delete --config <file>` | Delete all infrastructure (with confirmation) |
| `python native_api_simple.py delete --config <file> --force` | Delete without confirmation |

## ⚠️ Complexity Challenges

This native API implementation demonstrates several challenges:

### 1. **API Endpoint Discovery**
You must know the exact API endpoints for each operation:
- Sites: `/dna/intent/api/v1/site`
- IP Pools: `/api/v2/ippool`
- Reservations: `/dna/intent/api/v1/reserve-ip-subpool`

### 2. **Payload Structure Knowledge**
Each API requires a specific JSON payload structure that must be discovered from documentation or experimentation.

### 3. **Task Monitoring**
Most operations are asynchronous and require polling task endpoints to confirm completion.

### 4. **Error Handling**
Must implement retry logic, token refresh, and error parsing for each API call.

### 5. **Dependency Management**
Must create resources in the correct order (areas before buildings, buildings before floors, etc.).

## 📊 Comparison with NAC Module

| Aspect | Native API | NAC Module |
|--------|-----------|------------|
| **Lines of Code** | ~1200 lines Python | ~164 lines YAML |
| **API Knowledge** | Required | Not required |
| **Error Handling** | Manual implementation | Built-in |
| **Dependencies** | Manual ordering | Automatic |
| **Maintenance** | High (API changes break code) | Low (module handles changes) |

## 🔗 Related Examples

- **NAC Module Approach**: `../nac-catalystcenter-simple-example/`
- **Native Terraform Approach**: `../native-terraform-simple-example/`

## Suggested Learning Path

Follow the [Lab Guide](https://fsalvemi.github.io/DEVWKS-1709-Lab-Guide/)
