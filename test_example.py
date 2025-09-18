#!/usr/bin/env python3
"""
Example usage and testing for the Tunnel URL Monitor

This demonstrates how to use the monitor programmatically and test its components.
"""

import os
import tempfile
import time
from pathlib import Path

# Example of how to use the monitor programmatically
def create_sample_log_file():
    """Create a sample log file with tunnel URLs for testing."""

    sample_log_content = """
2025-09-17 10:00:01 INFO: Starting cloudflared tunnel...
2025-09-17 10:00:02 INFO: Tunnel connection established
2025-09-17 10:00:03 INFO: Your tunnel is now available at: https://abc123.trycloudflare.com
2025-09-17 10:00:04 INFO: Metrics server started on localhost:60123
2025-09-17 10:00:05 INFO: Registered tunnel connection connIndex=0 connection=abc123
2025-09-17 10:01:15 INFO: Updated tunnel URL: https://xyz789.trycloudflare.com
2025-09-17 10:02:30 INFO: Custom domain tunnel: https://api.myapp.com
2025-09-17 10:03:45 INFO: Worker tunnel available: https://my-worker.example.workers.dev
"""

    # Create temporary log file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_tunnel.log', delete=False)
    temp_file.write(sample_log_content)
    temp_file.close()

    return temp_file.name

def test_url_extraction():
    """Test URL extraction functionality."""
    print("🧪 Testing URL extraction...")

    # Import our classes (normally you'd import from the main file)
    import sys
    sys.path.append('.')

    from tunnel_url_monitor import TunnelURLExtractor

    extractor = TunnelURLExtractor()

    # Create sample log
    log_file = create_sample_log_file()

    with open(log_file, 'r') as f:
        content = f.read()

    urls = extractor.extract_urls(content)

    print(f"Found {len(urls)} tunnel URLs:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")

    # Cleanup
    os.unlink(log_file)

    return urls

def test_url_shortening():
    """Test URL shortening functionality."""
    print("\n🔗 Testing URL shortening...")

    from tunnel_url_monitor import URLShortener

    shortener = URLShortener()
    test_url = "https://example.trycloudflare.com"

    shortened = shortener.shorten_url(test_url)
    print(f"Original:  {test_url}")
    print(f"Shortened: {shortened}")

    return shortened

def demonstrate_monitoring():
    """Demonstrate file monitoring (without actually running the monitor)."""
    print("\n👁️  Monitor Configuration Example:")

    config = {
        "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN",
        "watch_directories": [".", "/var/log"],
        "file_extensions": [".log", ".txt"],
        "filename_patterns": ["*tunnel*", "*cloudflare*"]
    }

    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    print("\nThe monitor would watch these locations for file changes:")
    print("- Current directory (.) for any files matching patterns")
    print("- /var/log directory for system logs")
    print("- Files ending in .log or .txt")
    print("- Files containing 'tunnel' or 'cloudflare' in filename")

if __name__ == "__main__":
    print("🚀 Tunnel URL Monitor - Test Examples\n")

    try:
        # Test URL extraction
        urls = test_url_extraction()

        # Test URL shortening (might fail without internet)
        try:
            shortened = test_url_shortening()
        except Exception as e:
            print(f"URL shortening test failed (expected without internet): {e}")

        # Show monitoring concept
        demonstrate_monitoring()

        print("\n✅ Tests completed!")
        print("\nTo run the actual monitor:")
        print("1. Set your Discord webhook URL in environment variable:")
        print("   export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/....'")
        print("2. Run: python tunnel_url_monitor.py")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure tunnel_url_monitor.py is in the same directory")
    except Exception as e:
        print(f"❌ Test error: {e}")
