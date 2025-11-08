#!/usr/bin/env python3
"""
Script to delete all objects from a Cloudflare R2 bucket using S3 API.
Uses boto3 with S3-compatible endpoint for Cloudflare R2.

Note: This script requires Python 3.6+ (uses f-strings)
Run with: python3 delete_r2_bucket.py
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

def delete_all_objects(bucket_name, prefix=''):
    """
    Delete all objects from the specified R2 bucket.
    
    Args:
        bucket_name: Name of the R2 bucket
        prefix: Optional prefix to filter objects (default: '' for all objects)
    """
    s3_client = get_r2_client()
    
    print(f"Starting deletion process for bucket: {bucket_name}")
    if prefix:
        print(f"Filtering objects with prefix: {prefix}")
    
    deleted_count = 0
    error_count = 0
    
    try:
        # Use paginator to handle large number of objects
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        for page in pages:
            if 'Contents' not in page:
                print("No objects found in bucket.")
                break
            
            # Prepare objects for batch deletion (max 1000 per request)
            objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
            
            if not objects_to_delete:
                continue
            
            print(f"Deleting {len(objects_to_delete)} objects...")
            
            # Delete objects in batch
            response = s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects': objects_to_delete,
                    'Quiet': False
                }
            )
            
            # Count successful deletions
            if 'Deleted' in response:
                deleted_count += len(response['Deleted'])
                for obj in response['Deleted']:
                    print(f"  ✓ Deleted: {obj['Key']}")
            
            # Report errors
            if 'Errors' in response:
                error_count += len(response['Errors'])
                for error in response['Errors']:
                    print(f"  ✗ Error deleting {error['Key']}: {error['Code']} - {error['Message']}")
        
        print(f"\n{'='*60}")
        print(f"Deletion complete!")
        print(f"Successfully deleted: {deleted_count} objects")
        if error_count > 0:
            print(f"Errors encountered: {error_count} objects")
        print(f"{'='*60}")
        
    except ClientError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main function to execute the deletion script."""
    bucket_name = os.getenv('R2_BUCKET')
    prefix = os.getenv('R2_PREFIX', '')
    
    if not bucket_name:
        print("Error: R2_BUCKET not set in .env file")
        sys.exit(1)
    
    # Confirmation prompt
    print(f"\n{'='*60}")
    print(f"WARNING: This will delete ALL objects from bucket: {bucket_name}")
    if prefix:
        print(f"With prefix filter: {prefix}")
    print(f"{'='*60}\n")
    
    confirmation = input("Are you sure you want to continue? (yes/no): ")
    
    if confirmation.lower() != 'yes':
        print("Operation cancelled.")
        sys.exit(0)
    
    delete_all_objects(bucket_name, prefix)

if __name__ == "__main__":
    main()
