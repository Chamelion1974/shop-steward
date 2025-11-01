#!/usr/bin/env python3
"""
Shop Steward - File Organization System for CNC Programming

This script acts as a housekeeper/hall monitor for machine shop files.
It organizes files into proper folders based on their type and purpose,
creating the necessary folder structure if it doesn't exist.

Folder Structure:
- CAD: CAD design files
- CAM: CAM programming files
- NC Files: CNC machine code files
  - PROVEN: Tested and verified NC files
  - UNPROVEN: New or untested NC files
- MPI: Manufacturing Process Instructions
- ARCHIVE: Extra/unused data (nothing is deleted!)
- HOLDING: Files that cannot be categorized

"""

import shutil
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Try to load custom configuration if it exists
try:
    from config import CUSTOM_FOLDERS, CUSTOM_FILE_CATEGORIES
    USE_CUSTOM_CONFIG = True
except ImportError:
    USE_CUSTOM_CONFIG = False


class ShopSteward:
    """Main class for organizing CNC programming files."""
    
    # Log filename constant
    LOG_FILENAME = 'shop_steward.log'
    
    # Default folder structure
    FOLDERS = {
        'CAD': 'CAD',
        'CAM': 'CAM',
        'NC_FILES': 'NC Files',
        'NC_PROVEN': 'NC Files/PROVEN',
        'NC_UNPROVEN': 'NC Files/UNPROVEN',
        'MPI': 'MPI',
        'ARCHIVE': 'ARCHIVE',
        'HOLDING': 'HOLDING'
    }
    
    # File extension mappings for categorization
    FILE_CATEGORIES = {
        'CAD': ['.step', '.stp', '.igs', '.iges', '.stl', '.dwg', '.dxf', '.catpart', '.catproduct', '.prt', '.sldprt', '.sldasm'],
        'CAM': ['.mcam', '.cam', '.camproj', '.ncl', '.ncp', '.operations'],
        'NC_UNPROVEN': ['.nc', '.cnc', '.tap', '.mpf', '.ngc', '.eia', '.min', '.din'],
        'MPI': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls'],
    }
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        """
        Initialize the Shop Steward.
        
        Args:
            root_dir: Root directory where folders will be created/managed
            dry_run: If True, only log what would be done without making changes
        """
        self.root_dir = Path(root_dir).resolve()
        self.dry_run = dry_run
        
        # Load custom configuration if available
        if USE_CUSTOM_CONFIG:
            self.FOLDERS = CUSTOM_FOLDERS
            self.FILE_CATEGORIES = CUSTOM_FILE_CATEGORIES
            
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the application."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.root_dir / self.LOG_FILENAME)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_folder_structure(self):
        """Create the standard folder structure if it doesn't exist."""
        self.logger.info(f"Creating folder structure in: {self.root_dir}")
        
        for folder_name, folder_path in self.FOLDERS.items():
            full_path = self.root_dir / folder_path
            
            if not full_path.exists():
                if self.dry_run:
                    self.logger.info(f"[DRY RUN] Would create: {full_path}")
                else:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created: {full_path}")
            else:
                self.logger.debug(f"Already exists: {full_path}")
                
    def categorize_file(self, file_path: Path) -> Optional[str]:
        """
        Determine which category a file belongs to based on its extension.
        
        Args:
            file_path: Path to the file to categorize
            
        Returns:
            Category name (key from FOLDERS) or None if uncategorizable
        """
        extension = file_path.suffix.lower()
        
        for category, extensions in self.FILE_CATEGORIES.items():
            if extension in extensions:
                return category
                
        return None
        
    def move_file(self, source: Path, destination_folder: str, preserve_structure: bool = False) -> bool:
        """
        Move a file to its appropriate destination folder.
        
        Args:
            source: Source file path
            destination_folder: Key from FOLDERS dict
            preserve_structure: If True, preserve relative path structure
            
        Returns:
            True if successful, False otherwise
        """
        if not source.exists() or not source.is_file():
            self.logger.warning(f"Source file not found or not a file: {source}")
            return False
            
        dest_dir = self.root_dir / self.FOLDERS[destination_folder]
        
        # Create subdirectory structure if preserving
        if preserve_structure:
            try:
                rel_path = source.parent.relative_to(self.root_dir)
                dest_dir = dest_dir / rel_path
            except ValueError:
                # Source is not within root_dir, don't preserve structure
                self.logger.debug(f"Source {source} not in root_dir, not preserving structure")
            
        # Ensure destination directory exists
        if not self.dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            
        dest_path = dest_dir / source.name
        
        # Handle duplicate filenames
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = dest_path.stem
            suffix = dest_path.suffix
            dest_path = dest_dir / f"{stem}_{timestamp}{suffix}"
            self.logger.warning(f"Duplicate filename detected, renaming to: {dest_path.name}")
            
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would move: {source} -> {dest_path}")
            else:
                shutil.move(str(source), str(dest_path))
                self.logger.info(f"Moved: {source.name} -> {dest_path.parent}")
            return True
        except Exception as e:
            self.logger.error(f"Error moving {source} to {dest_path}: {e}")
            return False
            
    def organize_files(self, source_dir: Optional[str] = None, recursive: bool = True):
        """
        Organize all files in the source directory.
        
        Args:
            source_dir: Directory to scan for files (defaults to root_dir)
            recursive: Whether to scan subdirectories recursively
        """
        if source_dir is None:
            source_dir = self.root_dir
        else:
            source_dir = Path(source_dir).resolve()
            
        self.logger.info(f"Organizing files in: {source_dir}")
        
        # Get list of managed folders to avoid processing files already in place
        managed_folders = {self.root_dir / folder for folder in self.FOLDERS.values()}
        
        # Find all files
        if recursive:
            file_pattern = source_dir.rglob('*')
        else:
            file_pattern = source_dir.glob('*')
            
        files_processed = 0
        files_categorized = 0
        files_held = 0
        
        for file_path in file_pattern:
            # Skip directories, hidden files, and log files
            if not file_path.is_file() or file_path.name.startswith('.') or file_path.name == self.LOG_FILENAME:
                continue
                
            # Skip files already in managed folders
            try:
                # Check if file is in any managed folder
                if any(file_path.is_relative_to(folder) for folder in managed_folders):
                    continue
            except (ValueError, TypeError):
                # Fallback for Python < 3.9 or edge cases
                if any(str(file_path).startswith(str(folder)) for folder in managed_folders):
                    continue
                
            files_processed += 1
            
            # Categorize and move the file
            category = self.categorize_file(file_path)
            
            if category:
                if self.move_file(file_path, category):
                    files_categorized += 1
            else:
                # Move to HOLDING for manual review
                self.logger.warning(f"Cannot categorize: {file_path.name}")
                if self.move_file(file_path, 'HOLDING'):
                    files_held += 1
                    
        self.logger.info(f"Processing complete: {files_processed} files processed, "
                        f"{files_categorized} categorized, {files_held} sent to HOLDING")
                        
    def archive_folder(self, folder_path: str):
        """
        Move an entire folder to ARCHIVE.
        
        Args:
            folder_path: Path to the folder to archive
        """
        source = Path(folder_path).resolve()
        
        if not source.exists() or not source.is_dir():
            self.logger.error(f"Source folder not found or not a directory: {source}")
            return
            
        archive_dir = self.root_dir / self.FOLDERS['ARCHIVE']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = archive_dir / f"{source.name}_{timestamp}"
        
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would archive: {source} -> {dest_path}")
            else:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(dest_path))
                self.logger.info(f"Archived: {source} -> {dest_path}")
        except Exception as e:
            self.logger.error(f"Error archiving {source}: {e}")


def main():
    """Main entry point for the Shop Steward application."""
    parser = argparse.ArgumentParser(
        description='Shop Steward - File organization system for CNC Programming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize folder structure in current directory
  python shop_steward.py --init

  # Organize files in a specific directory
  python shop_steward.py --organize /path/to/files

  # Dry run to see what would happen
  python shop_steward.py --organize /path/to/files --dry-run

  # Archive a folder
  python shop_steward.py --archive /path/to/old/project
        """
    )
    
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory for the shop steward system (default: current directory)'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize the folder structure'
    )
    
    parser.add_argument(
        '--organize',
        type=str,
        metavar='DIR',
        help='Organize files in the specified directory'
    )
    
    parser.add_argument(
        '--archive',
        type=str,
        metavar='DIR',
        help='Move a folder to ARCHIVE'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not process subdirectories recursively'
    )
    
    args = parser.parse_args()
    
    # Create Shop Steward instance
    steward = ShopSteward(root_dir=args.root, dry_run=args.dry_run)
    
    # Execute requested action
    if args.init:
        steward.create_folder_structure()
        
    if args.organize:
        steward.create_folder_structure()  # Ensure structure exists
        steward.organize_files(source_dir=args.organize, recursive=not args.no_recursive)
        
    if args.archive:
        steward.archive_folder(args.archive)
        
    if not (args.init or args.organize or args.archive):
        parser.print_help()


if __name__ == '__main__':
    main()
