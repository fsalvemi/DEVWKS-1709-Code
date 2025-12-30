# NAC Module Approach - Simple Example

This folder demonstrates the **Network-as-Code (NAC) Module** approach to configuring Cisco Catalyst Center using YAML-based declarative configuration.

## 🎯 What This Example Does

Deploys a complete network infrastructure to Catalyst Center:
- **5 Areas**: United States, Golden Hills Campus, Lakefront Tower, Oceanfront Mansion, Desert Oasis Branch
- **4 Buildings**: Sunset Tower, Windy City Plaza, Art Deco Mansion, Desert Oasis Tower  
- **6 Floors**: Multiple floors across different buildings
- **4 Global IP Pools**: US_CORP (10.201.0.0/16), US_TECH (10.202.0.0/16), US_GUEST (10.203.0.0/16), US_BYOD (10.204.0.0/16)
- **16 IP Pool Reservations**: 4 reservations per building (CORP, TECH, GUEST, BYOD)

**Total Resources Created**: 35

## 📁 File Structure

```
nac-catalystcenter-simple-example/
├── main.tf                    # Terraform configuration using NAC module
├── data/
│   ├── sites.nac.yaml        # Site hierarchy (areas, buildings, floors)
│   └── ip_pools.nac.yaml     # IP pools and reservations
└── reference_configs/
    ├── initial_config/        # Base US-only configuration
    │   ├── sites.nac.yaml     # Initial site hierarchy
    │   └── ip_pools.nac.yaml  # Initial IP pools
    └── final_config/          # Complete configuration with Rome
        ├── sites.nac.yaml     # Final site hierarchy
        └── ip_pools.nac.yaml  # Final IP pools
```

**Note**: The `reference_configs` folder is provided for learning and validation purposes. It contains both the initial configuration (US sites only) and the final configuration (with Rome office added) that you'll work towards during the lab exercises.

## Suggested Learning Path

Follow the [Lab Guide](https://fsalvemi.github.io/DEVWKS-1709-Lab-Guide/)