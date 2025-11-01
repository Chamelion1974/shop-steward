# Shop Steward - Quick Start Guide

This guide will help you get started with Shop Steward in just a few minutes.

## Quick Start

### 1. Set Up Your Shop Directory

```bash
# Navigate to your shop directory (or create a new one)
mkdir /path/to/my-shop
cd /path/to/my-shop

# Initialize the folder structure
python3 /path/to/shop_steward.py --init
```

You should now see these folders:
```
my-shop/
├── CAD/
├── CAM/
├── NC Files/
│   ├── PROVEN/
│   └── UNPROVEN/
├── MPI/
├── ARCHIVE/
└── HOLDING/
```

### 2. Organize Your Files

Let's say you have a messy directory with mixed files:

```bash
# Your messy files are in a folder called "incoming"
/path/to/incoming/
├── part001.step
├── program.nc
├── setup_sheet.pdf
├── toolpath.cam
├── drawing.dwg
└── unknown_file.dat
```

Organize them with:

```bash
cd /path/to/my-shop
python3 /path/to/shop_steward.py --organize /path/to/incoming
```

**Result:**
- `part001.step` → `CAD/part001.step`
- `drawing.dwg` → `CAD/drawing.dwg`
- `toolpath.cam` → `CAM/toolpath.cam`
- `program.nc` → `NC Files/UNPROVEN/program.nc`
- `setup_sheet.pdf` → `MPI/setup_sheet.pdf`
- `unknown_file.dat` → `HOLDING/unknown_file.dat` (for review)

### 3. Preview Before Organizing (Dry Run)

Not sure what will happen? Run a dry-run first:

```bash
python3 /path/to/shop_steward.py --organize /path/to/incoming --dry-run
```

This shows you what *would* happen without making any changes.

### 4. Move Proven NC Files

Once you've tested an NC file and verified it works:

```bash
# Manually move it from UNPROVEN to PROVEN
mv "NC Files/UNPROVEN/program.nc" "NC Files/PROVEN/program.nc"
```

### 5. Archive Old Projects

Instead of deleting old projects, archive them:

```bash
python3 /path/to/shop_steward.py --archive /path/to/my-shop/old-project-2024
```

The project gets moved to `ARCHIVE/old-project-2024_TIMESTAMP/`

## Common Workflows

### Daily Incoming Files

```bash
# Every day, organize new files from your incoming directory
cd /path/to/my-shop
python3 /path/to/shop_steward.py --organize /path/to/incoming
```

### Review Uncategorized Files

```bash
# Check what files couldn't be categorized
ls HOLDING/

# Move them manually to the right place after reviewing
mv HOLDING/special_file.xyz CAD/special_file.xyz
```

### Clean Up After a Project

```bash
# Archive the project folder when done
python3 /path/to/shop_steward.py --archive completed-project-folder
```

## Tips

1. **Run dry-run first**: Always use `--dry-run` when organizing new file types
2. **Check logs**: Review `shop_steward.log` for a complete audit trail
3. **Verify UNPROVEN**: Always test NC files before moving to PROVEN
4. **Review HOLDING**: Check HOLDING folder regularly for miscategorized files
5. **Archive, don't delete**: Use the archive feature instead of deleting

## File Types Reference

| Folder | Extensions |
|--------|-----------|
| CAD | .step, .stp, .igs, .iges, .stl, .dwg, .dxf, .catpart, .prt, .sldprt, .sldasm |
| CAM | .mcam, .cam, .camproj, .ncl, .ncp, .operations |
| NC Files/UNPROVEN | .nc, .cnc, .tap, .mpf, .ngc, .eia, .min, .din |
| MPI | .pdf, .doc, .docx, .txt, .xlsx, .xls |
| HOLDING | Any unrecognized extension |

## Need Help?

- Run `python3 shop_steward.py --help` for all options
- Check the main README.md for detailed documentation
- Review the log file at `shop_steward.log` for operation details
