#!/bin/bash
# Setup script for Tunnel URL Monitor

echo "🚀 Setting up Cloudflare Tunnel URL Monitor..."

# Install required packages
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Create example config if it doesn't exist
if [ ! -f "tunnel_monitor_config.json" ]; then
  echo "📋 Creating example configuration file..."
  cp tunnel_monitor_config_example.json tunnel_monitor_config.json
  echo "⚠️  Please edit .env and add your Discord webhook URL!"
fi

# Create dotenv file
touch .env
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
