# R2 Bucket Management Scripts

Scripts to manage Cloudflare R2 bucket using the S3-compatible API.

## Scripts

1. **upload_to_r2.py** - Upload a directory to R2 maintaining folder hierarchy
2. **delete_r2_bucket.py** - Delete all objects from an R2 bucket

## Prerequisites

```bash
pip install boto3 python-dotenv
```

## Configuration

The script uses environment variables from your `.env` file:

- `R2_ACCOUNT_ID` - Your Cloudflare R2 account ID
- `R2_ACCESS_KEY_ID` - Your R2 access key ID
- `R2_SECRET_ACCESS_KEY` - Your R2 secret access key
- `R2_BUCKET` - The name of the bucket to delete objects from
- `R2_PREFIX` - (Optional) Prefix to filter objects (leave empty to delete all)

## Usage

### Upload Directory to R2

Upload all files from your source directory to R2:

```bash
python3 upload_to_r2.py
```

Or use the helper script:

```bash
./run_upload.sh
```

### Delete All Objects from R2

Delete all objects from the bucket:

```bash
python3 delete_r2_bucket.py
```

Or use the helper script:

```bash
./run_delete.sh
```

## Features

### Upload Script
- **Recursive upload**: Uploads entire directory structure
- **Hierarchy preservation**: Maintains folder structure in R2
- **Content-type detection**: Automatically sets correct MIME types
- **Progress tracking**: Shows each file being uploaded with size
- **Error handling**: Reports failures and continues with remaining files
- **Summary statistics**: Shows total files uploaded and total size

### Delete Script
- **Batch deletion**: Deletes up to 1000 objects per API call for efficiency
- **Pagination support**: Handles buckets with any number of objects
- **Prefix filtering**: Optional prefix filter using `R2_PREFIX` environment variable
- **Safety confirmation**: Requires explicit "yes" confirmation before deletion
- **Detailed logging**: Shows progress and reports any errors
- **Error handling**: Gracefully handles API errors and reports failures

## Safety

⚠️ **WARNING**: This script permanently deletes objects. Make sure you have backups if needed.

The script will:
1. Display the bucket name and prefix (if any)
2. Ask for confirmation before proceeding
3. Only proceed if you type "yes"

## Example Output

### Upload Example
```
============================================================
Upload Configuration:
  Source: /Users/abdul-macmini/Downloads/source
  Bucket: releasenotes
============================================================

Start upload? (yes/no): yes
Starting upload from: /Users/abdul-macmini/Downloads/source
To bucket: releasenotes
============================================================

Uploading: folder1/file1.txt -> folder1/file1.txt
  Size: 1.25 KB, Type: text/plain
  ✓ Uploaded successfully

Uploading: folder2/image.jpg -> folder2/image.jpg
  Size: 245.50 KB, Type: image/jpeg
  ✓ Uploaded successfully

============================================================
Upload complete!
Successfully uploaded: 150 files
Total size: 45.23 MB
============================================================
```

### Delete Example
```
============================================================
WARNING: This will delete ALL objects from bucket: releasenotes
============================================================

Are you sure you want to continue? (yes/no): yes
Starting deletion process for bucket: releasenotes
Deleting 150 objects...
  ✓ Deleted: file1.txt
  ✓ Deleted: file2.jpg
  ...

============================================================
Deletion complete!
Successfully deleted: 150 objects
============================================================
```
