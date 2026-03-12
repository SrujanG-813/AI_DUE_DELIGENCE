#!/usr/bin/env python3
"""
Health check script for Railway deployment
"""

import requests
import sys
import os

def check_health():
    """Check if the application is healthy"""
    port = os.getenv("PORT", "8000")
    url = f"http://localhost:{port}/api/health"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('status', 'unknown')}")
            print(f"   Provider: {data.get('provider', 'none')}")
            print(f"   API Key: {'✅' if data.get('api_key_configured') else '❌'}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)