#!/usr/bin/env python3
"""
Script to upload a directory to Cloudflare R2 bucket using S3 API.
Maintains the folder hierarchy in the bucket.

Note: This script requires Python 3.6+ (uses f-strings)
Run with: python3 upload_to_r2.py
"""

import os
import sys
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

def upload_directory(source_dir, bucket_name, prefix=''):
    """
    Upload all files from source directory to R2 bucket maintaining hierarchy.
    
    Args:
        source_dir: Local directory path to upload
        bucket_name: Name of the R2 bucket
        prefix: Optional prefix to add to all uploaded objects
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
    
    print(f"Starting upload from: {source_dir}")
    print(f"To bucket: {bucket_name}/{source_folder_name}")
    if prefix:
        print(f"With additional prefix: {prefix}")
    print(f"{'='*60}\n")
    
    uploaded_count = 0
    error_count = 0
    skipped_count = 0
    total_size = 0
    
    # Walk through all files in the directory
    for root, dirs, files in os.walk(source_dir):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            
            # Calculate relative path from source directory
            relative_path = os.path.relpath(local_file_path, source_dir)
            
            # Construct the S3 key (object path in bucket)
            # Include the source folder name as root, then the relative path
            if prefix:
                s3_key = os.path.join(prefix, source_folder_name, relative_path).replace('\\', '/')
            else:
                s3_key = os.path.join(source_folder_name, relative_path).replace('\\', '/')
            
            try:
                # Get file size
                file_size = os.path.getsize(local_file_path)
                
                # Determine content type
                content_type = get_content_type(local_file_path)
                
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
                total_size += file_size
                print(f"  ✓ Uploaded successfully\n")
                
            except ClientError as e:
                error_count += 1
                print(f"  ✗ Error: {e}\n")
            except Exception as e:
                error_count += 1
                print(f"  ✗ Unexpected error: {e}\n")
    
    # Print summary
    print(f"{'='*60}")
    print(f"Upload complete!")
    print(f"Successfully uploaded: {uploaded_count} files")
    print(f"Total size: {format_size(total_size)}")
    if error_count > 0:
        print(f"Errors encountered: {error_count} files")
    if skipped_count > 0:
        print(f"Skipped: {skipped_count} files")
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
    bucket_name = os.getenv('R2_BUCKET')
    source_dir = os.getenv('R2_SOURCE_DIR')
    prefix = os.getenv('R2_PREFIX', '')
    
    if not bucket_name:
        print("Error: R2_BUCKET not set in .env file")
        sys.exit(1)
    
    if not source_dir:
        print("Error: R2_SOURCE_DIR not set in .env file")
        sys.exit(1)
    
    # Confirmation prompt
    print(f"\n{'='*60}")
    print(f"Upload Configuration:")
    print(f"  Source: {source_dir}")
    print(f"  Bucket: {bucket_name}")
    if prefix:
        print(f"  Prefix: {prefix}")
    print(f"{'='*60}\n")
    
    confirmation = input("Start upload? (yes/no): ")
    
    if confirmation.lower() != 'yes':
        print("Operation cancelled.")
        sys.exit(0)
    
    upload_directory(source_dir, bucket_name, prefix)

if __name__ == "__main__":
    main()
