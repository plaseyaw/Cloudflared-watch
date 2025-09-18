#!/usr/bin/env python3
"""
Cloudflare Tunnel URL Monitor & Discord Webhook Notifier

This program monitors log files for Cloudflare tunnel URLs, shortens them using pyshorteners,
and sends notifications to Discord webhooks when URLs are detected or updated.

Requirements:
- pip install pyshorteners watchdog requests

Author: Generated for tunnel URL monitoring automation
"""

import os
import re
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

import requests
import pyshorteners
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
load_dotenv()


class TunnelURLExtractor:
    """Extract Cloudflare tunnel URLs from log content using various patterns."""

    # Common Cloudflare tunnel URL patterns
    TUNNEL_URL_PATTERNS = [
        # Standard tunnel URLs
        r'https://[\w-]+\.trycloudflare\.com',
        r'https://[\w-]+\.[\w-]+\.workers\.dev',
        # Custom domain tunnels  
        r'https://[\w.-]+\.cfargotunnel\.com',
        # General HTTPS URLs that might be tunnel endpoints
        r'https://[\w.-]+\.tunnel\.[\w.-]+',
        # URLs with tunnel-like subdomains
        r'https://tunnel-[\w-]+\.[\w.-]+',
        # Direct tunnel references in logs
        r'(?:tunnel|endpoint|url)[\s:=]+["\']?(https://[\w.-]+)["\']?',
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.TUNNEL_URL_PATTERNS]

    def extract_urls(self, content: str) -> list:
        """Extract all tunnel URLs from content."""
        urls = set()

        for pattern in self.compiled_patterns:
            matches = pattern.findall(content)
            for match in matches:
                # Handle tuple results from capturing groups
                url = match if isinstance(match, str) else match[0] if match else None
                if url and url.startswith('https://'):
                    urls.add(url)

        return list(urls)


class URLShortener:
    """Handle URL shortening with multiple service fallbacks."""

    def __init__(self):
        self.shortener = pyshorteners.Shortener()
        # List of services to try in order of preference
        self.services = ['tinyurl', 'chilpit', 'osdb']

    def shorten_url(self, url: str) -> Optional[str]:
        """Attempt to shorten URL with fallback services."""
        for service_name in self.services:
            try:
                service = getattr(self.shortener, service_name, None)
                if service:
                    shortened = service.short(url)
                    logging.info(f"Successfully shortened URL using {service_name}: {shortened}")
                    return shortened
            except Exception as e:
                logging.warning(f"Failed to shorten URL with {service_name}: {e}")
                continue

        logging.error(f"Failed to shorten URL with all services: {url}")
        return url  # Return original URL if all services fail


class DiscordWebhook:
    """Handle Discord webhook notifications."""

    def __init__(self, webhook_url: str, username: str = "Tunnel Monitor"):
        self.webhook_url = webhook_url
        self.username = username

    def send_message(self, content: str, embed: Optional[Dict[str, Any]] = None) -> bool:
        """Send message to Discord webhook."""
        payload = {
            "content": content,
            "username": self.username
        }

        if embed:
            payload["embeds"] = [embed]

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully sent Discord message: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Discord message: {e}")
            return False

    def send_tunnel_notification(self, original_url: str, shortened_url: str, 
                               log_file: str, timestamp: str = None) -> bool:
        """Send formatted tunnel URL notification."""
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create embed for better formatting
        embed = {
            "title": "🔗 New Tunnel URL Detected",
            "color": 0x00d4aa,  # Cloudflare orange color
            "fields": [
                {
                    "name": "📋 Shortened URL",
                    "value": f"[{shortened_url}]({shortened_url})",
                    "inline": False
                },
                {
                    "name": "🔗 Original URL", 
                    "value": f"```{original_url}```",
                    "inline": False
                },
                {
                    "name": "📁 Log File",
                    "value": f"`{log_file}`",
                    "inline": True
                },
                {
                    "name": "⏰ Detected At",
                    "value": f"`{timestamp}`",
                    "inline": True
                }
            ],
            "footer": {
                "text": "Cloudflare Tunnel Monitor"
            }
        }

        content = f"**New tunnel URL detected and shortened!**\n**Quick Access:** {shortened_url}"

        return self.send_message(content, embed)


class TunnelLogHandler(FileSystemEventHandler):
    """Handle file system events for tunnel log monitoring."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.url_extractor = TunnelURLExtractor()
        self.url_shortener = URLShortener()
        self.discord_webhook = DiscordWebhook(
            config['discord_webhook_url'],
            config.get('discord_username', 'Tunnel Monitor')
        )
        self.processed_urls = set()  # Track already processed URLs
        self.last_modified_times = {}  # Track file modification times

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.get('monitor_log_file', 'tunnel_monitor.log')),
                logging.StreamHandler()
            ]
        )

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = event.src_path

        # Check if this is a file we're monitoring
        if not self.should_monitor_file(file_path):
            return

        # Avoid processing the same modification multiple times
        current_time = time.time()
        last_time = self.last_modified_times.get(file_path, 0)
        if current_time - last_time < 1:  # Debounce: ignore changes within 1 second
            return

        self.last_modified_times[file_path] = current_time

        logging.info(f"Detected modification in: {file_path}")
        self.process_log_file(file_path)

    def should_monitor_file(self, file_path: str) -> bool:
        """Determine if file should be monitored based on config."""
        file_path_obj = Path(file_path)

        # Check file extensions
        allowed_extensions = self.config.get('file_extensions', ['.log', '.txt'])
        if file_path_obj.suffix.lower() not in allowed_extensions:
            return False

        # Check file name patterns
        filename_patterns = self.config.get('filename_patterns', ['*tunnel*', '*cloudflare*'])
        filename_lower = file_path_obj.name.lower()

        for pattern in filename_patterns:
            pattern_lower = pattern.lower().replace('*', '')
            if pattern_lower in filename_lower:
                return True

        return False

    def process_log_file(self, file_path: str):
        """Process log file for tunnel URLs."""
        try:
            # Read recent content (last N lines to avoid processing entire large logs)
            content = self.read_recent_content(file_path)
            if not content:
                return

            # Extract URLs
            urls = self.url_extractor.extract_urls(content)

            for url in urls:
                if url not in self.processed_urls:
                    self.handle_new_url(url, file_path)
                    self.processed_urls.add(url)

        except Exception as e:
            logging.error(f"Error processing log file {file_path}: {e}")

    def read_recent_content(self, file_path: str, max_lines: int = 100) -> str:
        """Read recent content from log file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Get last max_lines
                recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
                return ''.join(recent_lines)
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return ""

    def handle_new_url(self, url: str, log_file: str):
        """Handle discovery of new tunnel URL."""
        logging.info(f"Processing new tunnel URL: {url}")

        # Shorten URL
        shortened_url = self.url_shortener.shorten_url(url)

        # Send Discord notification
        success = self.discord_webhook.send_tunnel_notification(
            original_url=url,
            shortened_url=shortened_url,
            log_file=log_file
        )

        if success:
            logging.info(f"Successfully notified Discord about URL: {shortened_url}")
        else:
            logging.error(f"Failed to notify Discord about URL: {url}")


class TunnelMonitor:
    """Main tunnel monitoring application."""

    def __init__(self, config_file: str = 'tunnel_monitor_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.observer = Observer()
        self.event_handler = TunnelLogHandler(self.config)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "discord_webhook_url": os.getenv("DISCORD_WEBHOOK_URL", ""),
            "discord_username": "Tunnel Monitor",
            "watch_directories": [
                ".",
                "/var/log",
                "~/logs"
            ],
            "file_extensions": [".log", ".txt", ".out"],
            "filename_patterns": ["*tunnel*", "*cloudflare*", "*cloudflared*"],
            "monitor_log_file": "tunnel_monitor.log",
            "recursive_monitoring": True
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default config file: {self.config_file}")
                print("Please edit the config file and set your Discord webhook URL!")

        except Exception as e:
            logging.error(f"Error loading config: {e}")

        return default_config

    def validate_config(self) -> bool:
        """Validate configuration."""
        if not self.config.get('discord_webhook_url'):
            print("ERROR: Discord webhook URL not configured!")
            print("Please set DISCORD_WEBHOOK_URL environment variable or edit config file.")
            return False

        return True

    def start_monitoring(self):
        """Start the file monitoring process."""
        if not self.validate_config():
            return

        print("Starting Cloudflare Tunnel URL Monitor...")
        print(f"Monitoring directories: {self.config['watch_directories']}")
        print(f"File patterns: {self.config['filename_patterns']}")
        print(f"Discord webhook configured: {bool(self.config['discord_webhook_url'])}")

        # Setup file watchers for each directory
        for directory in self.config['watch_directories']:
            expanded_dir = os.path.expanduser(directory)
            if os.path.exists(expanded_dir):
                self.observer.schedule(
                    self.event_handler,
                    expanded_dir,
                    recursive=self.config.get('recursive_monitoring', True)
                )
                print(f"Watching directory: {expanded_dir}")
            else:
                print(f"Warning: Directory does not exist: {expanded_dir}")

        self.observer.start()
        print("\n🚀 Monitor started! Watching for tunnel URL changes...")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping monitor...")
            self.observer.stop()

        self.observer.join()
        print("Monitor stopped.")


def main():
    """Main application entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor log files for Cloudflare tunnel URLs")
    parser.add_argument('--config', '-c', default='tunnel_monitor_config.json',
                       help='Configuration file path')
    parser.add_argument('--test-webhook', action='store_true',
                       help='Test Discord webhook with sample message')
    parser.add_argument('--test-file', '-f', 
                       help='Test URL extraction on specific file')

    args = parser.parse_args()

    if args.test_webhook:
        # Test webhook functionality
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            print("Please set DISCORD_WEBHOOK_URL environment variable")
            return

        webhook = DiscordWebhook(webhook_url)
        success = webhook.send_tunnel_notification(
            original_url="https://example.trycloudflare.com",
            shortened_url="https://tinyurl.com/test123",
            log_file="test.log",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        print(f"Webhook test {'successful' if success else 'failed'}")
        return

    if args.test_file:
        # Test URL extraction on specific file
        if not os.path.exists(args.test_file):
            print(f"File not found: {args.test_file}")
            return

        extractor = TunnelURLExtractor()
        with open(args.test_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        urls = extractor.extract_urls(content)
        print(f"Found {len(urls)} tunnel URLs in {args.test_file}:")
        for url in urls:
            print(f"  - {url}")
        return

    # Start normal monitoring
    monitor = TunnelMonitor(args.config)
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
