# DEVWKS-1709: Catalyst Center API Automation

Repository for DEVWKS-1709 workshop code and examples demonstrating infrastructure automation with Cisco Catalyst Center APIs.

---

## Lab Summary

This lab demonstrates how to **create and manage network infrastructure objects in Cisco Catalyst Center via API**. You will learn to automate the provisioning of:

- Site hierarchy (Areas, Buildings, Floors)
- Global IP Address Pools
- IP Pool Reservations (subpools assigned to buildings)

By the end of this lab, you will understand how to use Python and the Catalyst Center REST API to programmatically deploy network infrastructure that would otherwise require manual configuration through the GUI.

---

## What the Script Does

The `native_api_simple.py` script automates the creation and deletion of the following objects in Catalyst Center:

### Global IP Pools (4 pools)
| Pool Name | CIDR Block | Purpose |
|-----------|------------|---------|
| US_CORP | 10.201.0.0/16 | Corporate network |
| US_TECH | 10.202.0.0/16 | Technology/Lab network |
| US_GUEST | 10.203.0.0/16 | Guest network |
| US_BYOD | 10.204.0.0/16 | BYOD network |

### Site Hierarchy
```
Global/
└── United States/
    ├── Golden Hills Campus/
    │   └── Sunset Tower (Building)
    │       ├── FLOOR_1
    │       └── FLOOR_2
    ├── Lakefront Tower/
    │   └── Windy City Plaza (Building)
    │       ├── FLOOR_1
    │       └── FLOOR_2
    ├── Oceanfront Mansion/
    │   └── Art Deco Mansion (Building)
    │       └── FLOOR_1
    └── Desert Oasis Branch/
        └── Desert Oasis Tower (Building)
            └── FLOOR_1
```

### IP Pool Reservations (16 reservations)
Each building receives 4 IP pool reservations (/24 subnets) from the global pools:
- `{PREFIX}_CORP` - Corporate subnet
- `{PREFIX}_TECH` - Technology subnet
- `{PREFIX}_GUEST` - Guest subnet
- `{PREFIX}_BYOD` - BYOD subnet

---

## How to Use the Script

### Prerequisites

1. Python 3.9+ with virtual environment
2. Access to a Cisco Catalyst Center instance
3. Valid credentials with API access

### Installation

```bash
cd native-api-simple-example

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a YAML configuration file with your Catalyst Center credentials:

```yaml
# CC_Env.yml
CC_IP: 10.x.x.x          # Catalyst Center IP address
CC_USERNAME: admin        # Username
CC_PASSWORD: your_pass    # Password
CC_INSECURE: true         # Set to true to skip SSL verification
```

### Available Commands

| Command | Description |
|---------|-------------|
| `create` | Create all infrastructure objects |
| `delete` | Delete all infrastructure objects |
| `status` | Check current state of infrastructure |

### Command Options

```bash
python native_api_simple.py <action> --config <config_file> [--force]

Arguments:
  action              create, delete, or status
  --config, -c        Path to YAML configuration file (required)
  --force, -f         Skip confirmation prompt for delete (optional)
```

### Examples

```bash
# Check current infrastructure status
python native_api_simple.py status --config CC_Env.yml

# Create all infrastructure
python native_api_simple.py create --config CC_Env.yml

# Delete all infrastructure (with confirmation)
python native_api_simple.py delete --config CC_Env.yml

# Delete all infrastructure (skip confirmation)
python native_api_simple.py delete --config CC_Env.yml --force
```

---

## Step 1: Check Initial Configuration

### Via Script

Run the status command to see what currently exists in Catalyst Center:

```bash
python native_api_simple.py status --config CC_Env.yml
```

Expected output for a clean environment:
```
📦 Global IP Pools
  ℹ️  No global pools found

🗺️  Site Hierarchy
  ℹ️  No sites found (besides Global)

🔖 IP Pool Reservations
  ℹ️  No IP pool reservations found
```

### Via Catalyst Center GUI

1. **Check Global IP Pools:**
   - Navigate to: `Design` → `Network Settings` → `IP Address Pools`
   - Verify no US_CORP, US_TECH, US_GUEST, or US_BYOD pools exist

2. **Check Site Hierarchy:**
   - Navigate to: `Design` → `Network Hierarchy`
   - Verify no "United States" area exists under Global

---

## Step 2: Create Objects and Verify

### Run the Create Command

```bash
python native_api_simple.py create --config CC_Env.yml
```

The script will:
1. ✅ Create 4 Global IP Pools
2. ✅ Create 5 Areas (United States + 4 campus areas)
3. ✅ Create 4 Buildings
4. ✅ Create 6 Floors
5. ✅ Create 16 IP Pool Reservations

### Verify via Script

```bash
python native_api_simple.py status --config CC_Env.yml
```

Expected output:
```
📦 Global IP Pools
Found 4 global pool(s):
  ✓ US_CORP: 10.201.0.0/16
  ✓ US_TECH: 10.202.0.0/16
  ✓ US_GUEST: 10.203.0.0/16
  ✓ US_BYOD: 10.204.0.0/16

🗺️  Site Hierarchy
  Areas (5): United States, Golden Hills Campus, ...
  Buildings (4): Sunset Tower, Windy City Plaza, ...
  Floors (6): FLOOR_1, FLOOR_2, ...

🔖 IP Pool Reservations
  Sunset Tower (4 reservation(s))
  Windy City Plaza (4 reservation(s))
  Art Deco Mansion (4 reservation(s))
  Desert Oasis Tower (4 reservation(s))
  Total: 16 reservation(s)
```

### Verify via Catalyst Center GUI

1. **Verify Global IP Pools:**
   - Navigate to: `Design` → `Network Settings` → `IP Address Pools`
   - Confirm 4 pools exist: US_CORP, US_TECH, US_GUEST, US_BYOD

2. **Verify Site Hierarchy:**
   - Navigate to: `Design` → `Network Hierarchy`
   - Expand `Global` → `United States`
   - Verify all 4 campus areas and their buildings/floors

3. **Verify IP Pool Reservations:**
   - Navigate to: `Design` → `Network Settings` → `IP Address Pools`
   - Select each building to view its assigned reservations

---

## Step 3: Delete Objects and Verify

### Run the Delete Command

```bash
python native_api_simple.py delete --config CC_Env.yml --force
```

The script will delete in the correct order:
1. 🗑️ IP Pool Reservations (must be deleted before pools)
2. 🗑️ Floors (must be deleted before buildings)
3. 🗑️ Buildings (must be deleted before areas)
4. 🗑️ Areas (children first, then parents)
5. 🗑️ Global IP Pools

### Verify via Script

```bash
python native_api_simple.py status --config CC_Env.yml
```

Expected output:
```
📦 Global IP Pools
  ℹ️  No global pools found

🗺️  Site Hierarchy
  (Only pre-existing sites remain)

🔖 IP Pool Reservations
  ℹ️  No IP pool reservations found
```

### Verify via Catalyst Center GUI

1. **Verify Global IP Pools Deleted:**
   - Navigate to: `Design` → `Network Settings` → `IP Address Pools`
   - Confirm US_CORP, US_TECH, US_GUEST, US_BYOD are gone

2. **Verify Site Hierarchy Deleted:**
   - Navigate to: `Design` → `Network Hierarchy`
   - Confirm "United States" area no longer exists under Global

---

## Project Structure

```
DEVWKS-1709-Code/
├── README.md
├── native-api-simple-example/
│   ├── native_api_simple.py    # Main automation script
│   ├── requirements.txt        # Python dependencies
│   ├── CC_Env_Sample.yml       # Sample configuration template
│   ├── CC_Env.yml              # Your configuration (create this)
│   └── venv/                   # Python virtual environment
└── local_data/
    └── DEVWKS-1709/            # Additional lab materials
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Verify credentials in YAML config file |
| Pool creation reports success but pool not found | Script uses correct `/api/v2/ippool` endpoint |
| Cannot delete pool | Ensure all reservations are deleted first |
| Cannot delete building | Ensure all floors are deleted first |
| SSL certificate errors | Set `CC_INSECURE: true` in config |

---

## License

This project is for educational purposes as part of Cisco Live DEVWKS-1709 workshop.

## Contact

For questions about this workshop, please contact the session presenters.
