# Cloudflare Tunnel URL Monitor

Automatically monitor log files for Cloudflare tunnel URLs, shorten them using pyshorteners, and send notifications to Discord webhooks when new URLs are detected.

## Features

- 🔍 **Real-time Log Monitoring**: Uses Python watchdog to monitor file changes
- 🔗 **URL Shortening**: Automatically shortens tunnel URLs using multiple services
- 📢 **Discord Notifications**: Sends formatted notifications to Discord webhooks
- 🎯 **Smart Detection**: Recognizes various Cloudflare tunnel URL patterns
- ⚙️ **Configurable**: Customizable file patterns, directories, and settings
- 🔄 **Fallback Support**: Multiple URL shortening services with automatic fallback

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install pyshorteners watchdog requests
   ```

2. **Set up Discord webhook:**
   ```bash
   echo "DISCORD_WEBHOOK_URL=[webhookurl]" > .env
   ```
3. **Run the monitor:**
   ```bash
   python tunnel_url_monitor.py
   ```

## Configuration

Edit `tunnel_monitor_config.json` to customize:

```json
{
  "watch_directories": [".", "/var/log", "~/logs"],
  "file_extensions": [".log", ".txt", ".out"],
  "filename_patterns": ["*tunnel*", "*cloudflare*", "*cloudflared*"],
  "recursive_monitoring": true
}
```

## Usage Examples

```bash
# Start monitoring
python tunnel_url_monitor.py

# Test Discord webhook
python tunnel_url_monitor.py --test-webhook

# Test URL extraction on specific file
python tunnel_url_monitor.py --test-file /path/to/logfile.log

# Use custom config file
python tunnel_url_monitor.py --config my_config.json
```

## Supported URL Patterns

The monitor detects various Cloudflare tunnel URL formats:
- `https://xxx.trycloudflare.com`
- `https://xxx.workers.dev`
- `https://xxx.cfargotunnel.com`
- Custom domain tunnels
- URLs mentioned in log entries

## Dependencies

- `pyshorteners` - URL shortening services
- `watchdog` - File system monitoring
- `requests` - HTTP requests for Discord webhooks

## License

MIT License - feel free to modify and use as needed.
