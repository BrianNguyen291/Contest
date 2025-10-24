#!/usr/bin/env python3
"""
Test script for the FastAPI backend
"""

import asyncio
import sys
import os
import time
import requests
from threading import Thread

# Add current directory to path
sys.path.append('.')

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AA Flight Scraper Backend API")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test airports endpoint
    try:
        response = requests.get(f"{base_url}/api/airports", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Airports endpoint working - {len(data['airports'])} airports available")
        else:
            print(f"❌ Airports endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Airports endpoint error: {e}")
    
    # Test search endpoint
    try:
        search_data = {
            "origin": "LAX",
            "destination": "JFK", 
            "date": "2025-12-15",
            "passengers": 1
        }
        response = requests.post(f"{base_url}/api/search", json=search_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ Search endpoint working")
                print(f"   Found {data['data']['total_results']} flights")
                print(f"   Execution time: {data['execution_time']:.2f}s")
            else:
                print(f"❌ Search failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
    
    print("\n🎉 Backend testing complete!")
    return True

if __name__ == "__main__":
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    # Test the backend
    test_backend()
