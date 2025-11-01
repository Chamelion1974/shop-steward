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

# Custom patterns for extracting part numbers from filenames
# Add your company's specific part number formats here
CUSTOM_PART_NUMBER_PATTERNS = [
    r'([A-Z0-9]{2,}-[A-Z0-9]{2,})',  # Format: ABC-123, XYZ-456A
    r'([A-Z]{2,}\d{3,})',             # Format: ABC123, XYZ456
    r'(\d{4,}-\d{2,})',               # Format: 1234-56, 12345-678
    r'([A-Z]\d{4,})',                 # Format: A1234, X12345
]

# Custom patterns for extracting revision levels
# Add your company's specific revision formats here
CUSTOM_REVISION_PATTERNS = [
    r'(?:REV|Rev|rev)[-_]?([A-Z0-9]+)',  # REV-A, Rev_B, revC
    r'(?:R|r)(\d+)',                       # R1, r2
    r'(?:V|v)(\d+)',                       # V1, v2
    r'[-_]([A-Z])(?:[-_\.]|$)',           # -A, _B, .C
]
