#!/usr/bin/env python3
"""
Script to upload a directory to Cloudflare R2 bucket using S3 API.
Maintains the folder hierarchy in the bucket.

Note: This script requires Python 3.6+ (uses f-strings)
Run with: python3 upload_to_r2.py
"""

import os
import sys
import argparse
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_r2_client():
    """
    Create and return a boto3 S3 client configured for Cloudflare R2.
    """
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key_id = os.getenv('R2_ACCESS_KEY_ID')
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
    
    if not all([account_id, access_key_id, secret_access_key]):
        raise ValueError("Missing required environment variables. Check your .env file.")
    
    # Cloudflare R2 endpoint format
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name='auto'  # R2 uses 'auto' for region
    )
    
    return s3_client

def get_content_type(file_path):
    """
    Determine content type based on file extension.
    """
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'

def get_existing_objects(s3_client, bucket_name, prefix=''):
    """
    Fetch all existing filenames from R2 bucket and return as a set of basenames.
    Uses pagination to handle large buckets.
    
    Note: This function extracts only the filename (basename) from each object key,
    ignoring the full path. This means duplicate detection is filename-based only.
    
    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the R2 bucket
        prefix: Optional prefix to filter objects
        
    Returns:
        set: Set of all filenames (basenames) in the bucket
    """
    print(f"Scanning R2 bucket: {bucket_name}...")
    existing_filenames = set()
    
    try:
        # Use paginator to handle large number of objects
        paginator = s3_client.get_paginator('list_objects_v2')
        
        if prefix:
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        else:
            pages = paginator.paginate(Bucket=bucket_name)
        
        object_count = 0
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Extract only the filename (basename) from the full key
                    filename = os.path.basename(obj['Key'])
                    if filename:  # Skip empty basenames (directories)
                        existing_filenames.add(filename)
                    object_count += 1
        
        print(f"Found {object_count} existing objects ({len(existing_filenames)} unique filenames) in bucket\n")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Warning: Bucket '{bucket_name}' does not exist or is not accessible")
        else:
            print(f"Warning: Error listing bucket contents: {e}")
        print("Proceeding with upload (will upload all files)\n")
    
    return existing_filenames

def build_local_file_list(source_dir, source_folder_name, prefix=''):
    """
    Build a list of local files with their intended R2 paths.
    
    Args:
        source_dir: Local directory path
        source_folder_name: Name of source folder to use as root
        prefix: Optional prefix to add to all objects
        
    Returns:
        list: List of tuples (local_path, s3_key, file_size)
    """
    print(f"Scanning local directory: {source_dir}...")
    local_files = []
    
    for root, dirs, files in os.walk(source_dir):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            
            # Calculate relative path from source directory
            relative_path = os.path.relpath(local_file_path, source_dir)
            
            # Construct the S3 key
            if prefix:
                s3_key = os.path.join(prefix, source_folder_name, relative_path).replace('\\', '/')
            else:
                s3_key = os.path.join(source_folder_name, relative_path).replace('\\', '/')
            
            try:
                file_size = os.path.getsize(local_file_path)
                local_files.append((local_file_path, s3_key, file_size))
            except OSError as e:
                print(f"Warning: Cannot access {local_file_path}: {e}")
    
    print(f"Found {len(local_files)} local files\n")
    return local_files

def upload_directory(source_dir, bucket_name, prefix='', dry_run=False):
    """
    Upload all files from source directory to R2 bucket maintaining hierarchy.
    Only uploads files whose filenames don't already exist in the bucket (filename-based duplicate detection).
    
    Note: Duplicate detection is based on filename only, not full path. If a file named "readme.txt"
    exists anywhere in the bucket, all local "readme.txt" files will be skipped regardless of their path.
    
    Args:
        source_dir: Local directory path to upload
        bucket_name: Name of the R2 bucket
        prefix: Optional prefix to add to all uploaded objects
        dry_run: If True, simulate upload without making changes
    """
    s3_client = get_r2_client()
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"Error: Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"Error: Source path is not a directory: {source_dir}")
        sys.exit(1)
    
    # Get the source folder name to use as root in bucket
    source_folder_name = source_path.name
    
    print(f"{'='*60}")
    print(f"Incremental Upload - Filename-based duplicate detection{' (DRY RUN)' if dry_run else ''}")
    print(f"{'='*60}\n")
    
    # Step 1: Get existing filenames from R2
    existing_filenames = get_existing_objects(s3_client, bucket_name, prefix)
    
    # Step 2: Build local file list
    local_files = build_local_file_list(source_dir, source_folder_name, prefix)
    
    # Step 3: Determine which files need to be uploaded (compare by filename only)
    files_to_upload = []
    files_to_skip = []
    
    for local_path, s3_key, file_size in local_files:
        filename = os.path.basename(local_path)
        if filename in existing_filenames:
            files_to_skip.append((local_path, s3_key, file_size))
        else:
            files_to_upload.append((local_path, s3_key, file_size))
    
    # Clear memory of existing filenames set (no longer needed)
    existing_filenames.clear()
    del existing_filenames
    
    # Calculate statistics
    total_upload_size = sum(size for _, _, size in files_to_upload)
    total_skip_size = sum(size for _, _, size in files_to_skip)
    
    # Display analysis
    print(f"{'='*60}")
    print(f"Analysis:")
    print(f"  Total local files: {len(local_files)}")
    print(f"  New files to upload: {len(files_to_upload)} ({format_size(total_upload_size)})")
    print(f"  Existing files (will skip): {len(files_to_skip)} ({format_size(total_skip_size)})")
    print(f"  Note: Duplicate detection is filename-based (ignores path)")
    print(f"{'='*60}\n")
    
    if len(files_to_upload) == 0:
        print("All files already exist in bucket (by filename). Nothing to upload!")
        return
    
    # Counters
    uploaded_count = 0
    error_count = 0
    skipped_count = len(files_to_skip)
    uploaded_size = 0
    
    print(f"Starting upload to: {bucket_name}/{source_folder_name}")
    if prefix:
        print(f"With additional prefix: {prefix}")
    print(f"{'='*60}\n")
    
    # Upload only new files
    for local_file_path, s3_key, file_size in files_to_upload:
        try:
            # Calculate relative path for display
            relative_path = os.path.relpath(local_file_path, source_dir)
            
            # Determine content type
            content_type = get_content_type(local_file_path)
            
            if dry_run:
                print(f"[DRY RUN] Would upload: {relative_path} -> {s3_key}")
                print(f"  Size: {format_size(file_size)}, Type: {content_type}")
                uploaded_count += 1
                uploaded_size += file_size
                print(f"  ✓ Simulation successful\n")
            else:
                print(f"Uploading: {relative_path} -> {s3_key}")
                print(f"  Size: {format_size(file_size)}, Type: {content_type}")
                
                # Upload the file
                with open(local_file_path, 'rb') as file_data:
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=s3_key,
                        Body=file_data,
                        ContentType=content_type
                    )
                
                uploaded_count += 1
                uploaded_size += file_size
                print(f"  ✓ Uploaded successfully\n")
            
        except ClientError as e:
            error_count += 1
            print(f"  ✗ Error: {e}\n")
        except Exception as e:
            error_count += 1
            print(f"  ✗ Unexpected error: {e}\n")
    
    # Print summary
    print(f"{'='*60}")
    print(f"Upload complete!{' (DRY RUN)' if dry_run else ''}")
    print(f"Successfully {('simulated' if dry_run else 'uploaded')}: {uploaded_count} files ({format_size(uploaded_size)})")
    print(f"Skipped (already exist): {skipped_count} files ({format_size(total_skip_size)})")
    if error_count > 0:
        print(f"Errors encountered: {error_count} files")
    print(f"Total files processed: {len(local_files)}")
    print(f"{'='*60}")

def format_size(bytes_size):
    """
    Format bytes to human-readable size.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def main():
    """Main function to execute the upload script."""
    
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Upload directory to Cloudflare R2 bucket.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate upload without actual execution")
    parser.add_argument("--source", type=str, help="Source directory path (overrides R2_SOURCE_DIR)")
    parser.add_argument("--destination", type=str, help="Destination folder in bucket (overrides R2_PREFIX)")
    parser.add_argument("--bucket", type=str, help="Target R2 bucket name (overrides R2_BUCKET)")
    
    args = parser.parse_args()
    
    # Determine values (CLI args > Env vars)
    bucket_name = args.bucket or os.getenv('R2_BUCKET')
    source_dir = args.source or os.getenv('R2_SOURCE_DIR')
    prefix = args.destination if args.destination is not None else os.getenv('R2_PREFIX', '')
    
    if not bucket_name:
        print("Error: Bucket name not specified. Use --bucket or set R2_BUCKET in .env")
        sys.exit(1)
    
    if not source_dir:
        print("Error: Source directory not specified. Use --source or set R2_SOURCE_DIR in .env")
        sys.exit(1)
    
    # Confirmation prompt (skip if dry-run, optional)
    print(f"\n{'='*60}")
    print(f"Upload Configuration:")
    print(f"  Source: {source_dir}")
    print(f"  Bucket: {bucket_name}")
    if prefix:
        print(f"  Prefix: {prefix}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE UPLOAD'}")
    print(f"{'='*60}\n")
    
    if not args.dry_run:
        confirmation = input("Start upload? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Operation cancelled.")
            sys.exit(0)
    
    upload_directory(source_dir, bucket_name, prefix, args.dry_run)

if __name__ == "__main__":
    main()
