#!/usr/bin/env python3
"""
Test script to verify config.py loads .env variables correctly.
Run this script to test configuration loading.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import config
    
    print("=" * 50)
    print("Configuration Test")
    print("=" * 50)
    
    # Test loading environment variables
    print(f"\nOPENAI_API_KEY: {'✓ Set' if config.OPENAI_API_KEY else '✗ Not set'}")
    if config.OPENAI_API_KEY:
        print(f"  Value: {config.OPENAI_API_KEY[:10]}...{config.OPENAI_API_KEY[-4:]}")
    
    print(f"\nFIRECRAWL_API_KEY: {'✓ Set' if config.FIRECRAWL_API_KEY else '✗ Not set'}")
    if config.FIRECRAWL_API_KEY:
        print(f"  Value: {config.FIRECRAWL_API_KEY[:10]}...{config.FIRECRAWL_API_KEY[-4:]}")
    
    print(f"\nDATABASE_URL: {'✓ Set' if config.DATABASE_URL else '✗ Not set'}")
    if config.DATABASE_URL:
        # Don't print full URL for security
        print(f"  Value: {config.DATABASE_URL.split('@')[0]}@...")
    
    print(f"\nFLASK_ENV: {config.FLASK_ENV}")
    print(f"FLASK_DEBUG: {config.FLASK_DEBUG}")
    
    # Test validation
    print("\n" + "=" * 50)
    print("Testing validation...")
    print("=" * 50)
    
    try:
        config.validate_config()
        print("\n✓ Configuration validation passed!")
        print("All required environment variables are set.")
    except ValueError as e:
        print(f"\n✗ Configuration validation failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Configuration test completed successfully!")
    print("=" * 50)
    
except ImportError as e:
    print(f"Error importing config: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
