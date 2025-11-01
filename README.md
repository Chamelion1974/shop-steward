# Shop Steward

**Server folder housekeeping and maintenance for CNC Programming**

Shop Steward is a file organization system for machine shops that automatically categorizes and organizes CNC programming files into a standardized folder structure. It acts as a "housekeeper" or "hall monitor" that captures errant files and places them in appropriate folders based on their file type and purpose.

## Features

- 🗂️ **Automated File Organization**: Categorizes files based on extensions
- 📁 **Standardized Folder Structure**: Creates and maintains consistent folder hierarchy
- 🔒 **Safe Operations**: Never deletes files - everything goes to ARCHIVE or HOLDING
- 🏷️ **Smart Categorization**: Recognizes common CAD, CAM, NC, and MPI file types
- 📋 **Comprehensive Logging**: Tracks all operations for audit purposes
- 🔍 **Dry Run Mode**: Preview changes before applying them

## Folder Structure

Shop Steward creates and manages the following folder structure:

```
.
├── CAD/                    # CAD design files (.step, .stl, .dwg, etc.)
├── CAM/                    # CAM programming files (.mcam, .cam, etc.)
├── NC Files/               # CNC machine code files
│   ├── PROVEN/            # Tested and verified NC files
│   └── UNPROVEN/          # New or untested NC files (.nc, .cnc, .tap, etc.)
├── MPI/                    # Manufacturing Process Instructions (.pdf, .doc, etc.)
├── ARCHIVE/               # Extra/unused data (nothing is deleted!)
└── HOLDING/               # Files that cannot be categorized (for manual review)
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Chamelion1974/shop-steward.git
cd shop-steward
```

2. The script uses only Python 3.6+ standard library, so no additional dependencies are needed.

3. Make the script executable (optional):
```bash
chmod +x shop_steward.py
```

## Usage

### Initialize Folder Structure

Create the standard folder structure in the current directory:

```bash
python shop_steward.py --init
```

Or in a specific directory:

```bash
python shop_steward.py --root /path/to/shop --init
```

### Organize Files

Organize files in a specific directory:

```bash
python shop_steward.py --organize /path/to/messy/files
```

Organize files in the current directory:

```bash
python shop_steward.py --root . --organize .
```

### Dry Run Mode

Preview what would happen without making any changes:

```bash
python shop_steward.py --organize /path/to/files --dry-run
```

### Archive a Folder

Move an entire folder to the ARCHIVE:

```bash
python shop_steward.py --archive /path/to/old/project
```

### Command Line Options

```
--root DIR          Root directory for the shop steward system (default: current directory)
--init              Initialize the folder structure
--organize DIR      Organize files in the specified directory
--archive DIR       Move a folder to ARCHIVE
--dry-run           Show what would be done without making changes
--no-recursive      Do not process subdirectories recursively
```

## File Type Recognition

Shop Steward automatically recognizes the following file types:

### CAD Files
`.step`, `.stp`, `.igs`, `.iges`, `.stl`, `.dwg`, `.dxf`, `.catpart`, `.catproduct`, `.prt`, `.sldprt`, `.sldasm`

### CAM Files
`.mcam`, `.cam`, `.camproj`, `.ncl`, `.ncp`, `.operations`

### NC Files (CNC Machine Code)
`.nc`, `.cnc`, `.tap`, `.mpf`, `.ngc`, `.eia`, `.min`, `.din`

**Note**: NC files are initially placed in the `UNPROVEN` subfolder. Move them to `PROVEN` manually once verified.

### MPI Files (Manufacturing Process Instructions)
`.pdf`, `.doc`, `.docx`, `.txt`, `.xlsx`, `.xls`

Files that don't match any category are moved to the `HOLDING` folder for manual review.

## Examples

### Example 1: Setting up a new shop directory

```bash
# Create and initialize a new shop directory
mkdir /data/shop
python shop_steward.py --root /data/shop --init
```

### Example 2: Organizing incoming files

```bash
# Organize files from an incoming directory
python shop_steward.py --root /data/shop --organize /data/incoming
```

### Example 3: Safe testing with dry-run

```bash
# See what would happen before making changes
python shop_steward.py --organize /data/incoming --dry-run
```

### Example 4: Archiving old projects

```bash
# Archive a completed project
python shop_steward.py --root /data/shop --archive /data/shop/old-project-2024
```

## Configuration

For advanced customization, copy `config.example.py` to `config.py` and modify the settings:

- Custom folder names
- Custom file extension mappings
- Logging levels
- File patterns to ignore

## Logging

All operations are logged to `shop_steward.log` in the root directory. The log includes:
- Timestamp of each operation
- Files moved and their destinations
- Errors and warnings
- Summary statistics

## Safety Features

- **No Deletions**: Files are never deleted, only moved
- **Duplicate Handling**: If a file with the same name exists, a timestamp is added
- **ARCHIVE Folder**: Old or unused data can be moved to ARCHIVE instead of being deleted
- **HOLDING Folder**: Unrecognizable files are held for manual review
- **Dry Run**: Test operations before executing them

## Best Practices

1. **Run dry-run first**: Always use `--dry-run` to preview changes
2. **Check HOLDING regularly**: Review files that couldn't be categorized
3. **Verify UNPROVEN files**: Test NC files before moving them to PROVEN
4. **Keep logs**: Maintain the log file for audit trails
5. **Archive old projects**: Use `--archive` instead of deleting old data

## Troubleshooting

### Files not being categorized
- Check if the file extension is in the recognized list
- Files with unrecognized extensions will go to HOLDING

### Duplicate filename warnings
- Shop Steward automatically adds timestamps to prevent overwrites
- Check the log for the new filename

### Permission errors
- Ensure you have write permissions to the target directory
- Run with appropriate user privileges

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available for use in machine shop environments.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
