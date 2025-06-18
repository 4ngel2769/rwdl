<div align="center">
  <h1>Recursive Web Directory Downloader (<code>rwdl</code>)</h1>
  <img src="https://img.shields.io/badge/python-3.7%2B-blue" title="Python version">
  <img src="https://img.shields.io/badge/license-MIT-green" title="License">
</div>

> [!NOTE] 
> Project has been moved to its own repository from [4ngel2769/side-projects](https://github.com/4ngel2769/side-projects)

A versatile Python script that recursively downloads specific file types from web directories with Apache-style listings. Perfect for mirroring repositories, downloading software distributions, or archiving web content.

## Features

- **Recursive directory traversal** with configurable depth
- **Multiple file extensions** support (`e.g., .torrent, .exe, .iso`)
- **Breadth-first search algorithm** for efficient traversal
- **Duplicate avoidance** with visited URL tracking
- **Resume capability** by skipping existing files
- **Smart Filtering**
    - Skips navigation links (`../, ./, #, ?`)
    - Ignores non-web links (`mailto:, tel:, javascript:`)
    - Validates file extensions before downloading
- **Configurable delays** between requests
- **Cross-platform** compatibility (`Windows, Linux, macOS`)

## Installation

### Prerequisites
- Python 3.7 or higher
- Git

1. Clone the repository:
```bash
git clone https://github.com/4ngel2769/rwdl.git
cd rwdl
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Command
```bash
python rwdl.py --url [BASE_URL] --extension [EXTENSIONS]
```

### Full Options
```bash
python rwdl.py \
  --url https://example.com/files/ \    # Base URL to start downloading from
  --depth 3 \                           # Recursion depth (0=base only)
  --extension .torrent,.iso \           # File extensions to download
  --output ./downloads \                # Output directory
  --delay 0.5                           # Optional delay between requests
```

### Arguments

| Argument        | Short | Required | Default     | Description                                 |
|-----------------|-------|----------|-------------|---------------------------------------------|
| `--url`         | `-u`  | Yes      |             | Base URL to start downloading from          |
| `--extension`   | `-e`  | Yes      |             | Comma-separated file extensions to download |
| `--depth`       | `-d`  | No       | 1           | Recursion depth (0=base only)               |
| `--output`      | `-o`  | No       | ./downloads | Output base directory                       |
| `--delay`       |       | No       | 0.5         | Delay between requests in seconds           |
| `--help`        | `-h`  | No       |             | Show help message                           |
| `--version`     | `-v`  | No       |             | Show version and                            |

## Examples

1. **Download ParrotOS torrent files** (depth 1):
```bash
python rwdl.py \
  --url https://deb.parrot.sh/parrot/iso/ \
  --extension .torrent \
  --output ./parrot_torrents \
  --depth 1 \
```

2. **Download Windows installers** (depth 2, slower):
```bash
python rwdl.py \
  --url https://software.example.com/windows/ \
  --depth 2 \
  --extension .exe,.msi \
  --delay 1.0
```

3. **Download Debian Linux ISOs** (base directory only):
```bash
python rwdl.py \
  --url https://cdimage.debian.org/cdimage/weekly-builds/amd64/ \
  --depth 1 \
  --extension .iso,.img
```

## Output Structure

The script creates a directory structure mirroring the remote server:

If the base URL is `https://example.com/files/` and the directories are structured like this:
```plaintext
https://example.com/files/folder1/file1.ext
                      │     └── file2.ext
                      ├── folder2/
                      │     └── nested/
                      │         └── file3.ext
                      └── base_files.ext
```
The output will be structured as follows:
```
output_dir/
├── folder1/
│   ├── file1.ext
│   └── file2.ext
├── folder2/
│   └── nested/
│       └── file3.ext
└── base_files.ext
```

## Limitations

1. Requires Apache-style directory listings
2. Doesn't handle JavaScript-rendered content
3. Won't follow links to external domains
4. Limited to HTTP/HTTPS protocols
5. May not work with custom directory listing formats

## Troubleshooting

**Problem**: Script fails to parse directory
- **Solution**: Verify the URL shows a standard Apache directory listing

**Problem**: Downloads are incomplete
- **Solution**: Increase delay time with `--delay 1.0`

**Problem**: SSL certificate errors
- **Solution**: Add this before the script:
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

> [!TIP]
> Read the [Code of Conduct](CONTRIBUTING.md)

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a pull request

---

**Disclaimer**: Use this script responsibly and respect server resources. Always comply with website terms of service and robots.txt directives.