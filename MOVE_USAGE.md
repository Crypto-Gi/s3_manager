# Move Directory Usage Guide

## Overview

The `move_r2_directory.py` script moves directories within your S3-compatible bucket by copying objects to a new location and deleting the originals.

## Configuration

### Method 1: Using .env File (Recommended)

Add move operations to your `.env` file:

```env
# Your bucket credentials (required)
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET=your_bucket_name

# Define move operations
MOVE_SOURCE_1=source/ecos-release-notes/
MOVE_DEST_1=source/HPE Aruba/ecos-release-notes/

MOVE_SOURCE_2=source/orch-release-notes/
MOVE_DEST_2=source/HPE Aruba/orch-release-notes/

# Add more moves as needed
MOVE_SOURCE_3=old/path/
MOVE_DEST_3=new/path/
```

### Method 2: Edit Script Directly

If you don't add move operations to `.env`, the script will use default example moves. You can also edit the `moves` list directly in the `main()` function:

```python
moves = [
    {
        'source': 'your/source/path/',
        'destination': 'your/destination/path/'
    },
    {
        'source': 'another/source/',
        'destination': 'another/destination/'
    }
]
```

## Usage

### Run the Script

```bash
python3 move_r2_directory.py
```

Or use the helper script:

```bash
./run_move.sh
```

### What Happens

1. **Scan**: Script lists all objects in source directories
2. **Preview**: Shows what will be moved
3. **Confirmation**: Asks for "yes" to proceed
4. **Move**: Copies each object to new location, then deletes original
5. **Report**: Shows statistics (moved count, errors)

## Example

### Current Structure
```
releasenotes/
└── source/
    ├── ecos-release-notes/
    │   ├── file1.md
    │   └── subfolder/
    │       └── file2.md
    └── orch-release-notes/
        └── file3.md
```

### After Move
```
releasenotes/
└── source/
    └── HPE Aruba/
        ├── ecos-release-notes/
        │   ├── file1.md
        │   └── subfolder/
        │       └── file2.md
        └── orch-release-notes/
            └── file3.md
```

## Important Notes

- **Paths must end with `/`** for directories
- **Original files are deleted** after successful copy
- **Structure is preserved** - all subdirectories and files maintain their relative paths
- **Safe operation** - copies before deleting
- **Confirmation required** - script asks before proceeding

## Troubleshooting

### No move operations found
Add `MOVE_SOURCE_1` and `MOVE_DEST_1` to your `.env` file, or edit the script directly.

### Objects not found
Check that your source path is correct and exists in the bucket.

### Permission errors
Verify your credentials have read, write, and delete permissions.

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `R2_ACCOUNT_ID` | Yes | S3 endpoint or account ID |
| `R2_ACCESS_KEY_ID` | Yes | Access key ID |
| `R2_SECRET_ACCESS_KEY` | Yes | Secret access key |
| `R2_BUCKET` | Yes | Bucket name |
| `MOVE_SOURCE_1` | Optional | First source directory path |
| `MOVE_DEST_1` | Optional | First destination directory path |
| `MOVE_SOURCE_2` | Optional | Second source directory path |
| `MOVE_DEST_2` | Optional | Second destination directory path |
| ... | Optional | Continue numbering for more moves |
