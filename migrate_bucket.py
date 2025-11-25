#!/usr/bin/env python3
"""
Script to migrate/copy objects between S3-compatible buckets.
Uses server-side copy (no download/upload) for fast migration.

Note: This script requires Python 3.6+ (uses f-strings)
Run with: python3 migrate_bucket.py
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_r2_client():
    """
    Create and return a boto3 S3 client configured for S3-compatible storage.
    """
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key_id = os.getenv('R2_ACCESS_KEY_ID')
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
    
    if not all([account_id, access_key_id, secret_access_key]):
        raise ValueError("Missing required environment variables. Check your .env file.")
    
    # S3-compatible endpoint format
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name='auto'
    )
    
    return s3_client

def list_all_objects(s3_client, bucket_name, prefix=''):
    """
    List all objects in the bucket.
    
    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the bucket
        prefix: Optional prefix to filter objects
        
    Returns:
        list: List of object keys
    """
    objects = []
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        
        if prefix:
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        else:
            pages = paginator.paginate(Bucket=bucket_name)
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects.append(obj['Key'])
    
    except ClientError as e:
        print(f"Error listing objects: {e}")
        return []
    
    return objects

def copy_object(s3_client, source_bucket, source_key, dest_bucket, dest_key):
    """
    Copy object from source to destination bucket (server-side copy).
    
    Args:
        s3_client: Boto3 S3 client
        source_bucket: Source bucket name
        source_key: Source object key
        dest_bucket: Destination bucket name
        dest_key: Destination object key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        s3_client.copy_object(
            Bucket=dest_bucket,
            Key=dest_key,
            CopySource=copy_source
        )
        return True
    
    except ClientError as e:
        print(f"  ✗ Error copying {source_key}: {e}")
        return False

def migrate_bucket(source_bucket, dest_bucket, prefix='', delete_source=False):
    """
    Migrate all objects from source bucket to destination bucket.
    
    Args:
        source_bucket: Source bucket name
        dest_bucket: Destination bucket name
        prefix: Optional prefix to filter objects
        delete_source: If True, delete from source after successful copy
    """
    s3_client = get_r2_client()
    
    print(f"{'='*60}")
    print(f"Bucket Migration Tool")
    print(f"{'='*60}")
    print(f"Source bucket: {source_bucket}")
    print(f"Destination bucket: {dest_bucket}")
    if prefix:
        print(f"Prefix filter: {prefix}")
    if delete_source:
        print(f"Mode: MIGRATE (copy + delete source)")
    else:
        print(f"Mode: COPY (keep source)")
    print(f"{'='*60}\n")
    
    # List objects in source bucket
    print(f"Scanning source bucket: {source_bucket}...")
    objects = list_all_objects(s3_client, source_bucket, prefix)
    
    if not objects:
        print("No objects found in source bucket.")
        return
    
    print(f"Found {len(objects)} objects to migrate\n")
    
    # Show preview
    print(f"{'='*60}")
    print(f"Preview (first 10 objects):")
    print(f"{'='*60}")
    for obj_key in objects[:10]:
        print(f"  {obj_key}")
    
    if len(objects) > 10:
        print(f"\n  ... and {len(objects) - 10} more objects")
    
    print(f"\n{'='*60}")
    
    # Confirmation
    if delete_source:
        print(f"⚠️  WARNING: Source objects will be DELETED after copying!")
    print(f"\nThis will copy {len(objects)} objects from '{source_bucket}' to '{dest_bucket}'")
    print(f"Type 'MIGRATE' to confirm: ", end='')
    confirmation = input()
    
    if confirmation != 'MIGRATE':
        print("\n❌ Operation cancelled.")
        return
    
    print("\n✓ Confirmation received. Starting migration...\n")
    
    # Migrate objects
    print(f"{'='*60}")
    print("Copying objects...")
    print(f"{'='*60}\n")
    
    copied_count = 0
    error_count = 0
    deleted_count = 0
    
    for i, obj_key in enumerate(objects, 1):
        print(f"[{i}/{len(objects)}] Copying: {obj_key}")
        
        # Copy object
        if copy_object(s3_client, source_bucket, obj_key, dest_bucket, obj_key):
            copied_count += 1
            print(f"  ✓ Copied successfully")
            
            # Delete from source if requested
            if delete_source:
                try:
                    s3_client.delete_object(Bucket=source_bucket, Key=obj_key)
                    deleted_count += 1
                    print(f"  ✓ Deleted from source")
                except ClientError as e:
                    print(f"  ✗ Error deleting from source: {e}")
        else:
            error_count += 1
        
        print()
    
    # Summary
    print(f"{'='*60}")
    print(f"✓ Migration complete!")
    print(f"{'='*60}")
    print(f"Successfully copied: {copied_count} objects")
    if delete_source:
        print(f"Successfully deleted from source: {deleted_count} objects")
    if error_count > 0:
        print(f"❌ Errors encountered: {error_count} objects")
    else:
        print(f"✓ No errors encountered")
    print(f"{'='*60}")

def main():
    """Main function to execute the migration script."""
    source_bucket = os.getenv('MIGRATE_SOURCE_BUCKET')
    dest_bucket = os.getenv('MIGRATE_DEST_BUCKET')
    prefix = os.getenv('MIGRATE_PREFIX', '')
    delete_source = os.getenv('MIGRATE_DELETE_SOURCE', 'false').lower() == 'true'
    
    if not source_bucket or not dest_bucket:
        print("Error: Migration buckets not configured.")
        print("\nAdd to your .env file:")
        print("MIGRATE_SOURCE_BUCKET=old-bucket-name")
        print("MIGRATE_DEST_BUCKET=new-bucket-name")
        print("MIGRATE_PREFIX=  # Optional: only migrate objects with this prefix")
        print("MIGRATE_DELETE_SOURCE=false  # Set to true to delete from source after copy")
        sys.exit(1)
    
    if source_bucket == dest_bucket:
        print("Error: Source and destination buckets cannot be the same.")
        sys.exit(1)
    
    migrate_bucket(source_bucket, dest_bucket, prefix, delete_source)

if __name__ == "__main__":
    main()
