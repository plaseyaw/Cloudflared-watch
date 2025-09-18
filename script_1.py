# Let me also create a simple configuration file example and a requirements.txt file

# Create example configuration file
config_example = {
    "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN",
    "discord_username": "Tunnel Monitor",
    "watch_directories": [
        ".",
        "/var/log",
        "~/logs",
        "~/cloudflared"
    ],
    "file_extensions": [".log", ".txt", ".out"],
    "filename_patterns": ["*tunnel*", "*cloudflare*", "*cloudflared*"],
    "monitor_log_file": "tunnel_monitor.log",
    "recursive_monitoring": True
}

import json
with open('tunnel_monitor_config_example.json', 'w') as f:
    json.dump(config_example, f, indent=2)

# Create requirements.txt
requirements = """pyshorteners>=1.0.1
watchdog>=2.1.0
requests>=2.25.0
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements)

# Create a simple setup script
setup_script = '''#!/bin/bash
# Setup script for Tunnel URL Monitor

echo "🚀 Setting up Cloudflare Tunnel URL Monitor..."

# Install required packages
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Create example config if it doesn't exist
if [ ! -f "tunnel_monitor_config.json" ]; then
    echo "📋 Creating example configuration file..."
    cp tunnel_monitor_config_example.json tunnel_monitor_config.json
    echo "⚠️  Please edit tunnel_monitor_config.json and add your Discord webhook URL!"
fi

# Make the Python script executable
chmod +x tunnel_url_monitor.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit tunnel_monitor_config.json and add your Discord webhook URL"
echo "2. Run: python tunnel_url_monitor.py"
echo ""
echo "For testing:"
echo "  python tunnel_url_monitor.py --test-webhook"
echo "  python tunnel_url_monitor.py --test-file your_log_file.log"
'''

with open('setup.sh', 'w') as f:
    f.write(setup_script)

print("✅ Created additional files:")
print("  - tunnel_monitor_config_example.json (example configuration)")
print("  - requirements.txt (Python dependencies)")
print("  - setup.sh (setup script)")