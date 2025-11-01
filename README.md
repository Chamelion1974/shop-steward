# Shop Steward

**Server folder housekeeping and maintenance for CNC Programming**

Shop Steward is a file organization system for machine shops that automatically categorizes and organizes CNC programming files into a standardized folder structure. It acts as a "housekeeper" or "hall monitor" that captures errant files and places them in appropriate folders based on their file type and purpose.

## Features

### File Organization
- 🗂️ **Automated File Organization**: Categorizes files based on extensions
- 📁 **Standardized Folder Structure**: Creates and maintains consistent folder hierarchy
- 🏗️ **Hierarchical Organization**: Supports Customer → Part# + Revision structure
- 🔍 **Smart Part Number Detection**: Automatically extracts part numbers and revisions from filenames
- 📝 **Naming Convention Enforcement**: Validates and enforces standardized naming conventions
- ✏️ **Auto-Rename**: Automatically renames files to match conventions
- 👀 **Real-Time Monitoring**: "Hall monitor" mode watches directories and organizes files as they arrive
- 🔒 **Safe Operations**: Never deletes files - everything goes to ARCHIVE or HOLDING
- 🏷️ **Smart Categorization**: Recognizes common CAD, CAM, NC, and MPI file types
- 📋 **Comprehensive Logging**: Tracks all operations for audit purposes
- 🔍 **Dry Run Mode**: Preview changes before applying them

### Workflow Management
- 📊 **Job Tracking**: Track CNC programming jobs from intake to production
- 👥 **Programmer Assignment**: Assign jobs to programmers with workload balancing
- ⏱️ **Time Tracking**: Measure programming time and cycle time automatically
- 📈 **Workload Metrics**: Monitor programmer capacity and productivity
- 🎯 **Priority Management**: Set job priorities for optimal scheduling
- 📝 **Status Workflow**: INTAKE → QUEUED → IN_PROGRESS → REVIEW → READY
- 📊 **Reporting**: Generate detailed status reports and analytics

## Folder Structure

Shop Steward supports two organization modes:

### Flat Structure (Default)

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

### Hierarchical Structure (--hierarchical)

Organizes files by Customer → Part Number + Revision → Category:

```
ProgrammingServer/
├── CustomerA/
│   ├── ABC123-REV-A/
│   │   ├── CAD/
│   │   ├── CAM/
│   │   ├── NC Files/
│   │   │   ├── PROVEN/
│   │   │   └── UNPROVEN/
│   │   ├── MPI/
│   │   └── ARCHIVE/
│   └── XYZ789-REV-B/
│       ├── CAD/
│       └── ...
├── CustomerB/
│   └── PART456-REV-C/
│       └── ...
└── HOLDING/               # Files that cannot be categorized
```

**Benefits of Hierarchical Mode:**
- Maintains customer separation for IP protection
- Groups all files for a specific part and revision together
- Supports document control and revision management (ISO13485, AS9100)
- Scales well for shops with multiple customers and hundreds of parts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Chamelion1974/shop-steward.git
cd shop-steward
```

2. **Basic Installation** - The script uses only Python 3.6+ standard library for basic operations.

3. **Optional: Real-time Monitoring** - For the "hall monitor" real-time monitoring feature:
```bash
pip install -r requirements.txt
# or
pip install watchdog
```

4. Make the script executable (optional):
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

### Hierarchical Organization

Use hierarchical mode to organize files by customer and part number:

```bash
# Organize files with hierarchical structure
python shop_steward.py --hierarchical --organize /path/to/files

# Specify customer name explicitly
python shop_steward.py --hierarchical --customer "Acme Corp" --organize /path/to/files

# Preview hierarchical organization
python shop_steward.py --hierarchical --organize /path/to/files --dry-run
```

**How it works:**
- Extracts part numbers from filenames (e.g., `ABC-123`, `XYZ456`)
- Extracts revision levels (e.g., `REV-A`, `R1`, `V2`)
- Detects customer from existing folder path or uses `--customer` flag
- Creates structure: `Customer/PartNumber-REV-X/{CAD,CAM,NC Files,MPI,ARCHIVE}`
- Files without part numbers go to `HOLDING` for manual review

### Real-Time Monitoring ("Hall Monitor" Mode)

Shop Steward can watch a directory and automatically organize new files as they arrive:

```bash
# Monitor a directory for new files
python shop_steward.py --root /data/shop --monitor /data/incoming

# Monitor with hierarchical organization
python shop_steward.py --root /data/shop --hierarchical --customer "AcmeCorp" --monitor /data/incoming

# The monitor runs continuously until you press Ctrl+C
```

**How it works:**
- Watches the specified directory for new files (recursively)
- Waits 2 seconds after file creation/modification (debounce) to ensure upload is complete
- Automatically categorizes and moves files to appropriate folders
- Logs all operations for audit trail
- Press `Ctrl+C` to stop monitoring

**Use cases:**
- Drop folder for incoming files from NPI coordinator
- Network share where programmers receive new jobs
- Automated cleanup of messy directories
- Integration with file transfer systems

### Naming Convention Enforcement

Shop Steward can enforce standardized naming conventions to ensure consistency and traceability:

**Expected Format:** `PARTNUMBER_REV-X_description.ext`

**Examples:**
- `ABC-123_REV-A_housing.step` ✅
- `XYZ-789_REV-B_toolpath.cam` ✅
- `PART456_REV-1_drawing.dwg` ✅

```bash
# Check files against naming conventions and report violations
python shop_steward.py --organize /path/to/files --enforce-naming

# Automatically rename files to match conventions
python shop_steward.py --organize /path/to/files --auto-rename

# Preview what would be renamed (dry-run + auto-rename)
python shop_steward.py --organize /path/to/files --auto-rename --dry-run
```

**How it works:**
- Validates filenames against the convention pattern
- Extracts part numbers and revisions from existing filenames
- Suggests properly formatted names for non-compliant files
- Can automatically rename files (with `--auto-rename`)
- Generates violation reports with suggestions
- Non-compliant files go to HOLDING if enforcement is strict

**Benefits:**
- Ensures consistent naming across all files
- Makes part numbers and revisions immediately visible
- Supports document control requirements (ISO, AS9100)
- Reduces confusion and misidentification
- Facilitates automated processing and searches

### Command Line Options

```
--root DIR          Root directory for the shop steward system (default: current directory)
--init              Initialize the folder structure
--organize DIR      Organize files in the specified directory
--archive DIR       Move a folder to ARCHIVE
--monitor DIR       Monitor directory for new files and organize them in real-time
--dry-run           Show what would be done without making changes
--no-recursive      Do not process subdirectories recursively
--hierarchical      Use hierarchical Customer/Part#-Rev/folders structure
--customer NAME     Specify customer name for hierarchical organization
--enforce-naming    Enforce naming conventions (PARTNUMBER_REV-X_description.ext)
--auto-rename       Automatically rename files to match naming conventions
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

### Example 5: Hierarchical organization for customer projects

```bash
# Organize files with hierarchical structure
# Files named like "ABC-123_REV-A_drawing.step" will be organized to:
# /data/shop/AcmeCorp/ABC-123-REV-A/CAD/ABC-123_REV-A_drawing.step
python shop_steward.py --root /data/shop --hierarchical --customer "AcmeCorp" --organize /data/incoming

# Let Shop Steward detect customer from existing folder structure
python shop_steward.py --root /data/shop --hierarchical --organize /data/AcmeCorp/incoming
```

### Example 6: Real-time monitoring (Hall Monitor mode)

```bash
# Set up a drop folder that automatically organizes files
python shop_steward.py --root /data/shop --monitor /data/dropbox

# Monitor with hierarchical organization
python shop_steward.py --root /data/shop --hierarchical --customer "AcmeCorp" --monitor /data/dropbox

# The script will run continuously and organize files as they arrive
# Press Ctrl+C to stop
```

### Example 7: Naming convention enforcement

```bash
# Check files and report naming violations
python shop_steward.py --root /data/shop --organize /data/incoming --enforce-naming

# Automatically rename files to match conventions
python shop_steward.py --root /data/shop --organize /data/incoming --auto-rename

# Combine with hierarchical organization
python shop_steward.py --root /data/shop --hierarchical --customer "AcmeCorp" \
  --organize /data/incoming --auto-rename

# Preview renaming without making changes
python shop_steward.py --organize /data/incoming --auto-rename --dry-run
```

## Configuration

For advanced customization, copy `config.example.py` to `config.py` and modify the settings:

- Custom folder names
- Custom file extension mappings
- Custom part number patterns (for your company's naming conventions)
- Custom revision patterns
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

## Workflow Management

Shop Steward includes a complete workflow management system for tracking CNC programming jobs. See [WORKFLOW.md](WORKFLOW.md) for detailed documentation.

### Quick Workflow Example

```bash
# Add programmers
python workflow_cli.py add-programmer "Alice"
python workflow_cli.py add-programmer "Bob"

# Create a job
python workflow_cli.py create "AcmeCorp" "ABC-123" "A" --priority 3

# Auto-assign to available programmer
python workflow_cli.py assign AcmeCorp_ABC-123_A_1234567890 --auto

# Start programming
python workflow_cli.py start AcmeCorp_ABC-123_A_1234567890

# Complete programming
python workflow_cli.py complete AcmeCorp_ABC-123_A_1234567890

# Approve for production
python workflow_cli.py approve AcmeCorp_ABC-123_A_1234567890

# Check workload
python workflow_cli.py workload

# Generate status report
python workflow_cli.py report
```

### Workflow Integration

The workflow system integrates with file organization:

1. **Files arrive** → Organized into Customer/Part#-Rev structure
2. **Job created** → Tracked through workflow states
3. **Programmer assigned** → Based on workload metrics
4. **Programming starts** → Timer tracks actual time
5. **Programming complete** → Job enters review purgatory
6. **Approved** → Files in final form, programs proven

For complete workflow documentation, see [WORKFLOW.md](WORKFLOW.md).

## Best Practices

1. **Run dry-run first**: Always use `--dry-run` to preview changes
2. **Check HOLDING regularly**: Review files that couldn't be categorized
3. **Verify UNPROVEN files**: Test NC files before moving them to PROVEN
4. **Keep logs**: Maintain the log file for audit trails
5. **Archive old projects**: Use `--archive` instead of deleting old data
6. **Use workflow tracking**: Create jobs for all programming work to track metrics
7. **Balance workload**: Use auto-assignment to distribute work fairly

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
