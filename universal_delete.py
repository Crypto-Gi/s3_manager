#!/usr/bin/env python3
"""
Universal Deletion Script for Cloudflare R2
-------------------------------------------
SAFELY deletes files based on:
1. Folder path (recursive)
2. File extensions
3. Filename patterns

Features:
- Strict double-confirmation (Type 'DELETE' -> Type 'y')
- Dry-run mode
- Summary previews
"""

import os
import sys
import argparse
import boto3
import fnmatch
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def get_r2_client():
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key_id = os.getenv('R2_ACCESS_KEY_ID')
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
    
    if not all([account_id, access_key_id, secret_access_key]):
        print("Error: Missing environment variables (R2_ACCOUNT_ID, etc.)")
        sys.exit(1)
    
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    return boto3.client('s3', endpoint_url=endpoint_url,
                       aws_access_key_id=access_key_id,
                       aws_secret_access_key=secret_access_key,
                       region_name='auto')

def list_objects(s3, bucket, prefix):
    objects = []
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects.append(obj['Key'])
    except ClientError as e:
        print(f"Error listing objects: {e}")
    return objects

def match_criteria(key, folder, extensions, patterns):
    # Filter by folder
    if folder:
        # Normalize folder to ensure it ends with / for prefix matching
        folder_prefix = folder if folder.endswith('/') else folder + '/'
        if not key.startswith(folder_prefix):
            return False, None

    filename = key.split('/')[-1]
    
    # If no specific patterns/extensions provided, and folder IS provided, match everything in folder
    if folder and not extensions and not patterns:
        return True, "matches folder"

    # Filter by extension
    if extensions:
        for ext in extensions:
            if filename.lower().endswith(ext.lower()):
                return True, f"extension '{ext}'"

    # Filter by pattern (supports wildcards)
    if patterns:
        for pat in patterns:
            # Check for direct substring match OR wildcard match
            if pat.lower() in filename.lower() or fnmatch.fnmatch(filename.lower(), pat.lower()):
                 return True, f"pattern '{pat}'"

    return False, None

def main():
    example_text = """
EXAMPLES:
  1. Delete by Extension:
     python3 universal_delete.py --extensions .tmp,.bak
     -> Deletes all files ending in .tmp or .bak found anywhere in the bucket.

  2. Delete by Pattern in a specific folder:
     python3 universal_delete.py --folder source/logs --patterns error*,*fail*
     -> Deletes files matching "error*" OR "*fail*" (e.g., 'error_log.txt', 'sys_fail_01').
     -> Supports '*' (any string) and '?' (any single character).

  3. Use Single Character Wildcard (?):
     python3 universal_delete.py --patterns "log_?.txt"
     -> Deletes 'log_1.txt', 'log_A.txt', but NOT 'log_10.txt' or 'log.txt'.

  4. Cleanup a Legacy Folder:
     python3 universal_delete.py --folder markdown/legacy
     -> Deletes the 'markdown/legacy' folder and EVERYTHING inside it.
     
  5. Delete the Bucket Itself:
     python3 universal_delete.py --delete-bucket
     -> Deletes the entire bucket (must be empty first).
"""
    parser = argparse.ArgumentParser(
        description="Universal R2 Deletion Tool with Safety First",
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--folder", help="Target specific folder path (e.g. 'markdown/legacy')")
    parser.add_argument("--extensions", help="Comma-separated extensions (e.g. '.tmp,.bak')")
    parser.add_argument("--patterns", help="Comma-separated patterns (e.g. 'img_*, log_?.txt'). Supports wildcards.")
    parser.add_argument("--delete-bucket", action="store_true", help="Delete the bucket itself (Bucket must be empty)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no deletion")
    parser.add_argument("--show-all", action="store_true", help="Show all files in preview")
    
    args = parser.parse_args()
    
    # Check if at least one action is specified
    if not any([args.folder, args.extensions, args.patterns, args.delete_bucket]):
        parser.print_help()
        print("\nError: You must specify a target (--folder, --extensions, --patterns) OR action (--delete-bucket)")
        sys.exit(1)

    bucket = os.getenv('R2_BUCKET')
    if not bucket:
        print("Error: R2_BUCKET not set in .env")
        sys.exit(1)

    # Parse lists
    exts = [e.strip() for e in args.extensions.split(',')] if args.extensions else []
    pats = [p.strip() for p in args.patterns.split(',')] if args.patterns else []
    target_prefix = args.folder if args.folder else ""

    print(f"\n{'='*60}")
    print(f"Universal Deletion Tool - SAFE MODE")
    print(f"Bucket: {bucket}")
    
    if args.delete_bucket:
        print("ACTION: DELETE BUCKET")
    else:
        print(f"Target: {target_prefix if target_prefix else '(Entire Bucket)'}")
        if exts: print(f"Extensions: {exts}")
        if pats: print(f"Patterns: {pats}")
    
    if args.dry_run: print(f"Mode: DRY RUN (No changes)")
    print(f"{'='*60}\n")

    s3 = get_r2_client()

    # --- Mode 1: Delete Bucket ---
    if args.delete_bucket:
        if args.dry_run:
            print(f"[DRY RUN] Would delete bucket '{bucket}'.")
            return

        print(f"WARNING: You are about to delete the ENTIRE BUCKET '{bucket}'.")
        print("The bucket must be empty for this to succeed.")
        
        confirm = input(f"Type 'DELETE {bucket}' to confirm: ")
        if confirm != f"DELETE {bucket}":
            print("Confirmation failed.")
            sys.exit(0)
            
        try:
            s3.delete_bucket(Bucket=bucket)
            print(f"✓ Bucket '{bucket}' deleted successfully.")
        except ClientError as e:
            print(f"✗ Failed to delete bucket: {e}")
            if 'BucketNotEmpty' in str(e):
                print("  Hint: Use this script to delete all files first (python3 universal_delete.py --folder '')")
        return

    # --- Mode 2: Delete Objects ---
    print("Scanning for files...", end='', flush=True)
    all_keys = list_objects(s3, bucket, target_prefix)
    print(f" Done. Scanned {len(all_keys)} objects.")

    targets = []
    for key in all_keys:
        match, reason = match_criteria(key, args.folder, exts, pats)
        if match:
            targets.append((key, reason))

    if not targets:
        print("No matching files found.")
        return

    # PREVIEW PHASE
    print(f"\nFound {len(targets)} files matching criteria.\n")
    limit = len(targets) if args.show_all else 15
    print("Preview:")
    for key, reason in targets[:limit]:
        print(f"  [DELETE] {key} ({reason})")
    
    if len(targets) > limit:
        print(f"  ... and {len(targets) - limit} more files.")
        print("  (Use --show-all to see the full list)")

    if args.dry_run:
        print(f"\n[DRY RUN] Would delete {len(targets)} files. Exiting.")
        return

    # SAFETY GATE 1
    print(f"\n{'!'*60}")
    print(f"WARNING: You are about to PERMANENTLY DELETE {len(targets)} files.")
    print(f"This action cannot be undone.")
    print(f"{'!'*60}\n")
    
    confirm_text = input("To proceed, type 'DELETE' (all caps) and press Enter: ")
    if confirm_text != 'DELETE':
        print("Verification failed. Operation cancelled.")
        sys.exit(0)

    # SAFETY GATE 2 (Summary)
    print(f"\nConfirmed. Final Summary:")
    print(f"  - Action: DELETE FILES")
    print(f"  - Target Count: {len(targets)} files")
    print(f"  - Folder Scope: {args.folder if args.folder else 'Global'}")
    
    confirm_final = input("Are you absolutely sure? (y/n): ")
    if confirm_final.lower() != 'y':
        print("Cancelled at final confirmation.")
        sys.exit(0)

    # EXECUTION
    print(f"\nDeleting files...")
    
    # Batch delete (max 1000)
    batch_size = 1000
    deleted = 0
    errors = 0
    
    for i in range(0, len(targets), batch_size):
        batch = targets[i:i+batch_size]
        objects = [{'Key': k} for k, r in batch]
        
        try:
            resp = s3.delete_objects(
                Bucket=bucket,
                Delete={'Objects': objects, 'Quiet': False}
            )
            if 'Deleted' in resp:
                count = len(resp['Deleted'])
                deleted += count
                print(f"  Batch {i//batch_size + 1}: Deleted {count} files")
            if 'Errors' in resp:
                count = len(resp['Errors'])
                errors += count
                print(f"  Errors in batch: {count}")
        except ClientError as e:
            print(f"  Critical error in batch: {e}")
            errors += len(batch)

    print(f"\n{'='*60}")
    print(f"Operation Complete")
    print(f"Deleted: {deleted}")
    print(f"Errors: {errors}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
