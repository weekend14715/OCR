#!/usr/bin/env python3
"""
Test script để debug license activation
"""

import requests
import json
from license_client_integrated import LicenseClient

def test_server_connection():
    """Test kết nối đến server"""
    print("=== TESTING SERVER CONNECTION ===")
    
    server_url = "https://vietnamese-ocr-license.onrender.com"
    
    # Test các endpoint khác nhau
    endpoints = [
        "/",
        "/health", 
        "/api/health",
        "/api/validate"
    ]
    
    for endpoint in endpoints:
        try:
            url = server_url + endpoint
            print(f"\nTesting: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"Text Response: {response.text[:200]}...")
            else:
                print(f"Error Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"Connection Error: {e}")
        except Exception as e:
            print(f"Other Error: {e}")

def test_license_validation():
    """Test license validation"""
    print("\n=== TESTING LICENSE VALIDATION ===")
    
    client = LicenseClient()
    
    # Test với license key giả
    test_license = "TEST-1234-5678-9012"
    print(f"Testing license: {test_license}")
    
    result = client.verify_license_online(test_license)
    print(f"Result: {json.dumps(result, indent=2)}")

def test_hardware_id():
    """Test hardware ID generation"""
    print("\n=== TESTING HARDWARE ID ===")
    
    client = LicenseClient()
    print(f"Hardware ID: {client.hardware_id}")
    print(f"License file path: {client.license_file}")

if __name__ == "__main__":
    test_server_connection()
    test_license_validation() 
    test_hardware_id()
