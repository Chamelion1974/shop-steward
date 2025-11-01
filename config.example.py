"""
Shop Steward Configuration Example

This configuration file is OPTIONAL. The script works with default settings.

To use custom settings:
1. Copy this file to config.py
2. Customize the values below
3. The script will automatically load config.py if it exists

Note: All settings have sensible defaults in shop_steward.py
"""

# Custom folder names (if you want to use different names)
CUSTOM_FOLDERS = {
    'CAD': 'CAD',
    'CAM': 'CAM',
    'NC_FILES': 'NC Files',
    'NC_PROVEN': 'NC Files/PROVEN',
    'NC_UNPROVEN': 'NC Files/UNPROVEN',
    'MPI': 'MPI',
    'ARCHIVE': 'ARCHIVE',
    'HOLDING': 'HOLDING'
}

# Custom file extension mappings
CUSTOM_FILE_CATEGORIES = {
    'CAD': ['.step', '.stp', '.igs', '.iges', '.stl', '.dwg', '.dxf', '.catpart', '.catproduct', '.prt', '.sldprt', '.sldasm'],
    'CAM': ['.mcam', '.cam', '.camproj', '.ncl', '.ncp', '.operations'],
    'NC_UNPROVEN': ['.nc', '.cnc', '.tap', '.mpf', '.ngc', '.eia', '.min', '.din'],
    'MPI': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls'],
}

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = 'INFO'

# Whether to preserve directory structure when moving files
PRESERVE_STRUCTURE = False

# File patterns to ignore (regex patterns)
IGNORE_PATTERNS = [
    r'^\..*',  # Hidden files
    r'.*\.log$',  # Log files
    r'shop_steward\.py$',  # The script itself
]
