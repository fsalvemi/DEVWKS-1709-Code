terraform {
  required_providers {
    catalystcenter = {
      source  = "CiscoDevNet/catalystcenter"
      version = "0.3.3"
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
# IP POOLS
# ==============================================================================

# US_CORP IP Pool
resource "catalystcenter_ip_pool" "us_corp" {
  name             = "US_CORP"
  ip_address_space = "IPv4"
  ip_subnet        = "10.201.0.0/16"
  gateway          = ["10.201.0.1"]
  dhcp_server_ips  = ["10.201.0.2"]
  dns_server_ips   = ["10.201.0.2"]
  type             = "generic"
}

resource "catalystcenter_ip_pool_reservation" "dot_corp" {
  ipv4_global_pool = "10.201.0.0/16"
  site_id        = catalystcenter_area.desert_oasis_branch.id
  name           = "DOT_CORP"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.201.1.0"
  ipv4_dhcp_servers = ["10.201.0.2"]
  ipv4_dns_servers  = ["10.201.0.2"]
  ipv4_gateway   = "10.201.1.1"
  depends_on     = [catalystcenter_ip_pool.us_corp]
}

resource "catalystcenter_ip_pool_reservation" "st_corp" {
  ipv4_global_pool = "10.201.0.0/16"
  site_id        = catalystcenter_building.sunset_tower.id
  name           = "ST_CORP"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.201.2.0"
  ipv4_dhcp_servers = ["10.201.0.2"]
  ipv4_dns_servers  = ["10.201.0.2"]
  ipv4_gateway   = "10.201.2.1"
  depends_on     = [catalystcenter_ip_pool.us_corp]
}

resource "catalystcenter_ip_pool_reservation" "wcp_corp" {
  ipv4_global_pool = "10.201.0.0/16"
  site_id        = catalystcenter_building.windy_city_plaza.id
  name           = "WCP_CORP"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.201.3.0"
  ipv4_dhcp_servers = ["10.201.0.2"]
  ipv4_dns_servers  = ["10.201.0.2"]
  ipv4_gateway   = "10.201.3.1"
  depends_on     = [catalystcenter_ip_pool.us_corp]
}

resource "catalystcenter_ip_pool_reservation" "adm_corp" {
  ipv4_global_pool = "10.201.0.0/16"
  site_id        = catalystcenter_building.art_deco_mansion.id
  name           = "ADM_CORP"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.201.4.0"
  ipv4_dhcp_servers = ["10.201.0.2"]
  ipv4_dns_servers  = ["10.201.0.2"]
  ipv4_gateway   = "10.201.4.1"
  depends_on     = [catalystcenter_ip_pool.us_corp]
}

# US_TECH IP Pool
resource "catalystcenter_ip_pool" "us_tech" {
  name             = "US_TECH"
  ip_address_space = "IPv4"
  ip_subnet        = "10.202.0.0/16"
  gateway          = ["10.202.0.1"]
  dhcp_server_ips  = ["10.202.0.2"]
  dns_server_ips   = ["10.202.0.2"]
  type             = "generic"
}

resource "catalystcenter_ip_pool_reservation" "dot_tech" {
  ipv4_global_pool = "10.202.0.0/16"
  site_id        = catalystcenter_area.desert_oasis_branch.id
  name           = "DOT_TECH"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.202.1.0"
  ipv4_dhcp_servers = ["10.202.0.2"]
  ipv4_dns_servers  = ["10.202.0.2"]
  ipv4_gateway   = "10.202.1.1"
  depends_on     = [catalystcenter_ip_pool.us_tech]
}

resource "catalystcenter_ip_pool_reservation" "st_tech" {
  ipv4_global_pool = "10.202.0.0/16"
  site_id        = catalystcenter_building.sunset_tower.id
  name           = "ST_TECH"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.202.2.0"
  ipv4_dhcp_servers = ["10.202.0.2"]
  ipv4_dns_servers  = ["10.202.0.2"]
  ipv4_gateway   = "10.202.2.1"
  depends_on     = [catalystcenter_ip_pool.us_tech]
}

resource "catalystcenter_ip_pool_reservation" "wcp_tech" {
  ipv4_global_pool = "10.202.0.0/16"
  site_id        = catalystcenter_building.windy_city_plaza.id
  name           = "WCP_TECH"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.202.3.0"
  ipv4_dhcp_servers = ["10.202.0.2"]
  ipv4_dns_servers  = ["10.202.0.2"]
  ipv4_gateway   = "10.202.3.1"
  depends_on     = [catalystcenter_ip_pool.us_tech]
}

resource "catalystcenter_ip_pool_reservation" "adm_tech" {
  ipv4_global_pool = "10.202.0.0/16"
  site_id        = catalystcenter_building.art_deco_mansion.id
  name           = "ADM_TECH"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.202.4.0"
  ipv4_dhcp_servers = ["10.202.0.2"]
  ipv4_dns_servers  = ["10.202.0.2"]
  ipv4_gateway   = "10.202.4.1"
  depends_on     = [catalystcenter_ip_pool.us_tech]
}

# US_GUEST IP Pool
resource "catalystcenter_ip_pool" "us_guest" {
  name             = "US_GUEST"
  ip_address_space = "IPv4"
  ip_subnet        = "10.203.0.0/16"
  gateway          = ["10.203.0.1"]
  dhcp_server_ips  = ["10.203.0.2"]
  dns_server_ips   = ["10.203.0.2"]
  type             = "generic"
}

resource "catalystcenter_ip_pool_reservation" "dot_guest" {
  ipv4_global_pool = "10.203.0.0/16"
  site_id        = catalystcenter_area.desert_oasis_branch.id
  name           = "DOT_GUEST"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.203.1.0"
  ipv4_dhcp_servers = ["10.203.0.2"]
  ipv4_dns_servers  = ["10.203.0.2"]
  ipv4_gateway   = "10.203.1.1"
  depends_on     = [catalystcenter_ip_pool.us_guest]
}

resource "catalystcenter_ip_pool_reservation" "st_guest" {
  ipv4_global_pool = "10.203.0.0/16"
  site_id        = catalystcenter_building.sunset_tower.id
  name           = "ST_GUEST"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.203.2.0"
  ipv4_dhcp_servers = ["10.203.0.2"]
  ipv4_dns_servers  = ["10.203.0.2"]
  ipv4_gateway   = "10.203.2.1"
  depends_on     = [catalystcenter_ip_pool.us_guest]
}

resource "catalystcenter_ip_pool_reservation" "wcp_guest" {
  ipv4_global_pool = "10.203.0.0/16"
  site_id        = catalystcenter_building.windy_city_plaza.id
  name           = "WCP_GUEST"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.203.3.0"
  ipv4_dhcp_servers = ["10.203.0.2"]
  ipv4_dns_servers  = ["10.203.0.2"]
  ipv4_gateway   = "10.203.3.1"
  depends_on     = [catalystcenter_ip_pool.us_guest]
}

resource "catalystcenter_ip_pool_reservation" "adm_guest" {
  ipv4_global_pool = "10.203.0.0/16"
  site_id        = catalystcenter_building.art_deco_mansion.id
  name           = "ADM_GUEST"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.203.4.0"
  ipv4_dhcp_servers = ["10.203.0.2"]
  ipv4_dns_servers  = ["10.203.0.2"]
  ipv4_gateway   = "10.203.4.1"
  depends_on     = [catalystcenter_ip_pool.us_guest]
}

# US_BYOD IP Pool
resource "catalystcenter_ip_pool" "us_byod" {
  name             = "US_BYOD"
  ip_address_space = "IPv4"
  ip_subnet        = "10.204.0.0/16"
  gateway          = ["10.204.0.1"]
  dhcp_server_ips  = ["10.204.0.2"]
  dns_server_ips   = ["10.204.0.2"]
  type             = "generic"
}

resource "catalystcenter_ip_pool_reservation" "dot_byod" {
  ipv4_global_pool = "10.204.0.0/16"
  site_id        = catalystcenter_area.desert_oasis_branch.id
  name           = "DOT_BYOD"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.204.1.0"
  ipv4_dhcp_servers = ["10.204.0.2"]
  ipv4_dns_servers  = ["10.204.0.2"]
  ipv4_gateway   = "10.204.1.1"
  depends_on     = [catalystcenter_ip_pool.us_byod]
}

resource "catalystcenter_ip_pool_reservation" "st_byod" {
  ipv4_global_pool = "10.204.0.0/16"
  site_id        = catalystcenter_building.sunset_tower.id
  name           = "ST_BYOD"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.204.2.0"
  ipv4_dhcp_servers = ["10.204.0.2"]
  ipv4_dns_servers  = ["10.204.0.2"]
  ipv4_gateway   = "10.204.2.1"
  depends_on     = [catalystcenter_ip_pool.us_byod]
}

resource "catalystcenter_ip_pool_reservation" "wcp_byod" {
  ipv4_global_pool = "10.204.0.0/16"
  site_id        = catalystcenter_building.windy_city_plaza.id
  name           = "WCP_BYOD"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.204.3.0"
  ipv4_dhcp_servers = ["10.204.0.2"]
  ipv4_dns_servers  = ["10.204.0.2"]
  ipv4_gateway   = "10.204.3.1"
  depends_on     = [catalystcenter_ip_pool.us_byod]
}

resource "catalystcenter_ip_pool_reservation" "adm_byod" {
  ipv4_global_pool = "10.204.0.0/16"
  site_id        = catalystcenter_building.art_deco_mansion.id
  name           = "ADM_BYOD"
  type           = "Generic"
  ipv4_prefix    = true
  ipv4_prefix_length = 24
  ipv4_subnet    = "10.204.4.0"
  ipv4_dhcp_servers = ["10.204.0.2"]
  ipv4_dns_servers  = ["10.204.0.2"]
  ipv4_gateway   = "10.204.4.1"
  depends_on     = [catalystcenter_ip_pool.us_byod]
}

# ==============================================================================
# SITE HIERARCHY - AREAS
# ==============================================================================

resource "catalystcenter_area" "united_states" {
  name        = "United States"
  parent_name = "Global"
}

resource "catalystcenter_area" "golden_hills_campus" {
  name        = "Golden Hills Campus"
  parent_name = "Global/United States"
  depends_on  = [catalystcenter_area.united_states]
}

resource "catalystcenter_area" "lakefront_tower" {
  name        = "Lakefront Tower"
  parent_name = "Global/United States"
  depends_on  = [catalystcenter_area.united_states]
}

resource "catalystcenter_area" "oceanfront_mansion" {
  name        = "Oceanfront Mansion"
  parent_name = "Global/United States"
  depends_on  = [catalystcenter_area.united_states]
}

resource "catalystcenter_area" "desert_oasis_branch" {
  name        = "Desert Oasis Branch"
  parent_name = "Global/United States"
  depends_on  = [catalystcenter_area.united_states]
}

# ==============================================================================
# SITE HIERARCHY - BUILDINGS
# ==============================================================================

resource "catalystcenter_building" "sunset_tower" {
  name        = "Sunset Tower"
  parent_name = "Global/United States/Golden Hills Campus"
  address     = "8358 Sunset Blvd, Los Angeles, CA 90069"
  latitude    = 34.099
  longitude   = -118.366
  country     = "United States"
  depends_on  = [catalystcenter_area.golden_hills_campus]
}

resource "catalystcenter_building" "windy_city_plaza" {
  name        = "Windy City Plaza"
  parent_name = "Global/United States/Lakefront Tower"
  address     = "233 S Wacker Dr, Chicago, IL 60606"
  latitude    = 41.878
  longitude   = -87.630
  country     = "United States"
  depends_on  = [catalystcenter_area.lakefront_tower]
}

resource "catalystcenter_building" "art_deco_mansion" {
  name        = "Art Deco Mansion"
  parent_name = "Global/United States/Oceanfront Mansion"
  address     = "123 Ocean Drive, Miami Beach, FL 33139"
  latitude    = 25.782
  longitude   = -80.133
  country     = "United States"
  depends_on  = [catalystcenter_area.oceanfront_mansion]
}

resource "catalystcenter_building" "desert_oasis_tower" {
  name        = "Desert Oasis Tower"
  parent_name = "Global/United States/Desert Oasis Branch"
  address     = "1235 Cactus Ave, Phoenix, AZ 85001"
  latitude    = 33.448
  longitude   = -112.074
  country     = "United States"
  depends_on  = [catalystcenter_area.desert_oasis_branch]
}

# ==============================================================================
# SITE HIERARCHY - FLOORS
# ==============================================================================

resource "catalystcenter_floor" "sunset_tower_floor_1" {
  name         = "FLOOR_1"
  parent_name  = "Global/United States/Golden Hills Campus/Sunset Tower"
  floor_number = 1
  rf_model     = "Cubes And Walled Offices"
  width        = 100
  length       = 100
  height       = 10
  depends_on   = [catalystcenter_building.sunset_tower]
}

resource "catalystcenter_floor" "sunset_tower_floor_2" {
  name         = "FLOOR_2"
  parent_name  = "Global/United States/Golden Hills Campus/Sunset Tower"
  floor_number = 2
  rf_model     = "Cubes And Walled Offices"
  width        = 100
  length       = 100
  height       = 10
  depends_on   = [catalystcenter_building.sunset_tower]
}

resource "catalystcenter_floor" "windy_city_plaza_floor_1" {
  name         = "FLOOR_1"
  parent_name  = "Global/United States/Lakefront Tower/Windy City Plaza"
  floor_number = 1
  rf_model     = "Cubes And Walled Offices"
  width        = 100
  length       = 100
  height       = 10
  depends_on   = [catalystcenter_building.windy_city_plaza]
}

resource "catalystcenter_floor" "windy_city_plaza_floor_2" {
  name         = "FLOOR_2"
  parent_name  = "Global/United States/Lakefront Tower/Windy City Plaza"
  floor_number = 2
  rf_model     = "Cubes And Walled Offices"
  width        = 100
  length       = 100
  height       = 10
  depends_on   = [catalystcenter_building.windy_city_plaza]
}

resource "catalystcenter_floor" "art_deco_mansion_floor_1" {
  name         = "FLOOR_1"
  parent_name  = "Global/United States/Oceanfront Mansion/Art Deco Mansion"
  floor_number = 1
  rf_model     = "Cubes And Walled Offices"
  width        = 100
  length       = 100
  height       = 10
  depends_on   = [catalystcenter_building.art_deco_mansion]
}

resource "catalystcenter_floor" "desert_oasis_tower_floor_1" {
  name         = "FLOOR_1"
  parent_name  = "Global/United States/Desert Oasis Branch/Desert Oasis Tower"
  floor_number = 1
  rf_model     = "Cubes And Walled Offices"
  width        = 100
  length       = 100
  height       = 10
  depends_on   = [catalystcenter_building.desert_oasis_tower]
}