#!/usr/bin/env python3
"""
Script to organize legacy markdown files in Cloudflare R2 bucket.
Moves all files from 'releasenotes/markdown/' to 'releasenotes/markdown/legacy/'
EXCEPT those in 'tech_docs_ec' and 'HPE Aruba'.

Run with: python3 organize_legacy_docs.py [--dry-run] [--show-all]
"""

import os
import sys
import argparse
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
BASE_PATH = "markdown/"
LEGACY_PATH = "markdown/legacy/"
KEEP_DIRS = [
    "markdown/tech_docs_ec/",
    "markdown/HPE Aruba/",
    "markdown/legacy/"  # Don't move things already in legacy
]

def get_r2_client():
    """Create and return a boto3 S3 client for R2."""
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key_id = os.getenv('R2_ACCESS_KEY_ID')
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
    
    if not all([account_id, access_key_id, secret_access_key]):
        print("Error: Missing required environment variables (R2_ACCOUNT_ID, etc.)")
        sys.exit(1)
    
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name='auto'
    )

def list_all_objects(s3_client, bucket_name, prefix):
    """List all objects with prefix."""
    objects = []
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects.append(obj['Key'])
    except ClientError as e:
        print(f"Error listing objects: {e}")
        return []
    return objects

def should_move(key):
    """Check if the key should be moved to legacy."""
    # Ensure we are only looking at files inside the base path
    if not key.startswith(BASE_PATH):
        return False
        
    # Check if it's in one of the kept directories
    for keep_dir in KEEP_DIRS:
        if key.startswith(keep_dir):
            return False
            
    return True

def get_destination_key(source_key):
    """Calculate the new key inside legacy folder preserving structure."""
    # source: releasenotes/markdown/somefolder/file.md
    # relative: somefolder/file.md
    # dest: releasenotes/markdown/legacy/somefolder/file.md
    
    relative_path = source_key[len(BASE_PATH):]
    # Remove leading slash if present (though len should handle strict prefix)
    if relative_path.startswith('/'):
        relative_path = relative_path[1:]
        
    return LEGACY_PATH + relative_path

def move_object(s3_client, bucket_name, source_key, dest_key):
    """Copy object to new location and delete original."""
    try:
        copy_source = {'Bucket': bucket_name, 'Key': source_key}
        s3_client.copy_object(
            Bucket=bucket_name,
            Key=dest_key,
            CopySource=copy_source
        )
        s3_client.delete_object(Bucket=bucket_name, Key=source_key)
        return True
    except ClientError as e:
        print(f"  ✗ Error moving {source_key}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Organize legacy markdown files in R2.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without moving files.")
    parser.add_argument("--show-all", action="store_true", help="Show all files to be moved, not just the first 15.")
    args = parser.parse_args()

    bucket_name = os.getenv('R2_BUCKET')
    if not bucket_name:
        print("Error: R2_BUCKET not set in .env")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Legacy Documentation Migration Tool")
    print(f"Bucket: {bucket_name}")
    print(f"Scanning target: {BASE_PATH}")
    print(f"Preserving: {', '.join([d.replace(BASE_PATH, '') for d in KEEP_DIRS])}")
    print(f"{'='*60}\n")

    s3 = get_r2_client()
    all_objects = list_all_objects(s3, bucket_name, BASE_PATH)
    
    if not all_objects:
        print(f"Warning: No objects found at '{BASE_PATH}'.")
        print("Checking root directory for available paths...")
        try:
            root_objects = list_all_objects(s3, bucket_name, "")
            # Get top-level directories/prefixes
            top_level = set()
            for key in root_objects:
                if '/' in key:
                    top_level.add(key.split('/')[0] + '/')
                else:
                    top_level.add(key)
            
            print(f"Available top-level paths in '{bucket_name}':")
            for path in sorted(top_level):
                print(f"  - {path}")
            
            if not top_level:
                print("  (Bucket appears to be empty)")
                
        except Exception as e:
            print(f"Could not list root objects: {e}")
            
        print("\nPlease optimize your BASE_PATH or check your .env configuration.")
        return

    to_move = []
    for key in all_objects:
        if should_move(key):
            to_move.append(key)
            
    if not to_move:
        print("No files found that need moving. Everything is already organized!")
        return

    print(f"Found {len(to_move)} files to move to '{LEGACY_PATH}'.\n")

    # Preview
    preview_count = len(to_move) if args.show_all else 15
    print(f"Preview of moves:")
    for i, key in enumerate(to_move[:preview_count]):
        dest = get_destination_key(key)
        print(f"  {key}")
        print(f"  → {dest}")
        print()
    
    if len(to_move) > preview_count:
        print(f"  ... and {len(to_move) - preview_count} more files.")
        print("  (Use --show-all to see the full list)")
    
    print(f"\nTotal files to move: {len(to_move)}")
    
    if args.dry_run:
        print(f"\n{'='*60}")
        print("DRY RUN COMPLETE - No changes made.")
        print(f"{'='*60}")
        return

    # Confirmation
    print(f"\n{'='*60}")
    confirm = input("Are you sure you want to move these files? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return

    print(f"\nStarting migration...")
    print(f"{'='*60}")
    
    success_count = 0
    error_count = 0
    
    for i, key in enumerate(to_move, 1):
        dest = get_destination_key(key)
        print(f"[{i}/{len(to_move)}] Moving: {key.split('/')[-1]}...", end='', flush=True)
        
        if move_object(s3, bucket_name, key, dest):
            print(" Done")
            success_count += 1
        else:
            print(" Failed")
            error_count += 1
            
    print(f"\n{'='*60}")
    print("Migration Complete")
    print(f"Successfully moved: {success_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
