# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [v0.6] - 2025-01-10

### Added
- **Hybrid duplicate detection**: Combines filename-based filtering with xxhash content verification
- **xxhash integration**: Computes xxhash64 for all uploaded files
- **Metadata storage**: Stores xxhash in S3 object metadata for future comparisons
- **Content verification**: Retrieves and compares hashes for files with matching names
- **Smart filtering**: Only calls head_object() for files with matching filenames (performance optimization)

### Changed
- Upload script now uses hybrid approach: filename check first, then hash verification
- Files with same name but different content will be uploaded (not skipped)
- Added hash verification statistics to upload summary
- Enhanced progress output to show xxhash values during upload

### Technical Details
- Added `compute_file_hash()` function using xxhash64 with 64KB chunks
- Modified `get_existing_objects()` to return dict mapping filename→key
- Added `get_file_hash_from_metadata()` to retrieve hashes via head_object()
- Upload process now stores xxhash in Metadata parameter
- Hash checks only performed for files with matching filenames (efficient)

### Dependencies
- Added `xxhash` library requirement (install via `pip install xxhash`)

### Performance
- Minimal performance impact: hash checks only for filename matches
- For 100K files with 1K matches: ~1K head_object() calls (vs 100K for full hash scan)
- xxhash64 is extremely fast: 5-13 GB/s depending on system

## [v0.5] - 2025-01-10

### Changed
- **Upload script**: Changed duplicate detection from path-based to filename-based
- Now checks if filename exists anywhere in bucket, regardless of path
- If `readme.txt` exists anywhere in bucket, all local `readme.txt` files are skipped
- Memory cleanup after determining upload list for better efficiency

### Technical Details
- `get_existing_objects()` now extracts basenames instead of full paths
- Comparison uses `os.path.basename()` for filename-only matching
- Clears filename set from memory after determining files to upload
- Updated documentation to clarify filename-based duplicate detection behavior

### Breaking Changes
- Duplicate detection behavior changed: previously compared full paths, now compares filenames only
- This may result in different files being skipped compared to v0.4

## [v0.3] - 2024-11-25

### Added
- **Move directory script**: New `move_r2_directory.py` for relocating directories within bucket
- Copy-then-delete operation for safe directory moves
- Preview mode showing what will be moved before execution
- Progress tracking for move operations
- Helper script `run_move.sh` for easy execution

### Features
- Move entire directories while preserving structure
- Handles any number of objects efficiently
- Detailed error reporting and recovery
- Customizable move operations via configuration

### Use Cases
- Reorganize bucket structure
- Consolidate directories under common parent
- Rename directory paths

## [v0.2] - 2024-11-08

### Added
- **Incremental upload feature**: Upload script now checks existing files in R2 before uploading
- Pre-upload analysis showing files to upload vs skip
- Memory-efficient in-memory comparison (uses ~150 bytes per file path)
- Detailed statistics showing uploaded and skipped file counts and sizes

### Changed
- Upload script now scans R2 bucket before uploading
- Upload script builds local file list with intended R2 paths
- Enhanced progress reporting with skip notifications
- Improved summary statistics with separate counts for uploaded and skipped files

### Technical Details
- Uses `list_objects_v2` with pagination to fetch all existing objects
- Stores existing object keys in a Python set for O(1) lookup performance
- Memory usage: ~30 MB for 100K files, ~750 MB for 5M files
- Comparison happens in-memory before any uploads begin

## [v0.1] - 2024-11-08

### Added
- Initial release
- Upload script to upload directories to R2 with hierarchy preservation
- Delete script to batch delete all objects from R2 bucket
- Helper scripts for easy execution
- Comprehensive README with usage instructions
- .gitignore for Python and environment files
