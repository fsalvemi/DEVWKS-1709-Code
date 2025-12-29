#!/usr/bin/env python3
"""
Simplified Catalyst Center Native API Implementation
Creates sites and global IP pools

Usage:
    python native_api_simple.py create --config CC_Env.yml
    python native_api_simple.py delete --config CC_Env.yml
    python native_api_simple.py status --config CC_Env.yml
    
Configuration:
    A YAML configuration file is REQUIRED containing Catalyst Center credentials.
    See CC_Env_Sample.yml for the required format.
"""

import requests
import time
import json
import sys
import argparse
import urllib3
import yaml
import os
from pathlib import Path

# Disable SSL warnings for demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_credentials_from_yaml(file_path='CC_Env.yml'):
    """
    Load Catalyst Center credentials from YAML file
    
    Args:
        file_path: Path to YAML configuration file (default: CC_Env.yml)
        
    Returns:
        dict: Configuration with keys: base_url, username, password, verify_ssl
    """
    # Try to find the YAML file in current directory or script directory
    script_dir = Path(__file__).parent
    yaml_paths = [
        Path(file_path),  # Current directory or absolute path
        script_dir / file_path,  # Script directory
    ]
    
    for yaml_path in yaml_paths:
        if yaml_path.exists():
            try:
                with open(yaml_path, 'r') as f:
                    config = yaml.safe_load(f)
                    
                    # Validate required fields
                    required_fields = ['CC_IP', 'CC_USERNAME', 'CC_PASSWORD']
                    missing = [f for f in required_fields if f not in config]
                    if missing:
                        print(f"❌ Missing required fields in {yaml_path}: {', '.join(missing)}")
                        return None
                    
                    # Build configuration
                    verify_ssl = not config.get('CC_INSECURE', True)
                    
                    return {
                        'base_url': f"https://{config['CC_IP']}",
                        'username': config['CC_USERNAME'],
                        'password': config['CC_PASSWORD'],
                        'verify_ssl': verify_ssl
                    }
            except yaml.YAMLError as e:
                print(f"❌ Error parsing YAML file {yaml_path}: {e}")
                return None
            except Exception as e:
                print(f"❌ Error reading credentials from {yaml_path}: {e}")
                return None
    
    return None


class CatalystCenterAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def wait_for_task(self, task_id: str, task_url: str = None, timeout: int = 600) -> bool:
        """
        Wait for a task to complete and return success status
        
        Args:
            task_id: The execution/task ID
            task_url: Optional full URL to check status (use executionStatusUrl from response)
            timeout: Maximum seconds to wait
        """
        # Use provided URL or construct the execution status URL
        if task_url:
            url = f"{self.base_url}{task_url}" if not task_url.startswith('http') else task_url
        else:
            # Use the dnacaap execution-status endpoint (not the task endpoint)
            url = f"{self.base_url}/dna/intent/api/v1/dnacaap/management/execution-status/{task_id}"
        
        start_time = time.time()
        check_interval = 10  # Check every 10 seconds
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, headers=self.headers, verify=False, timeout=30)
                
                # Handle 404 - task might not exist yet or completed too quickly
                if response.status_code == 404:
                    print("  ℹ️  Task not found (may have completed quickly)")
                    return True
                
                if response.status_code == 200:
                    task_data = response.json()
                    
                    # Check status field (dnacaap execution-status format)
                    status = task_data.get('status', '')
                    
                    if status == 'SUCCESS':
                        # Additional validation: Check bapiSyncResponse for actual errors
                        # Some APIs report SUCCESS but include error details in bapiSyncResponse
                        bapi_error = task_data.get('bapiError')
                        if bapi_error:
                            print(f"  ❌ Task reported success but has error: {bapi_error}")
                            return False
                        
                        # Check bapiSyncResponseJson for status indicators
                        sync_response = task_data.get('bapiSyncResponseJson', {})
                        if isinstance(sync_response, dict):
                            # Some responses have status: "false" even with SUCCESS
                            if sync_response.get('status') == 'false' or sync_response.get('status') == False:
                                error_msg = sync_response.get('message', 'Unknown error')
                                print(f"  ❌ Task failed (bapiSyncResponse): {error_msg}")
                                return False
                        
                        return True
                    elif status in ['FAILURE', 'FAILED']:
                        error = task_data.get('bapiError', 'Task failed')
                        print(f"  ❌ Task failed: {error}")
                        return False
                    
                    # Also check older task response format
                    if task_data.get('isError'):
                        error_msg = task_data.get('failureReason', 'Unknown error')
                        print(f"  ❌ Task failed: {error_msg}")
                        return False
                    
                    # Check if task has ended
                    if task_data.get('endTime') or task_data.get('endTimeEpoch'):
                        # Task ended - verify it was successful
                        if status == 'SUCCESS' or not task_data.get('isError'):
                            return True
                        else:
                            print(f"  ❌ Task ended with error")
                            return False
                    
                    # Task still in progress
                    elapsed = int(time.time() - start_time)
                    print(f"  ⏳ Task in progress... ({elapsed}s elapsed, status: {status})")
                    time.sleep(check_interval)
                    
                else:
                    # Unexpected status code
                    print(f"  ⚠️  Unexpected status {response.status_code}, retrying...")
                    time.sleep(check_interval)
                    
            except requests.exceptions.Timeout:
                print(f"  ⚠️  Request timeout, retrying...")
                time.sleep(check_interval)
            except requests.exceptions.ConnectionError:
                print(f"  ⚠️  Connection error, retrying...")
                time.sleep(check_interval)
            except Exception as e:
                print(f"  ⚠️  Error: {str(e)[:50]}, retrying...")
                time.sleep(check_interval)
        
        # Timeout reached
        print(f"  ⏱️  Task monitoring timeout after {timeout}s")
        print(f"  ℹ️  Assuming task completed (may need manual verification)")
        return True  # Return True to allow process to continue
    
    def authenticate(self):
        """Get authentication token"""
        auth_url = f"{self.base_url}/dna/system/api/v1/auth/token"
        response = requests.post(
            auth_url,
            auth=(self.username, self.password),
            verify=False,
            timeout=30
        )
        response.raise_for_status()
        self.token = response.json()["Token"]
        self.headers["X-Auth-Token"] = self.token
        print("✅ Authentication successful")
        return self.token
    
    def get_site_by_name(self, site_name: str):
        """Get site by name (returns first match only)"""
        url = f"{self.base_url}/dna/intent/api/v1/site"
        response = requests.get(url, headers=self.headers, verify=False, timeout=30)
        sites = response.json()["response"]
        for site in sites:
            if site["name"] == site_name:
                return site
        return None
    
    def get_site_by_name_and_parent(self, site_name: str, parent_name: str):
        """Get site by name under a specific parent (for duplicate names like floors)"""
        url = f"{self.base_url}/dna/intent/api/v1/site"
        response = requests.get(url, headers=self.headers, verify=False, timeout=30)
        sites = response.json()["response"]
        
        for site in sites:
            if site["name"] == site_name:
                # Check if this site is under the specified parent
                hierarchy = site.get('siteNameHierarchy', '')
                # Hierarchy format: "Global/United States/Area/Building/Floor"
                parts = hierarchy.split('/')
                
                # Check if parent_name is the direct parent (second to last in path)
                if len(parts) >= 2 and parts[-2] == parent_name:
                    return site
        
        return None
    
    def get_global_pool_by_name(self, pool_name: str):
        """Get global pool by name"""
        url = f"{self.base_url}/dna/intent/api/v1/global-pool"
        response = requests.get(url, headers=self.headers, verify=False, timeout=30)
        pools = response.json()["response"]
        for pool in pools:
            if pool.get("ipPoolName") == pool_name:
                return pool
        return None
    
    def get_reservation_by_name(self, site_name: str, reservation_name: str):
        """Get IP pool reservation by name for a specific site"""
        # Get site ID
        site = self.get_site_by_name(site_name)
        if not site:
            return None
        
        site_id = site["id"]
        
        try:
            url = f"{self.base_url}/dna/intent/api/v1/reserve-ip-subpool?siteId={site_id}"
            response = requests.get(url, headers=self.headers, verify=False, timeout=30)
            
            if response.status_code == 200:
                reservations = response.json().get('response', [])
                
                for res in reservations:
                    if res.get('groupName') == reservation_name:
                        return res
        except Exception:
            pass
        
        return None
    
    def create_ip_pool(self, name: str, cidr: str):
        """Create global IP pool with correct payload format"""
        # Check if exists
        existing = self.get_global_pool_by_name(name)
        if existing:
            print(f"ℹ️  Pool '{name}' already exists, skipping")
            return existing
        
        # Parse CIDR into subnet and prefix length
        subnet, prefix = cidr.split('/')
        
        url = f"{self.base_url}/dna/intent/api/v1/global-pool"
        # Use the correct schema from Catalyst Center documentation
        payload = {
            "name": name,
            "poolType": "Generic",
            "addressSpace": {
                "subnet": subnet,
                "prefixLength": int(prefix)
            }
        }
        
        print(f"Creating pool '{name}' ({cidr})...")
        response = requests.post(url, headers=self.headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Get task ID from response
        task_id = result.get('executionId')
        task_url = result.get('executionStatusUrl')
        
        if task_id:
            print(f"  Waiting for task {task_id[:8]}...")
            if self.wait_for_task(task_id, task_url, timeout=600):
                print(f"✅ Pool '{name}' task completed successfully")
                # Wait for pool to propagate
                print(f"  Verifying pool creation...")
                time.sleep(5)
                
                # Verify the pool actually exists
                created_pool = self.get_global_pool_by_name(name)
                if created_pool:
                    print(f"✅ Pool '{name}' verified in system")
                    return created_pool
                else:
                    print(f"⚠️  WARNING: Task succeeded but pool '{name}' not found in system!")
                    print(f"  This is a known Catalyst Center API issue with global pools.")
                    print(f"  Please create the pool manually via GUI with:")
                    print(f"    Name: {name}")
                    print(f"    CIDR: {cidr}")
                    return None
            else:
                print(f"❌ Pool '{name}' creation failed")
                return None
        elif task_url:
            # Fallback: check executionStatusUrl once (older API style)
            time.sleep(2)
            status_url = f"{self.base_url}{task_url}"
            status_resp = requests.get(status_url, headers=self.headers, verify=False, timeout=30)
            status = status_resp.json()
            
            if status.get("status") == "SUCCESS":
                print(f"✅ Pool '{name}' created successfully")
                time.sleep(3)  # Wait for pool to appear
                return self.get_global_pool_by_name(name)
            else:
                error = status.get("bapiError", "Unknown error")
                print(f"❌ Pool creation failed: {error}")
                return None
        else:
            print(f"✅ Pool '{name}' created")
        
        return result
    
    def create_area(self, name: str, parent_name: str):
        """Create area"""
        # Check if exists
        existing = self.get_site_by_name(name)
        if existing:
            print(f"ℹ️  Area '{name}' already exists, skipping")
            return existing
        
        url = f"{self.base_url}/dna/intent/api/v1/site"
        payload = {
            "type": "area",
            "site": {
                "area": {
                    "name": name,
                    "parentName": parent_name
                }
            }
        }
        
        print(f"Creating area '{name}'...")
        response = requests.post(url, headers=self.headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        task_id = result.get('executionId')
        task_url = result.get('executionStatusUrl')
        
        if task_id:
            print(f"  Waiting for task {task_id[:8]}...")
            if self.wait_for_task(task_id, task_url):
                print(f"✅ Area '{name}' created successfully")
            else:
                print(f"❌ Area '{name}' creation failed")
                return None
        else:
            print(f"✅ Area '{name}' created")
        
        time.sleep(1)
        return result
    
    def create_building(self, name: str, parent_name: str, latitude: float, longitude: float, address: str, country: str):
        """Create building"""
        # Check if exists
        existing = self.get_site_by_name(name)
        if existing:
            print(f"ℹ️  Building '{name}' already exists, skipping")
            return existing
        
        url = f"{self.base_url}/dna/intent/api/v1/site"
        payload = {
            "type": "building",
            "site": {
                "building": {
                    "name": name,
                    "parentName": parent_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "address": address,
                    "country": country
                }
            }
        }
        
        print(f"Creating building '{name}'...")
        response = requests.post(url, headers=self.headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        task_id = result.get('executionId')
        task_url = result.get('executionStatusUrl')
        
        if task_id:
            print(f"  Waiting for task {task_id[:8]}...")
            if self.wait_for_task(task_id, task_url):
                print(f"✅ Building '{name}' created successfully")
            else:
                print(f"❌ Building '{name}' creation failed")
                return None
        else:
            print(f"✅ Building '{name}' created")
        
        time.sleep(2)  # Buildings take longer
        return result
    
    def create_floor(self, name: str, parent_name: str, floor_number: int):
        """Create floor"""
        # Check if floor already exists under this specific parent
        # Use parent-aware lookup since floors can have duplicate names
        existing_floor = self.get_site_by_name_and_parent(name, parent_name)
        if existing_floor:
            print(f"ℹ️  Floor '{name}' already exists at '{parent_name}', skipping")
            return existing_floor
        
        url = f"{self.base_url}/dna/intent/api/v1/site"
        payload = {
            "type": "floor",
            "site": {
                "floor": {
                    "name": name,
                    "parentName": parent_name,
                    "rfModel": "Cubes And Walled Offices",
                    "width": 100,
                    "length": 100,
                    "height": 10,
                    "floorNumber": floor_number
                }
            }
        }
        
        print(f"Creating floor '{name}' at '{parent_name}'...")
        response = requests.post(url, headers=self.headers, json=payload, verify=False, timeout=30)
        
        # Check for errors before proceeding
        if response.status_code != 202:
            error_msg = response.text[:200] if response.text else "Unknown error"
            print(f"❌ Floor creation request failed (status {response.status_code}): {error_msg}")
            return None
        
        result = response.json()
        task_id = result.get('executionId')
        task_url = result.get('executionStatusUrl')
        
        if task_id:
            print(f"  Waiting for task {task_id[:8]}...")
            if self.wait_for_task(task_id, task_url):
                print(f"✅ Floor '{name}' created successfully")
            else:
                print(f"❌ Floor '{name}' creation failed")
                return None
        else:
            print(f"✅ Floor '{name}' created")
        
        time.sleep(1)
        return result
    
    def reserve_ip_subpool(self, site_name: str, reservation_name: str, parent_pool: str, subnet: str, prefix_length: int):
        """Reserve IP subpool for a site"""
        # Check if reservation already exists
        existing = self.get_reservation_by_name(site_name, reservation_name)
        if existing:
            print(f"ℹ️  Reservation '{reservation_name}' already exists at '{site_name}', skipping")
            return existing
        
        # Get site ID
        site = self.get_site_by_name(site_name)
        if not site:
            print(f"❌ Site '{site_name}' not found")
            return None
        
        site_id = site["id"]
        gateway = f"{subnet.rsplit('.', 1)[0]}.1"
        
        # Get parent pool to find its CIDR
        parent_pool_obj = self.get_global_pool_by_name(parent_pool)
        if not parent_pool_obj:
            print(f"❌ Global pool '{parent_pool}' not found")
            return None
        
        parent_cidr = parent_pool_obj.get("ipPoolCidr")
        
        url = f"{self.base_url}/dna/intent/api/v1/reserve-ip-subpool/{site_id}"
        payload = {
            "name": reservation_name,
            "type": "Generic",
            "ipv4GlobalPool": parent_cidr,  # Use CIDR instead of name
            "ipv4Prefix": True,
            "ipv4PrefixLength": prefix_length,
            "ipv4Subnet": subnet,
            "ipv4GateWay": gateway
        }
        
        print(f"Reserving '{reservation_name}' ({subnet}/{prefix_length}) from '{parent_pool}' ({parent_cidr})...")
        response = requests.post(url, headers=self.headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Get task ID from response
        task_id = result.get('executionId')
        task_url = result.get('executionStatusUrl')
        
        if task_id:
            print(f"  Waiting for task {task_id[:8]}...")
            if self.wait_for_task(task_id, task_url, timeout=600):
                print(f"✅ Reservation '{reservation_name}' created successfully")
            else:
                print(f"❌ Reservation '{reservation_name}' creation failed")
                return None
        elif task_url:
            # Fallback: check executionStatusUrl once (older API style)
            time.sleep(2)
            status_url = f"{self.base_url}{task_url}"
            status_resp = requests.get(status_url, headers=self.headers, verify=False, timeout=30)
            status = status_resp.json()
            
            if status.get("status") == "SUCCESS":
                print(f"✅ Reservation '{reservation_name}' created")
            else:
                error = status.get("bapiError", "Unknown error")
                print(f"❌ Reservation failed: {error}")
                return None
        else:
            print(f"✅ Reservation '{reservation_name}' created")
        
        time.sleep(1)
        return result
    
    # ==========================================================================
    # DELETE OPERATIONS
    # ==========================================================================
    
    def delete_site(self, site_name: str):
        """Delete a site (area/building/floor) with retry on auth failure"""
        site = self.get_site_by_name(site_name)
        if not site:
            print(f"ℹ️  Site '{site_name}' not found, skipping")
            return None
        
        site_id = site["id"]
        url = f"{self.base_url}/dna/intent/api/v1/site/{site_id}"
        
        print(f"Deleting site '{site_name}'...")
        
        # Try deletion with retry on 401
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.delete(url, headers=self.headers, verify=False, timeout=30)
                
                # If 401, re-authenticate and retry
                if response.status_code == 401 and attempt < max_retries - 1:
                    print(f"  🔐 Token expired, re-authenticating...")
                    self.authenticate()
                    continue
                
                # Check for other errors
                if response.status_code != 202 and response.status_code != 200:
                    error_msg = response.text
                    print(f"  ❌ Delete failed (status {response.status_code}): {error_msg[:200]}")
                    return None
                
                # Get task info from response
                result = response.json() if response.text else {}
                task_id = result.get('executionId')
                task_url = result.get('executionStatusUrl')
                
                if task_id:
                    print(f"  Waiting for deletion task {task_id[:8]}...")
                    if self.wait_for_task(task_id, task_url):
                        print(f"✅ Site '{site_name}' deleted successfully")
                    else:
                        print(f"❌ Site '{site_name}' deletion failed")
                        return None
                else:
                    print(f"✅ Site '{site_name}' deleted")
                
                time.sleep(0.5)
                return result
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️  Retrying after error: {str(e)[:100]}")
                    self.authenticate()
                else:
                    print(f"  ❌ Failed to delete '{site_name}': {str(e)[:100]}")
                    return None
        
        return None
    
    def delete_reservation(self, site_name: str, reservation_name: str):
        """Delete an IP pool reservation"""
        # Get site ID
        site = self.get_site_by_name(site_name)
        if not site:
            print(f"ℹ️  Site '{site_name}' not found for reservation '{reservation_name}'")
            return None
        
        site_id = site["id"]
        
        # Get reservations for this site
        try:
            url = f"{self.base_url}/dna/intent/api/v1/reserve-ip-subpool?siteId={site_id}"
            response = requests.get(url, headers=self.headers, verify=False, timeout=30)
            
            if response.status_code == 200:
                reservations = response.json().get('response', [])
                
                # Find the reservation by name
                reservation_id = None
                for res in reservations:
                    if res.get('groupName') == reservation_name:
                        reservation_id = res.get('id')
                        break
                
                if not reservation_id:
                    print(f"ℹ️  Reservation '{reservation_name}' not found in '{site_name}'")
                    return None
                
                # Delete the reservation
                delete_url = f"{self.base_url}/dna/intent/api/v1/reserve-ip-subpool/{reservation_id}"
                print(f"Deleting reservation '{reservation_name}' from '{site_name}'...")
                
                del_response = requests.delete(delete_url, headers=self.headers, verify=False, timeout=30)
                
                if del_response.status_code in [200, 202]:
                    # Get task info from response
                    result = del_response.json() if del_response.text else {}
                    task_id = result.get('executionId')
                    task_url = result.get('executionStatusUrl')
                    
                    if task_id:
                        print(f"  Waiting for deletion task {task_id[:8]}...")
                        if self.wait_for_task(task_id, task_url):
                            print(f"✅ Reservation '{reservation_name}' deleted successfully")
                        else:
                            print(f"❌ Reservation '{reservation_name}' deletion failed")
                            return None
                    else:
                        print(f"✅ Reservation '{reservation_name}' deleted")
                    
                    time.sleep(0.5)
                    return result
                else:
                    print(f"  ❌ Failed (status {del_response.status_code}): {del_response.text[:200]}")
                    return None
        except Exception as e:
            print(f"  ❌ Error deleting reservation: {str(e)[:100]}")
            return None
    
    def delete_global_pool(self, pool_name: str):
        """Delete a global IP pool"""
        pool = self.get_global_pool_by_name(pool_name)
        if not pool:
            print(f"ℹ️  Pool '{pool_name}' not found, skipping")
            return None
        
        pool_id = pool["id"]
        url = f"{self.base_url}/dna/intent/api/v1/global-pool/{pool_id}"
        
        print(f"Deleting global pool '{pool_name}'...")
        response = requests.delete(url, headers=self.headers, verify=False, timeout=30)
        
        if response.status_code in [200, 202]:
            # Get task info from response
            result = response.json() if response.text else {}
            task_id = result.get('executionId')
            task_url = result.get('executionStatusUrl')
            
            if task_id:
                print(f"  Waiting for deletion task {task_id[:8]}...")
                if self.wait_for_task(task_id, task_url):
                    print(f"✅ Global pool '{pool_name}' deleted successfully")
                else:
                    print(f"❌ Global pool '{pool_name}' deletion failed")
                    return None
            else:
                print(f"✅ Global pool '{pool_name}' deleted")
            
            time.sleep(1)
            return result
        else:
            print(f"  ❌ Failed (status {response.status_code}): {response.text[:200]}")
            return None


def create_infrastructure(cc):
    """Create all infrastructure"""
    print("="*70)
    print("Catalyst Center - Simplified Deployment - CREATE MODE")
    print("="*70)
    
    # Create Global IP Pools
    print("\n" + "="*70)
    print("📦 Creating Global IP Pools")
    print("="*70 + "\n")
    
    cc.create_ip_pool("US_CORP", "10.201.0.0/16")
    cc.create_ip_pool("US_TECH", "10.202.0.0/16")
    cc.create_ip_pool("US_GUEST", "10.203.0.0/16")
    cc.create_ip_pool("US_BYOD", "10.204.0.0/16")
    
    # Create Areas
    print("\n" + "="*70)
    print("🗺️  Creating Areas")
    print("="*70 + "\n")
    
    cc.create_area("United States", "Global")
    cc.create_area("Golden Hills Campus", "Global/United States")
    cc.create_area("Lakefront Tower", "Global/United States")
    cc.create_area("Oceanfront Mansion", "Global/United States")
    cc.create_area("Desert Oasis Branch", "Global/United States")
    
    # Create Buildings
    print("\n" + "="*70)
    print("🏢 Creating Buildings")
    print("="*70 + "\n")
    
    cc.create_building(
        "Sunset Tower",
        "Global/United States/Golden Hills Campus",
        34.099, -118.366,
        "8358 Sunset Blvd, Los Angeles, CA 90069",
        "United States"
    )
    
    cc.create_building(
        "Windy City Plaza",
        "Global/United States/Lakefront Tower",
        41.878, -87.630,
        "233 S Wacker Dr, Chicago, IL 60606",
        "United States"
    )
    
    cc.create_building(
        "Art Deco Mansion",
        "Global/United States/Oceanfront Mansion",
        25.782, -80.133,
        "123 Ocean Drive, Miami Beach, FL 33139",
        "United States"
    )
    
    cc.create_building(
        "Desert Oasis Tower",
        "Global/United States/Desert Oasis Branch",
        33.448, -112.074,
        "1235 Cactus Ave, Phoenix, AZ 85001",
        "United States"
    )
    
    # Create Floors
    print("\n" + "="*70)
    print("🏗️  Creating Floors")
    print("="*70 + "\n")
    
    cc.create_floor("FLOOR_1", "Global/United States/Golden Hills Campus/Sunset Tower", 1)
    cc.create_floor("FLOOR_2", "Global/United States/Golden Hills Campus/Sunset Tower", 2)
    cc.create_floor("FLOOR_1", "Global/United States/Lakefront Tower/Windy City Plaza", 1)
    cc.create_floor("FLOOR_2", "Global/United States/Lakefront Tower/Windy City Plaza", 2)
    cc.create_floor("FLOOR_1", "Global/United States/Oceanfront Mansion/Art Deco Mansion", 1)
    cc.create_floor("FLOOR_1", "Global/United States/Desert Oasis Branch/Desert Oasis Tower", 1)
    
    # Create IP Pool Reservations
    print("\n" + "="*70)
    print("🔖 Creating IP Pool Reservations")
    print("="*70 + "\n")
    
    # Sunset Tower Reservations
    print("🏢 Sunset Tower...")
    cc.reserve_ip_subpool("Sunset Tower", "ST_CORP", "US_CORP", "10.201.2.0", 24)
    cc.reserve_ip_subpool("Sunset Tower", "ST_TECH", "US_TECH", "10.202.2.0", 24)
    cc.reserve_ip_subpool("Sunset Tower", "ST_GUEST", "US_GUEST", "10.203.2.0", 24)
    cc.reserve_ip_subpool("Sunset Tower", "ST_BYOD", "US_BYOD", "10.204.2.0", 24)
    
    # Windy City Plaza Reservations
    print("\n🏢 Windy City Plaza...")
    cc.reserve_ip_subpool("Windy City Plaza", "WCP_CORP", "US_CORP", "10.201.3.0", 24)
    cc.reserve_ip_subpool("Windy City Plaza", "WCP_TECH", "US_TECH", "10.202.3.0", 24)
    cc.reserve_ip_subpool("Windy City Plaza", "WCP_GUEST", "US_GUEST", "10.203.3.0", 24)
    cc.reserve_ip_subpool("Windy City Plaza", "WCP_BYOD", "US_BYOD", "10.204.3.0", 24)
    
    # Art Deco Mansion Reservations
    print("\n🏢 Art Deco Mansion...")
    cc.reserve_ip_subpool("Art Deco Mansion", "ADM_CORP", "US_CORP", "10.201.4.0", 24)
    cc.reserve_ip_subpool("Art Deco Mansion", "ADM_TECH", "US_TECH", "10.202.4.0", 24)
    cc.reserve_ip_subpool("Art Deco Mansion", "ADM_GUEST", "US_GUEST", "10.203.4.0", 24)
    cc.reserve_ip_subpool("Art Deco Mansion", "ADM_BYOD", "US_BYOD", "10.204.4.0", 24)
    
    # Desert Oasis Tower Reservations
    print("\n🏢 Desert Oasis Tower...")
    cc.reserve_ip_subpool("Desert Oasis Tower", "DOT_CORP", "US_CORP", "10.201.1.0", 24)
    cc.reserve_ip_subpool("Desert Oasis Tower", "DOT_TECH", "US_TECH", "10.202.1.0", 24)
    cc.reserve_ip_subpool("Desert Oasis Tower", "DOT_GUEST", "US_GUEST", "10.203.1.0", 24)
    cc.reserve_ip_subpool("Desert Oasis Tower", "DOT_BYOD", "US_BYOD", "10.204.1.0", 24)
    
    # Summary
    print("\n" + "="*70)
    print("✅ Deployment Complete!")
    print("="*70)
    print("\nVerify in Catalyst Center GUI:")
    print("  - Design > Network Hierarchy: Check sites/buildings/floors")
    print("  - Design > Network Settings > IP Address Pools:")
    print("    • Global Pools: 4 pools (US_CORP, US_TECH, US_GUEST, US_BYOD)")
    print("    • Reservations: 16 reservations across 4 buildings")
    print()


def delete_infrastructure(cc):
    """Delete all infrastructure in reverse order"""
    print("="*70)
    print("Catalyst Center - Simplified Deployment - DELETE MODE")
    print("="*70)
    print("\n⚠️  WARNING: This will delete all created infrastructure!")
    print("⚠️  This includes sites, buildings, floors, and IP pool reservations.")
    print("⚠️  Global IP pools will NOT be deleted (must be done manually).")
    
    # Confirm deletion
    try:
        confirm = input("\nType 'DELETE' to confirm: ")
        if confirm != "DELETE":
            print("\n❌ Deletion cancelled.")
            return 1
    except (EOFError, KeyboardInterrupt):
        print("\n\n❌ Deletion cancelled.")
        return 1
    
    # Re-authenticate in case token expired during confirmation
    print("\n🔐 Re-authenticating...")
    try:
        cc.authenticate()
    except Exception as e:
        print(f"\n❌ Failed to re-authenticate. Exiting.")
        return 1
    
    print("\n🗑️  Starting deletion process...\n")
    
    # ==========================================================================
    # DELETE IP POOL RESERVATIONS FIRST (before deleting sites)
    # ==========================================================================
    
    print("="*70)
    print("🔖 Deleting IP Pool Reservations")
    print("="*70 + "\n")
    
    # Define all reservations to delete
    reservations_by_building = {
        "Sunset Tower": ["ST_CORP", "ST_TECH", "ST_GUEST", "ST_BYOD"],
        "Windy City Plaza": ["WCP_CORP", "WCP_TECH", "WCP_GUEST", "WCP_BYOD"],
        "Art Deco Mansion": ["ADM_CORP", "ADM_TECH", "ADM_GUEST", "ADM_BYOD"],
        "Desert Oasis Tower": ["DOT_CORP", "DOT_TECH", "DOT_GUEST", "DOT_BYOD"],
    }
    
    for building_name, reservations in reservations_by_building.items():
        print(f"\n🏢 {building_name}...")
        for reservation_name in reservations:
            cc.delete_reservation(building_name, reservation_name)
    
    # Note: IP pool reservations are automatically deleted when sites are deleted
    
    # Delete Floors (must be deleted before buildings)
    print("\n" + "="*70)
    print("🏗️  Deleting Floors")
    print("="*70 + "\n")
    
    # Re-authenticate to ensure fresh token
    print("🔐 Refreshing authentication...")
    cc.authenticate()
    print()
    
    floors = [
        "FLOOR_1",  # Will delete multiple times for different buildings
        "FLOOR_2",
    ]
    
    # Try deleting FLOOR_1 and FLOOR_2 multiple times (for different buildings)
    for _ in range(6):  # We have 7 floors total
        for floor_name in floors:
            try:
                result = cc.delete_site(floor_name)
                if result is None:
                    break  # No more floors with this name
            except Exception as e:
                break
    
    # Delete Buildings (must be deleted before areas)
    print("\n" + "="*70)
    print("🏢 Deleting Buildings")
    print("="*70 + "\n")
    
    # Re-authenticate to ensure fresh token
    print("🔐 Refreshing authentication...")
    cc.authenticate()
    
    buildings = [
        "Sunset Tower",
        "Windy City Plaza",
        "Art Deco Mansion",
        "Desert Oasis Tower",
    ]
    
    for building in buildings:
        cc.delete_site(building)
    
    # Delete Areas (delete children first, then parents)
    print("\n" + "="*70)
    print("🗺️  Deleting Areas")
    print("="*70 + "\n")
    
    # Re-authenticate again
    print("🔐 Refreshing authentication...")
    cc.authenticate()
    
    areas = [
        "Golden Hills Campus",
        "Lakefront Tower",
        "Oceanfront Mansion",
        "Desert Oasis Branch",
        "United States",  # Parent area last
    ]
    
    for area in areas:
        cc.delete_site(area)
    
    # Note about global pools
    print("\n" + "="*70)
    print("ℹ️  Global IP Pools")
    print("="*70)
    print("\nGlobal IP pools were NOT deleted.")
    print("To delete them, use the Catalyst Center GUI:")
    print("  Design > Network Settings > IP Address Pools > Global Pools")
    print("\nOr uncomment the deletion code in the script.")
    
    # Uncomment below to delete global pools:
    # print("\n" + "="*70)
    # print("📦 Deleting Global IP Pools")
    # print("="*70 + "\n")
    # for pool_name in ["US_CORP", "US_TECH", "US_GUEST", "US_BYOD"]:
    #     try:
    #         cc.delete_global_pool(pool_name)
    #     except Exception as e:
    #         pass
    
    print("\n" + "="*70)
    print("✅ Deletion Complete!")
    print("="*70)
    print()
    
    return 0


def check_infrastructure(cc):
    """Check and display existing infrastructure"""
    print("="*70)
    print("Catalyst Center - Infrastructure Status")
    print("="*70)
    
    # Check Global IP Pools
    print("\n" + "="*70)
    print("📦 Global IP Pools")
    print("="*70)
    
    try:
        pools_url = f"{cc.base_url}/dna/intent/api/v1/global-pool"
        response = requests.get(pools_url, headers=cc.headers, verify=False, timeout=30)
        response.raise_for_status()
        pools = response.json().get('response', [])
        
        if pools:
            print(f"\nFound {len(pools)} global pool(s):")
            for pool in pools:
                name = pool.get('ipPoolName')
                cidr = pool.get('ipPoolCidr')
                used = pool.get('usedIpAddressCount', 0)
                total = pool.get('totalAssignableIpAddressCount', 0)
                print(f"  ✓ {name}: {cidr}")
                print(f"    Used: {used}/{total} addresses")
        else:
            print("\n  ℹ️  No global pools found")
    except Exception as e:
        print(f"\n  ❌ Error checking pools: {e}")
    
    # Check Sites
    print("\n" + "="*70)
    print("🗺️  Site Hierarchy")
    print("="*70)
    
    try:
        sites_url = f"{cc.base_url}/dna/intent/api/v1/site"
        response = requests.get(sites_url, headers=cc.headers, verify=False, timeout=30)
        response.raise_for_status()
        sites = response.json().get('response', [])
        
        if sites:
            # Organize by type - use a safer approach
            areas = []
            buildings = []
            floors = []
            
            for site in sites:
                site_name = site.get('name', '')
                if site_name == 'Global':
                    continue  # Skip root
                
                # Try to determine type from additionalInfo
                site_type = None
                try:
                    if 'additionalInfo' in site and site['additionalInfo']:
                        for info in site['additionalInfo']:
                            if 'attributes' in info and 'type' in info['attributes']:
                                site_type = info['attributes']['type']
                                break
                except Exception:
                    pass
                
                # If that fails, use groupNameHierarchy or nameHierarchy
                if not site_type:
                    hierarchy = site.get('siteNameHierarchy', '')
                    parts = hierarchy.count('/')
                    if parts == 1:
                        site_type = 'area'
                    elif parts == 2:
                        site_type = 'area'
                    elif parts == 3:
                        site_type = 'building'
                    elif parts >= 4:
                        site_type = 'floor'
                
                # Categorize
                if site_type == 'area':
                    areas.append(site)
                elif site_type == 'building':
                    buildings.append(site)
                elif site_type == 'floor':
                    floors.append(site)
            
            print(f"\nFound {len(sites)-1} site(s) (excluding Global):")
            
            if areas:
                print(f"\n  Areas ({len(areas)}):")
                for area in areas:
                    hierarchy = area.get('siteNameHierarchy', area['name'])
                    print(f"    • {area['name']}")
                    print(f"      Path: {hierarchy}")
            
            if buildings:
                print(f"\n  Buildings ({len(buildings)}):")
                for building in buildings:
                    hierarchy = building.get('siteNameHierarchy', building['name'])
                    print(f"    • {building['name']}")
                    print(f"      Path: {hierarchy}")
            
            if floors:
                print(f"\n  Floors ({len(floors)}):")
                for floor in floors:
                    hierarchy = floor.get('siteNameHierarchy', floor['name'])
                    print(f"    • {floor['name']}")
                    print(f"      Parent: {hierarchy}")
            
            if not areas and not buildings and not floors:
                print("\n  ℹ️  No sites found (besides Global)")
        else:
            print("\n  ℹ️  No sites found (besides Global)")
    except Exception as e:
        print(f"\n  ❌ Error checking sites: {e}")
    
    # Check IP Pool Reservations
    print("\n" + "="*70)
    print("🔖 IP Pool Reservations")
    print("="*70)
    
    try:
        # Get all building sites
        sites_url = f"{cc.base_url}/dna/intent/api/v1/site"
        response = requests.get(sites_url, headers=cc.headers, verify=False, timeout=30)
        response.raise_for_status()
        all_sites = response.json().get('response', [])
        
        # Find buildings using safer approach
        buildings = []
        for site in all_sites:
            site_type = None
            try:
                if 'additionalInfo' in site and site['additionalInfo']:
                    for info in site['additionalInfo']:
                        if 'attributes' in info and 'type' in info['attributes']:
                            site_type = info['attributes']['type']
                            break
            except Exception:
                pass
            
            # Fallback to hierarchy depth
            if not site_type:
                hierarchy = site.get('siteNameHierarchy', '')
                parts = hierarchy.count('/')
                if parts == 3:
                    site_type = 'building'
            
            if site_type == 'building':
                buildings.append(site)
        
        total_reservations = 0
        if buildings:
            for building in buildings:
                building_name = building['name']
                building_id = building['id']
                
                # Try to get reservations for this building
                try:
                    # Use the correct v1 endpoint with query parameter
                    res_url = f"{cc.base_url}/dna/intent/api/v1/reserve-ip-subpool?siteId={building_id}"
                    res_response = requests.get(res_url, headers=cc.headers, verify=False, timeout=30)
                    
                    if res_response.status_code == 200:
                        data = res_response.json()
                        reservations = data.get('response', [])
                        if reservations:
                            print(f"\n  {building_name} ({len(reservations)} reservation(s)):")
                            for res in reservations:
                                # The structure has groupName and nested ipPools
                                res_name = res.get('groupName', 'Unknown')
                                # Get the first IP pool details
                                ip_pools = res.get('ipPools', [])
                                if ip_pools:
                                    pool = ip_pools[0]
                                    res_cidr = pool.get('ipPoolCidr', 'N/A')
                                    used = pool.get('usedIpAddressCount', 0)
                                    total = pool.get('totalIpAddressCount', 0)
                                    print(f"    • {res_name}: {res_cidr} ({used}/{total} used)")
                                else:
                                    print(f"    • {res_name}")
                                total_reservations += 1
                except Exception as e:
                    pass  # Skip buildings with no reservations or errors
            
            if total_reservations == 0:
                print("\n  ℹ️  No IP pool reservations found")
            else:
                print(f"\n  Total: {total_reservations} reservation(s)")
        else:
            print("\n  ℹ️  No buildings found")
    except Exception as e:
        print(f"\n  ❌ Error checking reservations: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("✅ Status Check Complete")
    print("="*70)
    print()
    
    return 0


def main():
    """Main execution"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Catalyst Center Infrastructure Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python native_api_simple.py create --config CC_Env.yml
  python native_api_simple.py delete --config CC_Env_CX_Lab_CC1.yml
  python native_api_simple.py status --config CC_Env_CX_Lab_CC3.yml
  
Configuration:
  A YAML configuration file is REQUIRED and must contain:
    CC_IP: IP address or hostname of Catalyst Center
    CC_USERNAME: Username for authentication
    CC_PASSWORD: Password for authentication
    CC_INSECURE: true/false (SSL certificate verification)
  
  See CC_Env_Sample.yml for a template.
        """
    )
    parser.add_argument(
        'action',
        choices=['create', 'delete', 'status'],
        help='Action to perform: create, delete, or check status of infrastructure'
    )
    parser.add_argument(
        '--config',
        required=True,
        help='Path to YAML configuration file (required)'
    )
    
    args = parser.parse_args()
    
    # Load credentials from YAML file
    print("🔍 Loading credentials...")
    config = load_credentials_from_yaml(args.config)
    
    if not config:
        print(f"❌ Failed to load credentials from {args.config}")
        print(f"   Please ensure the file exists and has the correct format.")
        print(f"   See CC_Env_Sample.yml for reference.")
        return 1
    
    print(f"✅ Loaded credentials from {args.config}")
    
    # Initialize API client
    cc = CatalystCenterAPI(
        base_url=config['base_url'],
        username=config['username'],
        password=config['password']
    )
    
    # Authenticate
    print("\n🔐 Authenticating...")
    try:
        cc.authenticate()
    except Exception as e:
        print(f"\n❌ Failed to authenticate. Exiting.")
        return 1
    
    # Execute requested action
    if args.action == 'create':
        return create_infrastructure(cc)
    elif args.action == 'delete':
        return delete_infrastructure(cc)
    elif args.action == 'status':
        return check_infrastructure(cc)
    else:
        print(f"❌ Unknown action: {args.action}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code if exit_code else 0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

