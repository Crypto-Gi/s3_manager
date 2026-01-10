# S3-Compatible Storage Manager

A powerful Python toolkit for managing S3-compatible object storage with intelligent duplicate detection, batch operations, and cross-bucket migration.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Crypto-Gi/S3-Compatible-Storage-Manager.git
cd S3-Compatible-Storage-Manager

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp env.example .env
# Edit .env with your credentials

# Upload files
python3 upload_to_r2.py
```

## ✨ Key Features

- **🔍 Smart Duplicate Detection** - Hybrid filename + xxhash64 content verification
- **⚡ High Performance** - Batch operations, incremental uploads, server-side copies
- **🔒 Safe Operations** - Confirmation prompts, dry-run mode, detailed previews
- **🌐 Universal Compatibility** - Works with any S3-compatible storage
- **📊 Detailed Reporting** - Progress tracking, statistics, error handling

## 📦 Supported Storage Providers

| Provider | Status | Endpoint Example |
|----------|--------|------------------|
| Cloudflare R2 | ✅ Tested | `{account_id}.r2.cloudflarestorage.com` |
| AWS S3 | ✅ Tested | `s3.amazonaws.com` |
| MinIO | ✅ Tested | `your-server.com:9000` |
| DigitalOcean Spaces | ✅ Tested | `nyc3.digitaloceanspaces.com` |
| Wasabi | ✅ Tested | `s3.wasabisys.com` |
| Backblaze B2 | ✅ Tested | `s3.us-west-001.backblazeb2.com` |
| Any S3-compatible | ✅ Compatible | Custom endpoint |

---

## 📚 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Scripts](#-scripts)
  - [Upload Script](#1-upload-script)
  - [Delete Script](#2-delete-script)
  - [Move Script](#3-move-script)
  - [Pattern Delete Script](#4-pattern-delete-script)
  - [Bucket Migration Script](#5-bucket-migration-script)
- [Advanced Usage](#-advanced-usage)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🔧 Installation

### Requirements
- Python 3.6 or higher
- pip package manager

### Setup

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `boto3` - AWS SDK for Python
- `python-dotenv` - Environment variable management
- `xxhash` - Fast hash function for duplicate detection

**2. Configure credentials:**
```bash
cp env.example .env
```

Edit `.env` with your storage credentials:
```env
R2_ACCOUNT_ID=your_account_id_or_endpoint
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET=your_bucket_name
R2_SOURCE_DIR=/path/to/your/source/directory
```

---

## ⚙️ Configuration

### Provider-Specific Setup

<details>
<summary><b>Cloudflare R2</b></summary>

```env
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
```

**Getting credentials:**
1. Log in to Cloudflare Dashboard
2. Navigate to R2 → Overview
3. Create API token with R2 read/write permissions
4. Copy Account ID, Access Key ID, and Secret Access Key

</details>

<details>
<summary><b>AWS S3</b></summary>

```env
R2_ACCOUNT_ID=s3.amazonaws.com  # or s3.region.amazonaws.com
R2_ACCESS_KEY_ID=your_aws_access_key
R2_SECRET_ACCESS_KEY=your_aws_secret_key
```

</details>

<details>
<summary><b>MinIO</b></summary>

```env
R2_ACCOUNT_ID=your-minio-server.com:9000
R2_ACCESS_KEY_ID=your_minio_access_key
R2_SECRET_ACCESS_KEY=your_minio_secret_key
```

</details>

<details>
<summary><b>DigitalOcean Spaces</b></summary>

```env
R2_ACCOUNT_ID=nyc3.digitaloceanspaces.com
R2_ACCESS_KEY_ID=your_spaces_access_key
R2_SECRET_ACCESS_KEY=your_spaces_secret_key
```

</details>

<details>
<summary><b>Other Providers</b></summary>

For other S3-compatible services, modify the endpoint URL in the scripts:

```python
# Find this line in the script:
endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

# Replace with your endpoint:
endpoint_url = "https://your-custom-endpoint.com"
```

</details>

---

## 📜 Scripts

### 1. Upload Script

**`upload_to_r2.py`** - Intelligent file upload with hybrid duplicate detection

#### Features
- ✅ Hybrid duplicate detection (filename + content hash)
- ✅ Incremental uploads (only new/modified files)
- ✅ Preserves directory structure
- ✅ Automatic content-type detection
- ✅ xxhash64 metadata storage
- ✅ Pre-upload analysis
- ✅ CLI arguments support

#### Usage

**Basic:**
```bash
python3 upload_to_r2.py
```

**With CLI arguments:**
```bash
# Dry run (preview only)
python3 upload_to_r2.py --dry-run

# Override source directory
python3 upload_to_r2.py --source /path/to/files

# Override bucket
python3 upload_to_r2.py --bucket my-other-bucket

# Override destination prefix
python3 upload_to_r2.py --destination my-folder
```

#### How It Works

1. **Scans bucket** - Gets list of existing filenames
2. **Scans local directory** - Builds list of files to process
3. **Smart filtering**:
   - First checks if filename exists (fast)
   - For matches, computes xxhash64 of local file
   - Retrieves xxhash from object metadata
   - Compares hashes - only skips if both match
4. **Uploads** - New or modified files with hash stored in metadata

**Example Output:**
```
============================================================
Incremental Upload - Hybrid duplicate detection
============================================================

Scanning R2 bucket: my-bucket...
Found 100 existing objects (95 unique filenames) in bucket

Scanning local directory: /Users/user/Downloads/source...
Found 200 local files

Analyzing files for upload...
  Note: readme.txt exists but content differs (hash mismatch) - will upload

============================================================
Analysis:
  Total local files: 200
  New files to upload: 108 (23.1 MB)
  Existing files (will skip): 92 (22.5 MB)
  Hash verifications performed: 95
============================================================

Uploading: folder1/newfile.txt -> source/folder1/newfile.txt
  Size: 1.25 KB, Type: text/plain
  xxhash: a1b2c3d4e5f67890
  ✓ Uploaded successfully

============================================================
Upload complete!
Successfully uploaded: 108 files (23.1 MB)
Skipped (already exist): 92 files (22.5 MB)
Total files processed: 200
============================================================
```

---

### 2. Delete Script

**`delete_r2_bucket.py`** - Batch delete all objects from a bucket

#### Features
- ✅ Batch deletion (1000 objects per API call)
- ✅ Pagination support
- ✅ Prefix filtering
- ✅ Safety confirmation

#### Usage

```bash
python3 delete_r2_bucket.py
```

**Configuration:**
```env
R2_BUCKET=bucket-to-delete
R2_PREFIX=optional/prefix/  # Optional: only delete objects with this prefix
```

⚠️ **Warning:** This permanently deletes objects. Ensure you have backups!

---

### 3. Move Script

**`move_r2_directory.py`** - Move directories within the same bucket

#### Features
- ✅ Preserves directory structure
- ✅ Copy-then-delete (safe operation)
- ✅ Preview mode
- ✅ Batch operations

#### Usage

```bash
python3 move_r2_directory.py
```

**Configuration:**
```env
MOVE_SOURCE_1=source/old-folder/
MOVE_DEST_1=source/new-folder/
MOVE_SOURCE_2=another/old-path/
MOVE_DEST_2=another/new-path/
```

**Example:**
```
Move: source/ecos-release-notes/ → source/HPE Aruba/ecos-release-notes/
```

---

### 4. Pattern Delete Script

**`delete_by_pattern.py`** - Delete files by extension or pattern

#### Features
- ✅ Delete by file extension
- ✅ Delete by filename pattern
- ✅ Dry run mode
- ✅ Detailed preview
- ✅ Safety confirmation (type 'DELETE')

#### Usage

```bash
python3 delete_by_pattern.py
```

**Configuration:**
```env
# Delete by extension
DELETE_EXTENSIONS=.DS_Store,.docx,.tmp

# Delete by pattern (files containing these words)
DELETE_PATTERNS=backup,temp,old

# Dry run (preview only)
DELETE_DRY_RUN=true
```

**Examples:**
```bash
# Remove all .DS_Store files
DELETE_EXTENSIONS=.DS_Store

# Remove backup files
DELETE_PATTERNS=backup,bak

# Preview mode
DELETE_DRY_RUN=true
```

---

### 5. Bucket Migration Script

**`migrate_bucket.py`** - Server-side copy between buckets

#### Features
- ✅ Server-side copy (no download/upload)
- ✅ Zero bandwidth usage
- ✅ Preserves metadata and structure
- ✅ Optional source deletion (true migration)
- ✅ Prefix filtering

#### Usage

```bash
python3 migrate_bucket.py
```

**Configuration:**
```env
MIGRATE_SOURCE_BUCKET=old-bucket
MIGRATE_DEST_BUCKET=new-bucket
MIGRATE_PREFIX=optional/folder/  # Optional
MIGRATE_DELETE_SOURCE=false  # Set to true for move instead of copy
```

**Use Cases:**
- 🔄 Rename bucket
- 💾 Backup bucket
- 📁 Reorganize structure
- 🔗 Consolidate buckets

**Advantages:**
- ⚡ Fast (server-side copy)
- 💰 Free (no bandwidth charges)
- 🔒 Safe (preserves metadata)

---

## 🎯 Advanced Usage

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `R2_ACCOUNT_ID` | ✅ | Endpoint hostname or account ID |
| `R2_ACCESS_KEY_ID` | ✅ | API access key ID |
| `R2_SECRET_ACCESS_KEY` | ✅ | API secret access key |
| `R2_BUCKET` | ✅ | Bucket name |
| `R2_SOURCE_DIR` | Upload only | Local directory path |
| `R2_PREFIX` | ❌ | Optional prefix filter |
| `MOVE_SOURCE_N` | Move only | Source directory (N=1,2,3...) |
| `MOVE_DEST_N` | Move only | Destination directory (N=1,2,3...) |
| `DELETE_EXTENSIONS` | Pattern delete | File extensions to delete |
| `DELETE_PATTERNS` | Pattern delete | Filename patterns to match |
| `DELETE_DRY_RUN` | Pattern delete | Preview mode (true/false) |
| `MIGRATE_SOURCE_BUCKET` | Migration only | Source bucket name |
| `MIGRATE_DEST_BUCKET` | Migration only | Destination bucket name |
| `MIGRATE_PREFIX` | Migration only | Optional prefix filter |
| `MIGRATE_DELETE_SOURCE` | Migration only | Delete source after copy |

### Helper Scripts

Convenience shell scripts are provided:

```bash
./run_upload.sh          # Upload files
./run_delete.sh          # Delete all objects
./run_move.sh            # Move directories
./run_delete_pattern.sh  # Delete by pattern
./run_migrate.sh         # Migrate buckets
```

---

## ⚡ Performance

### Memory Usage
| Files | RAM Usage |
|-------|-----------|
| 100K | ~30 MB |
| 1M | ~150 MB |
| 5M | ~750 MB |

### Upload Performance
- **Incremental**: Only uploads new/modified files
- **Hash verification**: Only for filename matches
- **Example**: 100K files with 1K matches = ~1K API calls (vs 100K for full scan)

### xxhash64 Speed
- **5-13 GB/s** depending on system
- Extremely fast, minimal overhead

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>ImportError: No module named 'xxhash'</b></summary>

**Solution:**
```bash
pip install xxhash
```

</details>

<details>
<summary><b>SyntaxError: invalid syntax (f-strings)</b></summary>

**Cause:** Python version < 3.6

**Solution:**
```bash
python3 --version  # Check version
# Upgrade to Python 3.6+
```

</details>

<details>
<summary><b>ClientError: NoSuchBucket</b></summary>

**Cause:** Bucket doesn't exist or incorrect credentials

**Solution:**
1. Verify bucket name in `.env`
2. Check credentials are correct
3. Ensure bucket exists in your account

</details>

<details>
<summary><b>Files not being skipped despite existing</b></summary>

**Cause:** Old uploads without xxhash metadata

**Solution:** Script will re-upload to add hash metadata. This is expected behavior for first run after upgrading to v0.6.

</details>

---

## 📊 Version History

| Version | Date | Description |
|---------|------|-------------|
| **v0.6** | 2025-01-10 | Hybrid duplicate detection (filename + xxhash) |
| **v0.5** | 2025-01-10 | Filename-based duplicate detection |
| **v0.4** | 2024-11-25 | CLI arguments for upload script |
| **v0.3** | 2024-11-25 | Move directory script |
| **v0.2** | 2024-11-08 | Incremental upload feature |
| **v0.1** | 2024-11-08 | Initial release |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [boto3](https://github.com/boto/boto3) - AWS SDK for Python
- Uses [xxhash](https://github.com/ifduyue/python-xxhash) for fast content hashing
- Inspired by the need for efficient S3-compatible storage management

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Crypto-Gi/S3-Compatible-Storage-Manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Crypto-Gi/S3-Compatible-Storage-Manager/discussions)

---

**Made with ❤️ for the cloud storage community**
