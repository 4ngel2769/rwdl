################################################
# RWDL - Recursive Web Directory Downloader
# Copyright (c) 2025 angeldev0
# Code written by angeldev0
# License: MIT
################################################

import os
import argparse
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import sys

# Custom headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0'
}

class VersionAction(argparse.Action):
    def __init__(self, option_strings, version=None, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help="Show version and exit"):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        version_message = f"""
╔══════════════════════════════════════════╗
║             RWDL version 1.0.0           ║
╚══════════════════════════════════════════╝
Thank you for using RWDL (Recursive Web Directory Downloader)!
Author: angeldev0
License: MIT

                    For more information, visit:

 - https://github.com/4ngel2769/side-projects/tree/main/scripts/rwdl -
"""
        print(version_message)
        parser.exit()

class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)
    
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(f"{option_string} {args_string}")
            return ', '.join(parts)

# Custom help action that displays our formatted help
class CustomHelpAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help="Show this help message and exit"):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)
    
    def __call__(self, parser, namespace, values, option_string=None):
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                   RWDL - Usage Guide                         ║
╚══════════════════════════════════════════════════════════════╝

Recursive Web Directory Downloader (RWDL)
----------------------------------------
A tool for recursively downloading files from web directories.
Downloads files with specified extensions while respecting 
the directory structure of the source.

Usage:
  python rwdl.py [-h] [--version] --url URL [--depth DEPTH] 
                 --extension EXTENSION [--output OUTPUT] [--delay DELAY]

options:
  -h, --help                           show this help message and exit
  --version                            Show version and exit
  --url URL, -u URL                    Base URL to start downloading from
  --depth DEPTH, -d DEPTH              Recursion depth (0=base only)
  --extension EXTENSION, -e EXTENSION  Comma-separated file extensions to download (e.g., .torrent,.exe)
  --output OUTPUT, -o OUTPUT           Output base directory (default: ./downloads)
  --delay DELAY                        Delay between requests in seconds (default: 0.5)

Examples:
---------
  • python rwdl.py -u http://example.com/files/ -e .pdf,.doc -d 2

  • python rwdl.py --url http://files.site.com/ --extension .zip --depth 1 
    --output ./downloads

                    For more information, visit:

 - https://github.com/4ngel2769/side-projects/tree/main/scripts/rwdl -
"""
        print(help_text)
        parser.exit()

def create_arg_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        formatter_class=CustomHelpFormatter,
        add_help=False  # Disable built-in help
    )
    
    # Add custom help argument
    parser.add_argument('-h', '--help', action=CustomHelpAction)
    parser.add_argument('--version', '-v', action=VersionAction,
                        help='Show version and exit')
    parser.add_argument('--url', '-u', required=True, 
                        help='Base URL to start downloading from')
    parser.add_argument('--depth', '-d', type=int, default=1,
                        help='Recursion depth (0=base only)')
    parser.add_argument('--extension', '-e', required=True,
                        help='Comma-separated file extensions to download (e.g., .torrent,.exe)')
    parser.add_argument('--output', '-o', default='./downloads',
                        help='Output base directory (default: ./downloads)')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Delay between requests in seconds (default: 0.5)')
    
    return parser.parse_args()

def normalize_url(url):
    """Ensure URL ends with a slash"""
    return url if url.endswith('/') else url + '/'

def is_valid_extension(filename, extensions):
    """Check if file has one of the target extensions"""
    return any(filename.endswith(ext) for ext in extensions)

def download_file(url, local_path):
    """Download file with error handling"""
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  ✗ Download failed: {str(e)}")
        return False

def parse_directory(url):
    """Parse directory listing and return valid links"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.select('a[href]'):
            href = link['href']
            # Skip navigation links
            if href in ['../', './'] or href.startswith(('?', '#')):
                continue
            # Skip special protocols
            if any(href.startswith(p) for p in ['javascript:', 'mailto:', 'tel:']):
                continue
            links.append(href)
        return links
    except Exception as e:
        print(f"  ✗ Directory parsing failed: {str(e)}")
        return []

def main():
    args = create_arg_parser()
    base_url = normalize_url(args.url)
    extensions = [ext.strip() for ext in args.extension.split(',')]
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # BFS queue: (current_url, current_depth, local_path)
    queue = deque([(base_url, 0, args.output)])
    visited = set()

    print(f"Starting download from: {base_url}")
    print(f"Target extensions: {', '.join(extensions)}")
    print(f"Max depth: {args.depth}, Delay: {args.delay}s\n")

    while queue:
        url, depth, local_base = queue.popleft()
        
        if url in visited:
            continue
        visited.add(url)
        
        print(f"Processing: {url} [Depth {depth}]")
        
        # Parse directory contents
        links = parse_directory(url)
        if not links:
            print("  → No valid links found")
            continue
        
        for link in links:
            absolute_url = urljoin(url, link)
            
            # Process directories
            if absolute_url.endswith('/'):
                if depth < args.depth:
                    # Create local directory path
                    dir_name = os.path.basename(absolute_url.rstrip('/'))
                    new_local = os.path.join(local_base, dir_name)
                    os.makedirs(new_local, exist_ok=True)
                    
                    # Add to queue for processing
                    queue.append((absolute_url, depth + 1, new_local))
                    print(f"  + Queued directory: {dir_name}")
            # Process files
            else:
                filename = os.path.basename(absolute_url)
                if is_valid_extension(filename, extensions):
                    local_path = os.path.join(local_base, filename)
                    
                    if os.path.exists(local_path):
                        print(f"  ✓ Skipping existing: {filename}")
                    else:
                        print(f"  ↓ Downloading: {filename}")
                        if download_file(absolute_url, local_path):
                            print(f"    → Saved to: {local_path}")
                        time.sleep(args.delay)
        time.sleep(args.delay)

    print("\nDownload process completed!")

if __name__ == "__main__":
    main()
