#!/usr/bin/env python3
"""
Catalyst Center Native API Implementation
Equivalent to NAC Module YAML Configuration
"""

import requests
import json
from typing import Dict, List
import urllib3

# Disable SSL warnings for demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CatalystCenterAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        
    def authenticate(self):
        """Get authentication token"""
        auth_url = f"{self.base_url}/dna/system/api/v1/auth/token"
        response = requests.post(
            auth_url,
            auth=(self.username, self.password),
            verify=False
        )
        self.token = response.json()["Token"]
        self.headers["X-Auth-Token"] = self.token
        return self.token
    
    def get_site_id(self, site_name: str) -> str:
        """Get site ID by name"""
        url = f"{self.base_url}/dna/intent/api/v1/site"
        response = requests.get(url, headers=self.headers, verify=False)
        sites = response.json()["response"]
        for site in sites:
            if site["name"] == site_name:
                return site["id"]
        return None
    
    # ==========================================================================
    # IP POOL OPERATIONS
    # ==========================================================================
    
    def create_ip_pool(self, pool_data: Dict) -> str:
        """Create global IP pool"""
        url = f"{self.base_url}/dna/intent/api/v1/global-pool"
        # Simplified payload - only name and CIDR
        # DHCP/DNS servers cause validation errors during creation
        payload = {
            "ipPoolName": pool_data["name"],
            "ipPoolCidr": pool_data["ip_pool_cidr"]
        }
        response = requests.post(
            url, 
            headers=self.headers, 
            json=payload, 
            verify=False
        )
        return response.json()
    
    def reserve_ip_pool(self, site_id: str, reservation_data: Dict) -> str:
        """Reserve IP pool for a site"""
        url = f"{self.base_url}/dna/intent/api/v1/reserve-ip-subpool/{site_id}"
        payload = {
            "name": reservation_data["name"],
            "type": "Generic",
            "ipv4GlobalPool": reservation_data["parent_pool"],
            "ipv4Prefix": True,
            "ipv4PrefixLength": reservation_data["prefix_length"],
            "ipv4Subnet": reservation_data["subnet"],
            "ipv4GateWay": f"{reservation_data['subnet'].rsplit('.', 1)[0]}.1",
            "ipv4DhcpServers": reservation_data["dhcp_servers"],
            "ipv4DnsServers": reservation_data["dns_servers"]
        }
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            verify=False
        )
        return response.json()
    
    # ==========================================================================
    # SITE OPERATIONS
    # ==========================================================================
    
    def create_area(self, area_data: Dict) -> str:
        """Create area in site hierarchy"""
        url = f"{self.base_url}/dna/intent/api/v1/site"
        
        # Get parent site ID
        parent_id = self.get_site_id(area_data["parent_name"])
        
        payload = {
            "type": "area",
            "site": {
                "area": {
                    "name": area_data["name"],
                    "parentName": area_data["parent_name"]
                }
            }
        }
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            verify=False
        )
        return response.json()
    
    def create_building(self, building_data: Dict) -> str:
        """Create building in site hierarchy"""
        url = f"{self.base_url}/dna/intent/api/v1/site"
        
        payload = {
            "type": "building",
            "site": {
                "building": {
                    "name": building_data["name"],
                    "parentName": building_data["parent_name"],
                    "latitude": building_data["latitude"],
                    "longitude": building_data["longitude"],
                    "address": building_data["address"],
                    "country": building_data["country"]
                }
            }
        }
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            verify=False
        )
        
        # Wait for task completion
        task_id = response.json()["executionId"]
        self.wait_for_task(task_id)
        
        return response.json()
    
    def create_floor(self, floor_data: Dict) -> str:
        """Create floor in site hierarchy"""
        url = f"{self.base_url}/dna/intent/api/v1/site"
        
        payload = {
            "type": "floor",
            "site": {
                "floor": {
                    "name": floor_data["name"],
                    "parentName": floor_data["parent_name"],
                    "rfModel": "Cubes And Walled Offices",
                    "width": 100,
                    "length": 100,
                    "height": 10,
                    "floorNumber": floor_data["floor_number"]
                }
            }
        }
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            verify=False
        )
        return response.json()
    
    def wait_for_task(self, task_id: str, max_attempts: int = 30):
        """Poll task status until completion"""
        url = f"{self.base_url}/dna/intent/api/v1/task/{task_id}"
        for _ in range(max_attempts):
            response = requests.get(url, headers=self.headers, verify=False)
            task = response.json()["response"]
            if task["isError"]:
                raise Exception(f"Task failed: {task.get('failureReason', 'Unknown error')}")
            if not task.get("isError") and task.get("endTime"):
                return task
            import time
            time.sleep(2)
        raise TimeoutError("Task did not complete in time")


def main():
    """Main execution - create all infrastructure"""
    
    # Initialize API client
    cc = CatalystCenterAPI(
        base_url="https://198.18.129.100",
        username="admin",
        password="C1sco12345"
    )
    
    # Authenticate
    print("Authenticating...")
    cc.authenticate()
    
    # ==========================================================================
    # CREATE IP POOLS
    # ==========================================================================
    
    print("\nCreating IP Pools...")
    
    # US_CORP Pool
    cc.create_ip_pool({
        "name": "US_CORP",
        "ip_address_space": "IPv4",
        "ip_pool_cidr": "10.201.0.0/16",
        "dhcp_servers": ["10.201.0.1"],
        "dns_servers": ["10.201.0.1"]
    })
    
    # US_TECH Pool
    cc.create_ip_pool({
        "name": "US_TECH",
        "ip_address_space": "IPv4",
        "ip_pool_cidr": "10.202.0.0/16",
        "dhcp_servers": ["10.202.0.1"],
        "dns_servers": ["10.202.0.1"]
    })
    
    # US_GUEST Pool
    cc.create_ip_pool({
        "name": "US_GUEST",
        "ip_address_space": "IPv4",
        "ip_pool_cidr": "10.203.0.0/16",
        "dhcp_servers": ["10.203.0.1"],
        "dns_servers": ["10.203.0.1"]
    })
    
    # US_BYOD Pool
    cc.create_ip_pool({
        "name": "US_BYOD",
        "ip_address_space": "IPv4",
        "ip_pool_cidr": "10.204.0.0/16",
        "dhcp_servers": ["10.204.0.1"],
        "dns_servers": ["10.204.0.1"]
    })
    
    # ==========================================================================
    # CREATE SITE HIERARCHY - AREAS
    # ==========================================================================
    
    print("\nCreating Areas...")
    
    cc.create_area({
        "name": "United States",
        "parent_name": "Global"
    })
    
    cc.create_area({
        "name": "Golden Hills Campus",
        "parent_name": "Global/United States"
    })
    
    cc.create_area({
        "name": "Lakefront Tower",
        "parent_name": "Global/United States"
    })
    
    cc.create_area({
        "name": "Oceanfront Mansion",
        "parent_name": "Global/United States"
    })
    
    cc.create_area({
        "name": "Desert Oasis Branch",
        "parent_name": "Global/United States"
    })
    
    # ==========================================================================
    # CREATE SITE HIERARCHY - BUILDINGS
    # ==========================================================================
    
    print("\nCreating Buildings...")
    
    cc.create_building({
        "name": "Sunset Tower",
        "parent_name": "Global/United States/Golden Hills Campus",
        "latitude": 34.099,
        "longitude": -118.366,
        "address": "8358 Sunset Blvd, Los Angeles, CA 90069",
        "country": "United States"
    })
    
    cc.create_building({
        "name": "Windy City Plaza",
        "parent_name": "Global/United States/Lakefront Tower",
        "latitude": 41.878,
        "longitude": -87.630,
        "address": "233 S Wacker Dr, Chicago, IL 60606",
        "country": "United States"
    })
    
    cc.create_building({
        "name": "Art Deco Mansion",
        "parent_name": "Global/United States/Oceanfront Mansion",
        "latitude": 25.782,
        "longitude": -80.133,
        "address": "123 Ocean Drive, Miami Beach, FL 33139",
        "country": "United States"
    })
    
    cc.create_building({
        "name": "Desert Oasis Tower",
        "parent_name": "Global/United States/Desert Oasis Branch",
        "latitude": 33.448,
        "longitude": -112.074,
        "address": "1235 Cactus Ave, Phoenix, AZ 85001",
        "country": "United States"
    })
    
    # ==========================================================================
    # CREATE SITE HIERARCHY - FLOORS
    # ==========================================================================
    
    print("\nCreating Floors...")
    
    cc.create_floor({
        "name": "FLOOR_1",
        "parent_name": "Global/United States/Golden Hills Campus/Sunset Tower",
        "floor_number": 1
    })
    
    cc.create_floor({
        "name": "FLOOR_2",
        "parent_name": "Global/United States/Golden Hills Campus/Sunset Tower",
        "floor_number": 2
    })
    
    cc.create_floor({
        "name": "FLOOR_1",
        "parent_name": "Global/United States/Lakefront Tower/Windy City Plaza",
        "floor_number": 1
    })
    
    cc.create_floor({
        "name": "FLOOR_2",
        "parent_name": "Global/United States/Lakefront Tower/Windy City Plaza",
        "floor_number": 2
    })
    
    cc.create_floor({
        "name": "FLOOR_1",
        "parent_name": "Global/United States/Oceanfront Mansion/Art Deco Mansion",
        "floor_number": 1
    })
    
    cc.create_floor({
        "name": "FLOOR_1",
        "parent_name": "Global/United States/Desert Oasis Branch/Desert Oasis Tower",
        "floor_number": 1
    })
    
    # ==========================================================================
    # CREATE IP POOL RESERVATIONS
    # ==========================================================================
    
    print("\nCreating IP Pool Reservations...")
    
    # Get site IDs
    sunset_tower_id = cc.get_site_id("Sunset Tower")
    windy_city_id = cc.get_site_id("Windy City Plaza")
    art_deco_id = cc.get_site_id("Art Deco Mansion")
    desert_oasis_id = cc.get_site_id("Desert Oasis Tower")
    
    # Sunset Tower Reservations
    cc.reserve_ip_pool(sunset_tower_id, {
        "name": "ST_CORP",
        "parent_pool": "US_CORP",
        "prefix_length": 24,
        "subnet": "10.201.2.0",
        "dhcp_servers": ["10.201.0.1"],
        "dns_servers": ["10.201.0.1"]
    })
    
    cc.reserve_ip_pool(sunset_tower_id, {
        "name": "ST_TECH",
        "parent_pool": "US_TECH",
        "prefix_length": 24,
        "subnet": "10.202.2.0",
        "dhcp_servers": ["10.202.0.1"],
        "dns_servers": ["10.202.0.1"]
    })
    
    cc.reserve_ip_pool(sunset_tower_id, {
        "name": "ST_GUEST",
        "parent_pool": "US_GUEST",
        "prefix_length": 24,
        "subnet": "10.203.2.0",
        "dhcp_servers": ["10.203.0.1"],
        "dns_servers": ["10.203.0.1"]
    })
    
    cc.reserve_ip_pool(sunset_tower_id, {
        "name": "ST_BYOD",
        "parent_pool": "US_BYOD",
        "prefix_length": 24,
        "subnet": "10.204.2.0",
        "dhcp_servers": ["10.204.0.1"],
        "dns_servers": ["10.204.0.1"]
    })
    
    # Windy City Plaza Reservations
    cc.reserve_ip_pool(windy_city_id, {
        "name": "WCP_CORP",
        "parent_pool": "US_CORP",
        "prefix_length": 24,
        "subnet": "10.201.3.0",
        "dhcp_servers": ["10.201.0.1"],
        "dns_servers": ["10.201.0.1"]
    })
    
    cc.reserve_ip_pool(windy_city_id, {
        "name": "WCP_TECH",
        "parent_pool": "US_TECH",
        "prefix_length": 24,
        "subnet": "10.202.3.0",
        "dhcp_servers": ["10.202.0.1"],
        "dns_servers": ["10.202.0.1"]
    })
    
    cc.reserve_ip_pool(windy_city_id, {
        "name": "WCP_GUEST",
        "parent_pool": "US_GUEST",
        "prefix_length": 24,
        "subnet": "10.203.3.0",
        "dhcp_servers": ["10.203.0.1"],
        "dns_servers": ["10.203.0.1"]
    })
    
    cc.reserve_ip_pool(windy_city_id, {
        "name": "WCP_BYOD",
        "parent_pool": "US_BYOD",
        "prefix_length": 24,
        "subnet": "10.204.3.0",
        "dhcp_servers": ["10.204.0.1"],
        "dns_servers": ["10.204.0.1"]
    })
    
    # Art Deco Mansion Reservations
    cc.reserve_ip_pool(art_deco_id, {
        "name": "ADM_CORP",
        "parent_pool": "US_CORP",
        "prefix_length": 24,
        "subnet": "10.201.4.0",
        "dhcp_servers": ["10.201.0.1"],
        "dns_servers": ["10.201.0.1"]
    })
    
    cc.reserve_ip_pool(art_deco_id, {
        "name": "ADM_TECH",
        "parent_pool": "US_TECH",
        "prefix_length": 24,
        "subnet": "10.202.4.0",
        "dhcp_servers": ["10.202.0.1"],
        "dns_servers": ["10.202.0.1"]
    })
    
    cc.reserve_ip_pool(art_deco_id, {
        "name": "ADM_GUEST",
        "parent_pool": "US_GUEST",
        "prefix_length": 24,
        "subnet": "10.203.4.0",
        "dhcp_servers": ["10.203.0.1"],
        "dns_servers": ["10.203.0.1"]
    })
    
    cc.reserve_ip_pool(art_deco_id, {
        "name": "ADM_BYOD",
        "parent_pool": "US_BYOD",
        "prefix_length": 24,
        "subnet": "10.204.4.0",
        "dhcp_servers": ["10.204.0.1"],
        "dns_servers": ["10.204.0.1"]
    })
    
    # Desert Oasis Tower Reservations
    cc.reserve_ip_pool(desert_oasis_id, {
        "name": "DOT_CORP",
        "parent_pool": "US_CORP",
        "prefix_length": 24,
        "subnet": "10.201.1.0",
        "dhcp_servers": ["10.201.0.1"],
        "dns_servers": ["10.201.0.1"]
    })
    
    cc.reserve_ip_pool(desert_oasis_id, {
        "name": "DOT_TECH",
        "parent_pool": "US_TECH",
        "prefix_length": 24,
        "subnet": "10.202.1.0",
        "dhcp_servers": ["10.202.0.1"],
        "dns_servers": ["10.202.0.1"]
    })
    
    cc.reserve_ip_pool(desert_oasis_id, {
        "name": "DOT_GUEST",
        "parent_pool": "US_GUEST",
        "prefix_length": 24,
        "subnet": "10.203.1.0",
        "dhcp_servers": ["10.203.0.1"],
        "dns_servers": ["10.203.0.1"]
    })
    
    cc.reserve_ip_pool(desert_oasis_id, {
        "name": "DOT_BYOD",
        "parent_pool": "US_BYOD",
        "prefix_length": 24,
        "subnet": "10.204.1.0",
        "dhcp_servers": ["10.204.0.1"],
        "dns_servers": ["10.204.0.1"]
    })
    
    print("\n✅ All infrastructure created successfully!")


if __name__ == "__main__":
    main()
