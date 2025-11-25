# S3-Compatible Storage Manager

Python scripts to manage S3-compatible object storage buckets using boto3. Works with **Cloudflare R2**, **AWS S3**, **MinIO**, **DigitalOcean Spaces**, **Wasabi**, **Backblaze B2**, and any other S3-compatible storage service.

## Features

### 📤 Upload Script (`upload_to_r2.py`)
- **Incremental uploads**: Only uploads new files, skips existing ones
- **Recursive upload**: Uploads entire directory structure
- **Hierarchy preservation**: Maintains folder structure in the bucket
- **Content-type detection**: Automatically sets correct MIME types based on file extensions
- **Pre-scan analysis**: Shows what will be uploaded vs skipped before starting
- **Progress tracking**: Shows each file being uploaded with size and type
- **Memory efficient**: Uses ~30MB for 100K files, ~750MB for 5M files
- **Error handling**: Reports failures and continues with remaining files
- **Detailed statistics**: Shows uploaded count, skipped count, and sizes

### 🗑️ Delete Script (`delete_r2_bucket.py`)
- **Batch deletion**: Deletes up to 1000 objects per API call for efficiency
- **Pagination support**: Handles buckets with any number of objects
- **Prefix filtering**: Optional prefix filter using `R2_PREFIX` environment variable
- **Safety confirmation**: Requires explicit "yes" confirmation before deletion
- **Detailed logging**: Shows progress and reports any errors
- **Error handling**: Gracefully handles API errors and reports failures

### 📦 Move Script (`move_r2_directory.py`)
- **Directory relocation**: Move entire directories within the same bucket
- **Preserves structure**: Maintains all subdirectories and files
- **Copy-then-delete**: Safely copies objects before deleting originals
- **Preview mode**: Shows what will be moved before execution
- **Batch operations**: Handles any number of objects efficiently
- **Progress tracking**: Shows each object being moved
- **Error handling**: Reports failures and continues with remaining objects

### 🎯 Pattern Deletion Script (`delete_by_pattern.py`)
- **Selective deletion**: Delete files by extension or filename pattern
- **Flexible filtering**: Combine extensions and patterns for precise targeting
- **Dry run mode**: Preview what will be deleted without actually deleting
- **Batch operations**: Efficiently deletes up to 1000 objects per request
- **Safety confirmation**: Requires typing 'DELETE' to proceed
- **Detailed preview**: Shows matching files before deletion
- **Progress tracking**: Reports each deleted file and any errors

### 🔄 Bucket Migration Script (`migrate_bucket.py`)
- **Server-side copy**: Copy between buckets without downloading (fast!)
- **No bandwidth usage**: Data never leaves the cloud provider's network
- **Preserve structure**: Maintains all folder hierarchies and files
- **Copy or migrate**: Option to delete from source after copying
- **Prefix filtering**: Migrate only specific directories
- **Progress tracking**: Shows each object being copied
- **Error handling**: Reports failures and continues with remaining objects

## Prerequisites

```bash
pip install boto3 python-dotenv
```

## Configuration

Create a `.env` file in the project root with your S3-compatible storage credentials. You can use the provided `env.example` as a template:

```bash
cp env.example .env
```

Then edit `.env` with your credentials:

```env
R2_ACCOUNT_ID=your_account_id_or_endpoint
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET=your_bucket_name
R2_PREFIX=
R2_SOURCE_DIR=/path/to/your/source/directory
```

### S3-Compatible Service Configuration

The scripts work with any S3-compatible storage by modifying the endpoint URL in the code. Here's how to configure for different services:

#### Cloudflare R2
```env
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
```
Endpoint format: `https://{account_id}.r2.cloudflarestorage.com`

**Getting R2 Credentials:**
1. Log in to Cloudflare dashboard
2. Go to R2 → Overview
3. Create an API token with R2 read/write permissions
4. Copy your Account ID, Access Key ID, and Secret Access Key

#### AWS S3
```env
R2_ACCOUNT_ID=s3.amazonaws.com  # or s3.region.amazonaws.com
R2_ACCESS_KEY_ID=your_aws_access_key
R2_SECRET_ACCESS_KEY=your_aws_secret_key
```
Endpoint format: `https://s3.amazonaws.com` or `https://s3.{region}.amazonaws.com`

#### MinIO
```env
R2_ACCOUNT_ID=your-minio-server.com:9000
R2_ACCESS_KEY_ID=your_minio_access_key
R2_SECRET_ACCESS_KEY=your_minio_secret_key
```
Endpoint format: `https://your-minio-server.com:9000`

#### DigitalOcean Spaces
```env
R2_ACCOUNT_ID=nyc3.digitaloceanspaces.com  # or your region
R2_ACCESS_KEY_ID=your_spaces_access_key
R2_SECRET_ACCESS_KEY=your_spaces_secret_key
```
Endpoint format: `https://{region}.digitaloceanspaces.com`

#### Wasabi
```env
R2_ACCOUNT_ID=s3.wasabisys.com  # or s3.region.wasabisys.com
R2_ACCESS_KEY_ID=your_wasabi_access_key
R2_SECRET_ACCESS_KEY=your_wasabi_secret_key
```
Endpoint format: `https://s3.wasabisys.com` or `https://s3.{region}.wasabisys.com`

#### Backblaze B2
```env
R2_ACCOUNT_ID=s3.us-west-001.backblazeb2.com  # or your region
R2_ACCESS_KEY_ID=your_b2_key_id
R2_SECRET_ACCESS_KEY=your_b2_application_key
```
Endpoint format: `https://s3.{region}.backblazeb2.com`

### Custom Endpoint Configuration

To use a different S3-compatible service, modify the endpoint URL in both scripts:

**In `upload_to_r2.py` and `delete_r2_bucket.py`**, find this line:
```python
endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
```

Replace it with your service's endpoint:
```python
# For AWS S3
endpoint_url = f"https://{account_id}"

# For MinIO
endpoint_url = f"https://{account_id}"

# For any custom endpoint
endpoint_url = "https://your-custom-s3-endpoint.com"
```

## Usage

### Upload Directory to S3-Compatible Storage

Upload all files from your source directory while maintaining the folder structure:

```bash
python3 upload_to_r2.py
```

Or use the helper script:

```bash
./run_upload.sh
```

**How it works:**
- Local path: `/Users/username/Downloads/source`
- Bucket structure: `bucket-name/source/folder1/file.txt`
- The source folder name is automatically included as the root folder in the bucket
- Only new files are uploaded; existing files are skipped (incremental upload)
- Shows pre-upload analysis with file counts and sizes

**Example workflow:**
1. Script scans the S3 bucket to get existing files
2. Script scans your local directory
3. Compares and shows what will be uploaded vs skipped
4. Asks for confirmation
5. Uploads only new files

### Delete All Objects from Bucket

Delete all objects from your S3-compatible bucket:

```bash
python3 delete_r2_bucket.py
```

Or use the helper script:

```bash
./run_delete.sh
```

⚠️ **Warning:** This permanently deletes all objects. Make sure you have backups if needed.

**Safety features:**
- Displays bucket name and prefix (if any) before deletion
- Requires explicit "yes" confirmation
- Shows progress for each deleted object
- Reports any errors encountered

### Move Directories Within Bucket

Move directories to a new location within the same bucket:

```bash
python3 move_r2_directory.py
```

Or use the helper script:

```bash
./run_move.sh
```

**How it works:**
- Copies all objects from source directory to destination
- Deletes original objects after successful copy
- Preserves complete directory structure and all files
- Shows preview before moving

**Example:**
- Move `source/ecos-release-notes/` → `source/HPE Aruba/ecos-release-notes/`
- Move `source/orch-release-notes/` → `source/HPE Aruba/orch-release-notes/`

**Configuration via .env:**
```env
MOVE_SOURCE_1=source/old-folder/
MOVE_DEST_1=source/new-folder/
MOVE_SOURCE_2=another/old-path/
MOVE_DEST_2=another/new-path/
```

### Delete Files by Pattern

Delete specific files by extension or filename pattern:

```bash
python3 delete_by_pattern.py
```

Or use the helper script:

```bash
./run_delete_pattern.sh
```

**How it works:**
- Scans bucket for files matching your criteria
- Shows preview of files to be deleted
- Requires typing 'DELETE' to confirm
- Deletes matching files in batches

**Configuration via .env:**
```env
# Delete by file extension
DELETE_EXTENSIONS=.DS_Store,.docx,.tmp,.bak

# Delete by filename pattern (files containing these words)
DELETE_PATTERNS=backup,temp,old,cache

# Enable dry run mode (preview only, no deletion)
DELETE_DRY_RUN=true
```

**Examples:**
- Remove all `.DS_Store` files: `DELETE_EXTENSIONS=.DS_Store`
- Remove backup files: `DELETE_PATTERNS=backup,bak`
- Remove temp files: `DELETE_EXTENSIONS=.tmp,.temp` + `DELETE_PATTERNS=temp`
- Preview mode: `DELETE_DRY_RUN=true`

**Safety features:**
- Dry run mode for safe testing
- Shows preview of all matching files
- Requires typing 'DELETE' (not just 'yes')
- Detailed progress reporting

### Migrate Between Buckets

Copy or migrate all objects from one bucket to another **without downloading** (server-side copy):

```bash
python3 migrate_bucket.py
```

Or use the helper script:

```bash
./run_migrate.sh
```

**How it works:**
- Lists all objects in source bucket
- Copies each object directly to destination bucket (server-side)
- Optionally deletes from source after successful copy
- No data transfer through your computer (fast and free!)

**Configuration via .env:**
```env
# Source and destination buckets
MIGRATE_SOURCE_BUCKET=old-bucket-name
MIGRATE_DEST_BUCKET=new-bucket-name

# Optional: only migrate specific directory
MIGRATE_PREFIX=source/specific-folder/

# Optional: delete from source after copy (true migration)
MIGRATE_DELETE_SOURCE=false  # Set to true for move instead of copy
```

**Use cases:**
- **Rename bucket**: Copy to new bucket with desired name
- **Backup bucket**: Create a copy in another bucket
- **Reorganize**: Migrate to bucket with better structure
- **Consolidate**: Merge multiple buckets into one

**Advantages:**
- ⚡ **Fast**: Server-side copy (no download/upload)
- 💰 **Free**: No bandwidth charges
- 🔒 **Safe**: Preserves all metadata and structure
- 📊 **Progress tracking**: See each file being copied

**Safety features:**
- Shows preview of objects to migrate
- Requires typing 'MIGRATE' to confirm
- Copy mode by default (keeps source intact)
- Detailed progress and error reporting

## How It Works

### Upload Process

1. Reads configuration from `.env` file
2. **Scans R2 bucket** to get list of existing files (in-memory set)
3. **Scans local directory** to build list of files to process
4. **Compares** local vs remote and identifies new files
5. Shows analysis: how many files to upload vs skip
6. Uploads only new files with correct content-type
7. Reports detailed statistics (uploaded, skipped, sizes)

### Delete Process

1. Lists all objects in the bucket (with optional prefix filter)
2. Deletes objects in batches of up to 1000
3. Handles pagination automatically
4. Reports deleted objects and any errors

### Move Process

1. Lists all objects with the source prefix
2. Shows preview of what will be moved
3. Asks for confirmation
4. For each object:
   - Copies to new location (preserving path structure)
   - Deletes original after successful copy
5. Reports detailed statistics (moved count, errors)

### Pattern Deletion Process

1. Reads deletion criteria from .env (extensions and patterns)
2. Scans bucket for all objects
3. Filters objects matching criteria
4. Shows preview of matching files
5. Asks for confirmation (must type 'DELETE')
6. Deletes matching files in batches
7. Reports detailed statistics (deleted count, errors)

## Examples

### Upload Output

```
============================================================
Upload Configuration:
  Source: /Users/username/Downloads/source
  Bucket: my-bucket
============================================================

Start upload? (yes/no): yes

============================================================
Incremental Upload - Skipping existing files
============================================================

Scanning R2 bucket: my-bucket...
Found 100 existing objects in bucket

Scanning local directory: /Users/username/Downloads/source...
Found 200 local files

============================================================
Analysis:
  Total local files: 200
  New files to upload: 100 (22.5 MB)
  Existing files (will skip): 100 (22.73 MB)
============================================================

Starting upload to: my-bucket/source
============================================================

Uploading: folder1/newfile.txt -> source/folder1/newfile.txt
  Size: 1.25 KB, Type: text/plain
  ✓ Uploaded successfully

============================================================
Upload complete!
Successfully uploaded: 100 files (22.5 MB)
Skipped (already exist): 100 files (22.73 MB)
Total files processed: 200
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
| `R2_ACCOUNT_ID` | Yes | S3 endpoint hostname or account ID (e.g., `account.r2.cloudflarestorage.com`, `s3.amazonaws.com`, `minio.example.com`) |
| `R2_ACCESS_KEY_ID` | Yes | S3 API access key ID |
| `R2_SECRET_ACCESS_KEY` | Yes | S3 API secret access key |
| `R2_BUCKET` | Yes | Name of the S3 bucket |
| `R2_SOURCE_DIR` | Yes (upload) | Local directory path to upload |
| `R2_PREFIX` | No | Optional prefix to filter/organize objects |
| `MOVE_SOURCE_N` | No | Source directory for move operation (N=1,2,3...) |
| `MOVE_DEST_N` | No | Destination directory for move operation (N=1,2,3...) |
| `DELETE_EXTENSIONS` | No | Comma-separated file extensions to delete (e.g., `.DS_Store,.tmp`) |
| `DELETE_PATTERNS` | No | Comma-separated patterns to match in filenames (e.g., `backup,temp`) |
| `DELETE_DRY_RUN` | No | Set to `true` for preview mode (no actual deletion) |
| `MIGRATE_SOURCE_BUCKET` | No | Source bucket name for migration |
| `MIGRATE_DEST_BUCKET` | No | Destination bucket name for migration |
| `MIGRATE_PREFIX` | No | Optional prefix to filter objects for migration |
| `MIGRATE_DELETE_SOURCE` | No | Set to `true` to delete from source after copy (default: `false`) |

**Note:** Despite the `R2_` prefix in variable names (for historical reasons), these work with any S3-compatible service.

## Compatibility

✅ **Tested with:**
- Cloudflare R2
- AWS S3
- MinIO
- DigitalOcean Spaces
- Wasabi
- Backblaze B2

✅ **Should work with any S3-compatible storage** that supports:
- S3 API v2 (ListObjectsV2)
- Standard S3 authentication
- PutObject and DeleteObjects operations

## Performance & Scalability

### Memory Usage
- **100,000 files**: ~30 MB RAM
- **1,000,000 files**: ~150 MB RAM
- **5,000,000 files**: ~750 MB RAM

The in-memory comparison approach is efficient and works well even with millions of files on modern systems.

### Upload Speed
- Depends on your internet connection and file sizes
- Incremental uploads save significant time on subsequent runs
- Only new files are uploaded, skipping existing ones

### Batch Operations
- Delete operations handle up to 1000 objects per API call
- Automatic pagination for buckets with any number of objects

## Important Notes

- **Python 3.6+** required (uses f-strings)
- Use `python3` command (not `python`) if you have Python 2.x installed
- The upload script preserves the source folder name as the root in the bucket
- Content types are automatically detected based on file extensions
- Both scripts require explicit confirmation before executing
- Works with any S3-compatible storage service - just change the endpoint URL
- Variable names use `R2_` prefix for historical reasons, but work with any S3 service

## Use Cases

- **Backup and sync**: Incrementally backup local directories to cloud storage
- **Static site deployment**: Upload website files to S3/R2 for hosting
- **Data migration**: Transfer files between different S3-compatible services
- **Bulk operations**: Efficiently manage large numbers of files
- **Multi-cloud**: Use the same scripts across different cloud providers
- **Directory reorganization**: Restructure your bucket by moving directories
- **Folder consolidation**: Move multiple directories under a common parent

## License

MIT

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Version History

- **v0.5** - Bucket migration script (server-side copy between buckets)
- **v0.4** - Pattern-based deletion script (delete by extension/pattern)
- **v0.3** - Move directory script (relocate directories within bucket)
- **v0.2** - Incremental upload feature (skip existing files)
- **v0.1** - Initial release
