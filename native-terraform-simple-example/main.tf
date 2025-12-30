terraform {
  required_providers {
    catalystcenter = {
      source  = "CiscoDevNet/catalystcenter"
      version = "0.4.5"
    }
  }
}

provider "catalystcenter" {
  username = var.catalyst_center_username
  password = var.catalyst_center_password
  url      = var.catalyst_center_url
  insecure = var.catalyst_center_insecure
}

# ==============================================================================
# DATA SOURCE - Get Global Site ID
# ==============================================================================

data "catalystcenter_site" "global" {
  name_hierarchy = "Global"
}

# ==============================================================================
# IP POOLS
# ==============================================================================

# US_CORP IP Pool
resource "catalystcenter_ip_pool" "us_corp" {
  name                        = "US_CORP"
  pool_type                   = "Generic"
  address_space_subnet        = "10.201.0.0"
  address_space_prefix_length = 16
  address_space_gateway       = "10.201.0.1"
  address_space_dhcp_servers  = ["10.201.0.2"]
  address_space_dns_servers   = ["10.201.0.2"]
}

resource "catalystcenter_ip_pool_reservation" "dot_corp" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_corp.id
  site_id             = catalystcenter_area.desert_oasis_branch.id
  name                = "DOT_CORP"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.201.1.0"
  ipv4_dhcp_servers   = ["10.201.0.2"]
  ipv4_dns_servers    = ["10.201.0.2"]
  ipv4_gateway        = "10.201.1.1"
}

resource "catalystcenter_ip_pool_reservation" "st_corp" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_corp.id
  site_id             = catalystcenter_building.sunset_tower.id
  name                = "ST_CORP"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.201.2.0"
  ipv4_dhcp_servers   = ["10.201.0.2"]
  ipv4_dns_servers    = ["10.201.0.2"]
  ipv4_gateway        = "10.201.2.1"
}

resource "catalystcenter_ip_pool_reservation" "wcp_corp" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_corp.id
  site_id             = catalystcenter_building.windy_city_plaza.id
  name                = "WCP_CORP"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.201.3.0"
  ipv4_dhcp_servers   = ["10.201.0.2"]
  ipv4_dns_servers    = ["10.201.0.2"]
  ipv4_gateway        = "10.201.3.1"
}

resource "catalystcenter_ip_pool_reservation" "adm_corp" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_corp.id
  site_id             = catalystcenter_building.art_deco_mansion.id
  name                = "ADM_CORP"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.201.4.0"
  ipv4_dhcp_servers   = ["10.201.0.2"]
  ipv4_dns_servers    = ["10.201.0.2"]
  ipv4_gateway        = "10.201.4.1"
}

# US_TECH IP Pool
resource "catalystcenter_ip_pool" "us_tech" {
  name                        = "US_TECH"
  pool_type                   = "Generic"
  address_space_subnet        = "10.202.0.0"
  address_space_prefix_length = 16
  address_space_gateway       = "10.202.0.1"
  address_space_dhcp_servers  = ["10.202.0.2"]
  address_space_dns_servers   = ["10.202.0.2"]
}

resource "catalystcenter_ip_pool_reservation" "dot_tech" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_tech.id
  site_id             = catalystcenter_area.desert_oasis_branch.id
  name                = "DOT_TECH"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.202.1.0"
  ipv4_dhcp_servers   = ["10.202.0.2"]
  ipv4_dns_servers    = ["10.202.0.2"]
  ipv4_gateway        = "10.202.1.1"
}

resource "catalystcenter_ip_pool_reservation" "st_tech" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_tech.id
  site_id             = catalystcenter_building.sunset_tower.id
  name                = "ST_TECH"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.202.2.0"
  ipv4_dhcp_servers   = ["10.202.0.2"]
  ipv4_dns_servers    = ["10.202.0.2"]
  ipv4_gateway        = "10.202.2.1"
}

resource "catalystcenter_ip_pool_reservation" "wcp_tech" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_tech.id
  site_id             = catalystcenter_building.windy_city_plaza.id
  name                = "WCP_TECH"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.202.3.0"
  ipv4_dhcp_servers   = ["10.202.0.2"]
  ipv4_dns_servers    = ["10.202.0.2"]
  ipv4_gateway        = "10.202.3.1"
}

resource "catalystcenter_ip_pool_reservation" "adm_tech" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_tech.id
  site_id             = catalystcenter_building.art_deco_mansion.id
  name                = "ADM_TECH"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.202.4.0"
  ipv4_dhcp_servers   = ["10.202.0.2"]
  ipv4_dns_servers    = ["10.202.0.2"]
  ipv4_gateway        = "10.202.4.1"
}

# US_GUEST IP Pool
resource "catalystcenter_ip_pool" "us_guest" {
  name                        = "US_GUEST"
  pool_type                   = "Generic"
  address_space_subnet        = "10.203.0.0"
  address_space_prefix_length = 16
  address_space_gateway       = "10.203.0.1"
  address_space_dhcp_servers  = ["10.203.0.2"]
  address_space_dns_servers   = ["10.203.0.2"]
}

resource "catalystcenter_ip_pool_reservation" "dot_guest" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_guest.id
  site_id             = catalystcenter_area.desert_oasis_branch.id
  name                = "DOT_GUEST"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.203.1.0"
  ipv4_dhcp_servers   = ["10.203.0.2"]
  ipv4_dns_servers    = ["10.203.0.2"]
  ipv4_gateway        = "10.203.1.1"
}

resource "catalystcenter_ip_pool_reservation" "st_guest" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_guest.id
  site_id             = catalystcenter_building.sunset_tower.id
  name                = "ST_GUEST"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.203.2.0"
  ipv4_dhcp_servers   = ["10.203.0.2"]
  ipv4_dns_servers    = ["10.203.0.2"]
  ipv4_gateway        = "10.203.2.1"
}

resource "catalystcenter_ip_pool_reservation" "wcp_guest" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_guest.id
  site_id             = catalystcenter_building.windy_city_plaza.id
  name                = "WCP_GUEST"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.203.3.0"
  ipv4_dhcp_servers   = ["10.203.0.2"]
  ipv4_dns_servers    = ["10.203.0.2"]
  ipv4_gateway        = "10.203.3.1"
}

resource "catalystcenter_ip_pool_reservation" "adm_guest" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_guest.id
  site_id             = catalystcenter_building.art_deco_mansion.id
  name                = "ADM_GUEST"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.203.4.0"
  ipv4_dhcp_servers   = ["10.203.0.2"]
  ipv4_dns_servers    = ["10.203.0.2"]
  ipv4_gateway        = "10.203.4.1"
}

# US_BYOD IP Pool
resource "catalystcenter_ip_pool" "us_byod" {
  name                        = "US_BYOD"
  pool_type                   = "Generic"
  address_space_subnet        = "10.204.0.0"
  address_space_prefix_length = 16
  address_space_gateway       = "10.204.0.1"
  address_space_dhcp_servers  = ["10.204.0.2"]
  address_space_dns_servers   = ["10.204.0.2"]
}

resource "catalystcenter_ip_pool_reservation" "dot_byod" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_byod.id
  site_id             = catalystcenter_area.desert_oasis_branch.id
  name                = "DOT_BYOD"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.204.1.0"
  ipv4_dhcp_servers   = ["10.204.0.2"]
  ipv4_dns_servers    = ["10.204.0.2"]
  ipv4_gateway        = "10.204.1.1"
}

resource "catalystcenter_ip_pool_reservation" "st_byod" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_byod.id
  site_id             = catalystcenter_building.sunset_tower.id
  name                = "ST_BYOD"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.204.2.0"
  ipv4_dhcp_servers   = ["10.204.0.2"]
  ipv4_dns_servers    = ["10.204.0.2"]
  ipv4_gateway        = "10.204.2.1"
}

resource "catalystcenter_ip_pool_reservation" "wcp_byod" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_byod.id
  site_id             = catalystcenter_building.windy_city_plaza.id
  name                = "WCP_BYOD"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.204.3.0"
  ipv4_dhcp_servers   = ["10.204.0.2"]
  ipv4_dns_servers    = ["10.204.0.2"]
  ipv4_gateway        = "10.204.3.1"
}

resource "catalystcenter_ip_pool_reservation" "adm_byod" {
  ipv4_global_pool_id = catalystcenter_ip_pool.us_byod.id
  site_id             = catalystcenter_building.art_deco_mansion.id
  name                = "ADM_BYOD"
  pool_type           = "Generic"
  ipv4_prefix_length  = 24
  ipv4_subnet         = "10.204.4.0"
  ipv4_dhcp_servers   = ["10.204.0.2"]
  ipv4_dns_servers    = ["10.204.0.2"]
  ipv4_gateway        = "10.204.4.1"
}

# ==============================================================================
# SITE HIERARCHY - AREAS
# ==============================================================================

resource "catalystcenter_area" "united_states" {
  name      = "United States"
  parent_id = data.catalystcenter_site.global.id
}

resource "catalystcenter_area" "golden_hills_campus" {
  name      = "Golden Hills Campus"
  parent_id = catalystcenter_area.united_states.id
}

resource "catalystcenter_area" "lakefront_tower" {
  name      = "Lakefront Tower"
  parent_id = catalystcenter_area.united_states.id
}

resource "catalystcenter_area" "oceanfront_mansion" {
  name      = "Oceanfront Mansion"
  parent_id = catalystcenter_area.united_states.id
}

resource "catalystcenter_area" "desert_oasis_branch" {
  name      = "Desert Oasis Branch"
  parent_id = catalystcenter_area.united_states.id
}

# ==============================================================================
# SITE HIERARCHY - BUILDINGS
# ==============================================================================

resource "catalystcenter_building" "sunset_tower" {
  name      = "Sunset Tower"
  parent_id = catalystcenter_area.golden_hills_campus.id
  address   = "8358 Sunset Blvd, Los Angeles, CA 90069"
  latitude  = 34.099
  longitude = -118.366
  country   = "United States"
}

resource "catalystcenter_building" "windy_city_plaza" {
  name      = "Windy City Plaza"
  parent_id = catalystcenter_area.lakefront_tower.id
  address   = "233 S Wacker Dr, Chicago, IL 60606"
  latitude  = 41.878
  longitude = -87.630
  country   = "United States"
}

resource "catalystcenter_building" "art_deco_mansion" {
  name      = "Art Deco Mansion"
  parent_id = catalystcenter_area.oceanfront_mansion.id
  address   = "123 Ocean Drive, Miami Beach, FL 33139"
  latitude  = 25.782
  longitude = -80.133
  country   = "United States"
}

resource "catalystcenter_building" "desert_oasis_tower" {
  name      = "Desert Oasis Tower"
  parent_id = catalystcenter_area.desert_oasis_branch.id
  address   = "1235 Cactus Ave, Phoenix, AZ 85001"
  latitude  = 33.448
  longitude = -112.074
  country   = "United States"
}

# ==============================================================================
# SITE HIERARCHY - FLOORS
# ==============================================================================

resource "catalystcenter_floor" "sunset_tower_floor_1" {
  name             = "FLOOR_1"
  parent_id        = catalystcenter_building.sunset_tower.id
  floor_number     = 1
  rf_model         = "Cubes And Walled Offices"
  width            = 100
  length           = 100
  height           = 10
  units_of_measure = "feet"
}

resource "catalystcenter_floor" "sunset_tower_floor_2" {
  name             = "FLOOR_2"
  parent_id        = catalystcenter_building.sunset_tower.id
  floor_number     = 2
  rf_model         = "Cubes And Walled Offices"
  width            = 100
  length           = 100
  height           = 10
  units_of_measure = "feet"
}

resource "catalystcenter_floor" "windy_city_plaza_floor_1" {
  name             = "FLOOR_1"
  parent_id        = catalystcenter_building.windy_city_plaza.id
  floor_number     = 1
  rf_model         = "Cubes And Walled Offices"
  width            = 100
  length           = 100
  height           = 10
  units_of_measure = "feet"
}

resource "catalystcenter_floor" "windy_city_plaza_floor_2" {
  name             = "FLOOR_2"
  parent_id        = catalystcenter_building.windy_city_plaza.id
  floor_number     = 2
  rf_model         = "Cubes And Walled Offices"
  width            = 100
  length           = 100
  height           = 10
  units_of_measure = "feet"
}

resource "catalystcenter_floor" "art_deco_mansion_floor_1" {
  name             = "FLOOR_1"
  parent_id        = catalystcenter_building.art_deco_mansion.id
  floor_number     = 1
  rf_model         = "Cubes And Walled Offices"
  width            = 100
  length           = 100
  height           = 10
  units_of_measure = "feet"
}

resource "catalystcenter_floor" "desert_oasis_tower_floor_1" {
  name             = "FLOOR_1"
  parent_id        = catalystcenter_building.desert_oasis_tower.id
  floor_number     = 1
  rf_model         = "Cubes And Walled Offices"
  width            = 100
  length           = 100
  height           = 10
  units_of_measure = "feet"
}