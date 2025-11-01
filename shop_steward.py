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
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Try to import watchdog for real-time monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

# Try to load custom configuration if it exists
try:
    from config import (
        CUSTOM_FOLDERS,
        CUSTOM_FILE_CATEGORIES,
        CUSTOM_PART_NUMBER_PATTERNS,
        CUSTOM_REVISION_PATTERNS
    )
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

    # Default patterns for extracting part numbers from filenames
    # These patterns try to identify part numbers in various common formats
    PART_NUMBER_PATTERNS = [
        r'([A-Z0-9]{2,}-[A-Z0-9]{2,})',  # Format: ABC-123, XYZ-456A
        r'([A-Z]{2,}\d{3,})',             # Format: ABC123, XYZ456
        r'(\d{4,}-\d{2,})',               # Format: 1234-56, 12345-678
        r'([A-Z]\d{4,})',                 # Format: A1234, X12345
    ]

    # Default patterns for extracting revision levels
    # Common formats: REV-A, R1, V2, etc.
    REVISION_PATTERNS = [
        r'(?:REV|Rev|rev)[-_]?([A-Z0-9]+)',  # REV-A, Rev_B, revC
        r'(?:R|r)(\d+)',                       # R1, r2
        r'(?:V|v)(\d+)',                       # V1, v2
        r'[-_]([A-Z])(?:[-_\.]|$)',           # -A, _B, .C
    ]
    
    # Expected naming convention: PARTNUMBER_REV-X_description.ext
    # Example: ABC-123_REV-A_housing.step
    NAMING_CONVENTION_PATTERN = r'^([A-Z0-9\-]+)_(REV-[A-Z0-9]+|R\d+|V\d+)_(.+)\.[a-z0-9]+$'

    def __init__(self, root_dir: str, dry_run: bool = False, hierarchical: bool = False,
                 enforce_naming: bool = False, auto_rename: bool = False):
        """
        Initialize the Shop Steward.

        Args:
            root_dir: Root directory where folders will be created/managed
            dry_run: If True, only log what would be done without making changes
            hierarchical: If True, organize into Customer/Part#-Rev/folders structure
            enforce_naming: If True, validate filenames against naming conventions
            auto_rename: If True, automatically rename files to match conventions
        """
        self.root_dir = Path(root_dir).resolve()
        self.dry_run = dry_run
        self.hierarchical = hierarchical
        self.enforce_naming = enforce_naming
        self.auto_rename = auto_rename
        self.forced_customer = None  # Can be set to override customer detection
        self.naming_violations = []  # Track naming convention violations

        # Load custom configuration if available
        if USE_CUSTOM_CONFIG:
            self.FOLDERS = CUSTOM_FOLDERS
            self.FILE_CATEGORIES = CUSTOM_FILE_CATEGORIES
            if hasattr(self, 'CUSTOM_PART_NUMBER_PATTERNS'):
                self.PART_NUMBER_PATTERNS = CUSTOM_PART_NUMBER_PATTERNS
            if hasattr(self, 'CUSTOM_REVISION_PATTERNS'):
                self.REVISION_PATTERNS = CUSTOM_REVISION_PATTERNS

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

    def extract_part_number(self, filename: str) -> Optional[str]:
        """
        Extract part number from filename using configured patterns.

        Args:
            filename: The filename to extract part number from

        Returns:
            Extracted part number or None if not found
        """
        for pattern in self.PART_NUMBER_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def extract_revision(self, filename: str) -> Optional[str]:
        """
        Extract revision level from filename using configured patterns.

        Args:
            filename: The filename to extract revision from

        Returns:
            Extracted revision or None if not found
        """
        for pattern in self.REVISION_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def validate_naming_convention(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if filename follows the expected naming convention.

        Expected format: PARTNUMBER_REV-X_description.ext
        Example: ABC-123_REV-A_housing.step

        Args:
            filename: The filename to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check against naming convention pattern
        match = re.match(self.NAMING_CONVENTION_PATTERN, filename, re.IGNORECASE)

        if match:
            return (True, None)

        # Provide specific error message
        part_num = self.extract_part_number(filename)
        revision = self.extract_revision(filename)

        if not part_num and not revision:
            return (False, "Missing both part number and revision")
        elif not part_num:
            return (False, "Missing part number")
        elif not revision:
            return (False, "Missing revision level")
        else:
            return (False, "Incorrect format - expected: PARTNUMBER_REV-X_description.ext")

    def suggest_filename(self, file_path: Path) -> Optional[str]:
        """
        Suggest a properly formatted filename based on the current filename.

        Args:
            file_path: Path to the file

        Returns:
            Suggested filename or None if cannot be determined
        """
        filename = file_path.stem  # without extension
        extension = file_path.suffix

        # Extract components
        part_num = self.extract_part_number(filename)
        revision = self.extract_revision(filename)

        if not part_num:
            return None

        # Normalize revision format
        if revision:
            # Standardize to REV-X format
            if revision.isdigit():
                rev_formatted = f"REV-{revision}"
            elif len(revision) == 1 and revision.isalpha():
                rev_formatted = f"REV-{revision}"
            else:
                rev_formatted = f"REV-{revision}"
        else:
            rev_formatted = "REV-A"  # Default to REV-A if no revision found

        # Try to extract description (anything that's not part number or revision)
        description = filename
        # Remove part number
        description = re.sub(re.escape(part_num), '', description, flags=re.IGNORECASE)
        # Remove revision
        if revision:
            description = re.sub(f"(?:REV|Rev|rev|R|r|V|v)[-_]?{re.escape(revision)}", '', description, flags=re.IGNORECASE)
        # Clean up separators
        description = re.sub(r'^[-_\s]+|[-_\s]+$', '', description)
        description = re.sub(r'[-_\s]+', '_', description)

        if not description:
            description = "file"

        # Construct suggested filename
        suggested = f"{part_num}_{rev_formatted}_{description}{extension}"
        return suggested.lower() if extension.lower() != extension else suggested

    def rename_file_to_convention(self, file_path: Path) -> Optional[Path]:
        """
        Rename a file to match naming conventions.

        Args:
            file_path: Path to the file to rename

        Returns:
            New path after renaming, or None if failed
        """
        suggested = self.suggest_filename(file_path)

        if not suggested:
            self.logger.warning(f"Cannot suggest filename for: {file_path.name}")
            return None

        new_path = file_path.parent / suggested

        # Check if target already exists
        if new_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = new_path.stem
            suffix = new_path.suffix
            new_path = file_path.parent / f"{stem}_{timestamp}{suffix}"

        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would rename: {file_path.name} -> {new_path.name}")
            else:
                file_path.rename(new_path)
                self.logger.info(f"Renamed: {file_path.name} -> {new_path.name}")
            return new_path
        except Exception as e:
            self.logger.error(f"Error renaming {file_path.name}: {e}")
            return None

    def check_and_fix_naming(self, file_path: Path) -> Tuple[bool, Path]:
        """
        Check naming convention and optionally fix it.

        Args:
            file_path: Path to file to check

        Returns:
            Tuple of (is_compliant, final_path)
        """
        is_valid, error = self.validate_naming_convention(file_path.name)

        if is_valid:
            return (True, file_path)

        # Record violation
        violation = {
            'file': file_path.name,
            'error': error,
            'suggestion': self.suggest_filename(file_path)
        }
        self.naming_violations.append(violation)

        if self.enforce_naming:
            self.logger.warning(f"NAMING VIOLATION: {file_path.name} - {error}")

            if self.auto_rename:
                # Try to auto-rename
                new_path = self.rename_file_to_convention(file_path)
                if new_path:
                    return (True, new_path)
                else:
                    return (False, file_path)
            else:
                # Just suggest
                if violation['suggestion']:
                    self.logger.info(f"  Suggested name: {violation['suggestion']}")
                return (False, file_path)
        else:
            # Just log the issue
            self.logger.debug(f"Naming convention issue: {file_path.name} - {error}")
            return (True, file_path)  # Continue processing anyway

    def generate_naming_report(self) -> str:
        """
        Generate a report of naming convention violations.

        Returns:
            Formatted report string
        """
        if not self.naming_violations:
            return "No naming convention violations detected."

        report = ["\n" + "="*60]
        report.append("NAMING CONVENTION VIOLATIONS REPORT")
        report.append("="*60 + "\n")

        for i, violation in enumerate(self.naming_violations, 1):
            report.append(f"{i}. File: {violation['file']}")
            report.append(f"   Issue: {violation['error']}")
            if violation['suggestion']:
                report.append(f"   Suggested: {violation['suggestion']}")
            report.append("")

        report.append(f"Total violations: {len(self.naming_violations)}")
        report.append("="*60 + "\n")

        return "\n".join(report)

    def extract_customer_from_path(self, file_path: Path) -> Optional[str]:
        """
        Extract customer name from file path.
        Looks for customer folder in path hierarchy.

        Args:
            file_path: The file path to extract customer from

        Returns:
            Customer name or None if not found
        """
        # Try to find a customer folder in the path
        # Look for a parent directory that's not a standard folder
        parts = file_path.parts
        standard_folders = set(self.FOLDERS.values())

        for part in reversed(parts):
            # Skip the root dir, standard folders, and the filename
            if part not in standard_folders and part != self.root_dir.name and part != file_path.name:
                # This might be a customer folder
                return part

        return None

    def create_hierarchical_structure(self, customer: str, part_number: str, revision: Optional[str] = None) -> Path:
        """
        Create hierarchical folder structure: Customer/PartNumber-RevX/folders

        Args:
            customer: Customer name
            part_number: Part number
            revision: Revision level (optional)

        Returns:
            Path to the part folder
        """
        # Create customer folder
        customer_path = self.root_dir / customer

        # Create part folder with revision if available
        if revision:
            part_folder_name = f"{part_number}-REV-{revision}"
        else:
            part_folder_name = part_number

        part_path = customer_path / part_folder_name

        if not self.dry_run:
            part_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created hierarchical structure: {part_path}")

            # Create standard subfolders within the part folder
            for folder_key, folder_name in self.FOLDERS.items():
                subfolder = part_path / folder_name
                subfolder.mkdir(parents=True, exist_ok=True)
        else:
            self.logger.info(f"[DRY RUN] Would create hierarchical structure: {part_path}")

        return part_path

    def get_hierarchical_destination(self, file_path: Path, category: str) -> Optional[Tuple[Path, str]]:
        """
        Determine destination folder in hierarchical structure.

        Args:
            file_path: Source file path
            category: File category (key from FOLDERS)

        Returns:
            Tuple of (base_path, customer_name) or None if unable to determine
        """
        # Extract metadata from filename
        filename = file_path.stem  # filename without extension
        part_number = self.extract_part_number(filename)
        revision = self.extract_revision(filename)

        if not part_number:
            self.logger.warning(f"Could not extract part number from: {file_path.name}")
            return None

        # Try to extract customer from path, or use forced customer
        if self.forced_customer:
            customer = self.forced_customer
        else:
            customer = self.extract_customer_from_path(file_path)

        # If no customer found in path, use UNKNOWN
        if not customer:
            self.logger.warning(f"Could not determine customer for: {file_path.name}")
            customer = "UNKNOWN_CUSTOMER"

        # Create hierarchical structure
        part_base_path = self.create_hierarchical_structure(customer, part_number, revision)

        return (part_base_path, customer)

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

        # Determine destination based on mode
        if self.hierarchical:
            # Use hierarchical structure
            result = self.get_hierarchical_destination(source, destination_folder)
            if result:
                part_base_path, customer = result
                dest_dir = part_base_path / self.FOLDERS[destination_folder]
            else:
                # Fall back to HOLDING if we can't determine hierarchy
                dest_dir = self.root_dir / self.FOLDERS['HOLDING']
                self.logger.warning(f"Using HOLDING folder for: {source.name}")
        else:
            # Use flat structure
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

            # Check and optionally fix naming convention
            if self.enforce_naming or self.auto_rename:
                is_compliant, file_path = self.check_and_fix_naming(file_path)
                if self.enforce_naming and not is_compliant and not self.auto_rename:
                    # Naming violation and not auto-renaming - send to HOLDING
                    self.logger.warning(f"Sending to HOLDING due to naming violation: {file_path.name}")
                    if self.move_file(file_path, 'HOLDING'):
                        files_held += 1
                    continue

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

        # Generate naming report if there were violations
        if self.naming_violations:
            report = self.generate_naming_report()
            self.logger.info(report)

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


class ShopStewardWatcher(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """
    File system watcher that monitors directories for new files
    and automatically organizes them using Shop Steward.
    """

    def __init__(self, shop_steward: ShopSteward, watch_dir: str, debounce_seconds: float = 2.0):
        """
        Initialize the watcher.

        Args:
            shop_steward: ShopSteward instance to use for organizing files
            watch_dir: Directory to monitor for new files
            debounce_seconds: Wait time before processing a new file (to avoid partial uploads)
        """
        if not WATCHDOG_AVAILABLE:
            raise ImportError("watchdog library is required for real-time monitoring. "
                            "Install it with: pip install watchdog")

        super().__init__()
        self.steward = shop_steward
        self.watch_dir = Path(watch_dir).resolve()
        self.debounce_seconds = debounce_seconds
        self.pending_files = {}  # Track files waiting to be processed

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip log files and hidden files
        if file_path.name.startswith('.') or file_path.name == self.steward.LOG_FILENAME:
            return

        self.steward.logger.info(f"Detected new file: {file_path.name}")

        # Add to pending with timestamp
        self.pending_files[file_path] = time.time()

    def on_modified(self, event):
        """Handle file modification events (file still being written)."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Update timestamp for pending files
        if file_path in self.pending_files:
            self.pending_files[file_path] = time.time()

    def process_pending_files(self):
        """Process files that have finished uploading/copying."""
        current_time = time.time()
        files_to_process = []

        # Find files that haven't been modified for debounce_seconds
        for file_path, timestamp in list(self.pending_files.items()):
            if current_time - timestamp >= self.debounce_seconds:
                files_to_process.append(file_path)
                del self.pending_files[file_path]

        # Process each file
        for file_path in files_to_process:
            if file_path.exists() and file_path.is_file():
                self.steward.logger.info(f"Processing: {file_path.name}")

                # Categorize the file
                category = self.steward.categorize_file(file_path)

                if category:
                    self.steward.move_file(file_path, category)
                else:
                    # Move to HOLDING
                    self.steward.logger.warning(f"Cannot categorize: {file_path.name}")
                    self.steward.move_file(file_path, 'HOLDING')

    def start_monitoring(self):
        """Start monitoring the watch directory."""
        if not self.watch_dir.exists():
            self.steward.logger.error(f"Watch directory does not exist: {self.watch_dir}")
            return

        self.steward.logger.info(f"Starting real-time monitoring of: {self.watch_dir}")
        self.steward.logger.info(f"Press Ctrl+C to stop monitoring")

        observer = Observer()
        observer.schedule(self, str(self.watch_dir), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
                self.process_pending_files()
        except KeyboardInterrupt:
            self.steward.logger.info("Stopping monitor...")
            observer.stop()

        observer.join()
        self.steward.logger.info("Monitor stopped")


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

  # Monitor directory for new files in real-time
  python shop_steward.py --monitor /path/to/watch

  # Enforce naming conventions and report violations
  python shop_steward.py --organize /path/to/files --enforce-naming

  # Automatically rename files to match conventions
  python shop_steward.py --organize /path/to/files --auto-rename
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

    parser.add_argument(
        '--hierarchical',
        action='store_true',
        help='Use hierarchical structure: Customer/PartNumber-Rev/folders'
    )

    parser.add_argument(
        '--customer',
        type=str,
        metavar='NAME',
        help='Specify customer name for hierarchical organization'
    )

    parser.add_argument(
        '--monitor',
        type=str,
        metavar='DIR',
        help='Monitor directory for new files and organize them in real-time (requires watchdog library)'
    )

    parser.add_argument(
        '--enforce-naming',
        action='store_true',
        help='Enforce naming conventions (files must follow PARTNUMBER_REV-X_description.ext format)'
    )

    parser.add_argument(
        '--auto-rename',
        action='store_true',
        help='Automatically rename files to match naming conventions (implies --enforce-naming)'
    )

    args = parser.parse_args()

    # Auto-rename implies enforce-naming
    if args.auto_rename:
        args.enforce_naming = True

    # Create Shop Steward instance
    steward = ShopSteward(
        root_dir=args.root,
        dry_run=args.dry_run,
        hierarchical=args.hierarchical,
        enforce_naming=args.enforce_naming,
        auto_rename=args.auto_rename
    )

    # If customer is specified, store it for use during organization
    if args.customer:
        steward.forced_customer = args.customer
    
    # Execute requested action
    if args.init:
        steward.create_folder_structure()
        
    if args.organize:
        steward.create_folder_structure()  # Ensure structure exists
        steward.organize_files(source_dir=args.organize, recursive=not args.no_recursive)
        
    if args.archive:
        steward.archive_folder(args.archive)

    if args.monitor:
        if not WATCHDOG_AVAILABLE:
            print("ERROR: Real-time monitoring requires the watchdog library.")
            print("Install it with: pip install watchdog")
            return 1

        # Ensure folder structure exists
        steward.create_folder_structure()

        # Start monitoring
        watcher = ShopStewardWatcher(steward, args.monitor)
        watcher.start_monitoring()

    if not (args.init or args.organize or args.archive or args.monitor):
        parser.print_help()


if __name__ == '__main__':
    main()
