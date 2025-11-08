# Cloudflare R2 Bucket Management Scripts

Python scripts to manage Cloudflare R2 buckets using the S3-compatible API with boto3.

## Features

### 📤 Upload Script (`upload_to_r2.py`)
- Recursively uploads entire directory structure to R2
- Maintains folder hierarchy in the bucket
- Automatically detects and sets correct content types
- Shows progress with file sizes
- Provides upload summary with statistics

### 🗑️ Delete Script (`delete_r2_bucket.py`)
- Batch deletes all objects from R2 bucket
- Handles pagination for large buckets (1000+ objects)
- Optional prefix filtering
- Safety confirmation before deletion
- Detailed progress reporting

## Prerequisites

```bash
pip install boto3 python-dotenv
```

## Configuration

Create a `.env` file in the project root with your Cloudflare R2 credentials:

```env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET=your_bucket_name
R2_PREFIX=
R2_SOURCE_DIR=/path/to/your/source/directory
```

### Getting R2 Credentials

1. Log in to your Cloudflare dashboard
2. Go to R2 → Overview
3. Create an API token with R2 read/write permissions
4. Copy your Account ID, Access Key ID, and Secret Access Key

## Usage

### Upload Directory to R2

Upload all files from your source directory while maintaining the folder structure:

```bash
python3 upload_to_r2.py
```

Or use the helper script:

```bash
./run_upload.sh
```

**Example:**
- Local path: `/Users/username/Downloads/source`
- Bucket structure: `bucket-name/source/folder1/file.txt`

The source folder name is automatically included as the root folder in R2.

### Delete All Objects from Bucket

Delete all objects from your R2 bucket:

```bash
python3 delete_r2_bucket.py
```

Or use the helper script:

```bash
./run_delete.sh
```

⚠️ **Warning:** This permanently deletes all objects. Use with caution!

## How It Works

### Upload Process

1. Reads configuration from `.env` file
2. Walks through all files in `R2_SOURCE_DIR`
3. Maintains the exact folder hierarchy
4. Uploads each file with correct content-type
5. Reports progress and final statistics

### Delete Process

1. Lists all objects in the bucket (with optional prefix filter)
2. Deletes objects in batches of up to 1000
3. Handles pagination automatically
4. Reports deleted objects and any errors

## Examples

### Upload Output

```
============================================================
Upload Configuration:
  Source: /Users/username/Downloads/source
  Bucket: my-bucket
============================================================

Start upload? (yes/no): yes
Starting upload from: /Users/username/Downloads/source
To bucket: my-bucket/source

Uploading: folder1/file1.txt -> source/folder1/file1.txt
  Size: 1.25 KB, Type: text/plain
  ✓ Uploaded successfully

============================================================
Upload complete!
Successfully uploaded: 150 files
Total size: 45.23 MB
============================================================
```

### Delete Output

```
============================================================
WARNING: This will delete ALL objects from bucket: my-bucket
============================================================

Are you sure you want to continue? (yes/no): yes
Starting deletion process for bucket: my-bucket
Deleting 150 objects...
  ✓ Deleted: source/folder1/file1.txt
  ✓ Deleted: source/folder2/image.jpg

============================================================
Deletion complete!
Successfully deleted: 150 objects
============================================================
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `R2_ACCOUNT_ID` | Yes | Your Cloudflare R2 account ID |
| `R2_ACCESS_KEY_ID` | Yes | R2 API access key ID |
| `R2_SECRET_ACCESS_KEY` | Yes | R2 API secret access key |
| `R2_BUCKET` | Yes | Name of the R2 bucket |
| `R2_SOURCE_DIR` | Yes (upload) | Local directory path to upload |
| `R2_PREFIX` | No | Optional prefix to filter/organize objects |

## Notes

- Python 3.6+ required (uses f-strings)
- Use `python3` command (not `python`) if you have Python 2.x installed
- The upload script preserves the source folder name as the root in R2
- Content types are automatically detected based on file extensions
- Both scripts require explicit confirmation before executing

## License

MIT

## Version

v0.1 - Initial release
