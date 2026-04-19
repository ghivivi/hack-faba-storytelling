# 🚫 Faba Advertisement Remover

Safely remove advertisement files from Faba device with automatic renumbering.

## 🎯 What It Does

Many Faba figures include a short advertisement as the first track (CP01.MKI, ~448KB). This script:
- Identifies advertisements by file size (440-470KB)
- Shows preview before proceeding
- Backs up or deletes ads safely
- Optionally renumbers remaining tracks (CP02→CP01, CP03→CP02, etc.)

## 🔧 Requirements

**For renumbering only:**
```bash
pip install mutagen
```

## 🚀 Usage

### 1. Dry-Run Mode (Safe - Recommended First)

Shows what would be removed **without modifying anything**:

```bash
./remove_ads.py /mnt/faba/MKI01 --dry-run
```

### 2. Backup Mode (Recommended)

Moves advertisements to backup folder instead of deleting:

```bash
./remove_ads.py /mnt/faba/MKI01 --backup
```

**Result:**
- Creates `faba_ads_backup_YYYYMMDD_HHMMSS/` folder
- Moves all ad CP01 files to backup
- Keeps folder structure (K0010/, K0011/, etc.)
- Can restore if needed

### 3. Delete Mode (Caution!)

Permanently deletes advertisements:

```bash
./remove_ads.py /mnt/faba/MKI01 --delete
```

⚠️ **WARNING:** This operation is irreversible!
- You'll be asked to type "DELETE" to confirm
- Files are permanently deleted

### 4. Renumber Option (Automatic Renumbering)

After removing CP01, automatically renumber remaining files:

```bash
./remove_ads.py /mnt/faba/MKI01 --backup --renumber
```

**What --renumber does:**
- Renumbers remaining files: CP02→CP01, CP03→CP02, etc.
- Automatically updates internal ID3 tags (e.g., "K0015CP02" becomes "K0015CP01")
- Maintains Faba device compatibility
- Eliminates gaps in track numbering

**Example:**

Before removal:
```
K0010/
  ├── CP01.MKI (448KB - advertisement)
  ├── CP02.MKI (1.2MB - content)
  └── CP03.MKI (850KB - content)
```

After `--backup --renumber`:
```
K0010/
  ├── CP01.MKI (1.2MB - was CP02, tag updated to "K0010CP01")
  └── CP02.MKI (850KB - was CP03, tag updated to "K0010CP02")
```

## 📝 Examples

### Example 1: First Use (Exploratory)

```bash
# 1. Analyze what's there (no changes)
./remove_ads.py /mnt/faba/MKI01 --dry-run

# 2. See what would happen with renumbering
./remove_ads.py /mnt/faba/MKI01 --dry-run --renumber

# 3. If satisfied, backup with renumbering
./remove_ads.py /mnt/faba/MKI01 --backup --renumber
```

### Example 2: External Faba Disk

```bash
# Assuming Faba is mounted at /media/usb/FABA
./remove_ads.py /media/usb/FABA/MKI01 --backup --renumber
```

## ❓ FAQ

### Q: Is this script safe?
**A:** Yes! The script is designed to be conservative and protects real content. Always use `--dry-run` first to see what would be done.

### Q: What if I delete something by mistake?
**A:** Always use `--backup` mode instead of `--delete`. This way files are moved, not deleted, and you can restore them.

### Q: How does it identify advertisements?
**A:** The script automatically identifies CP01 files with size ~448KB (440-470KB). Real content usually has very different sizes.

### Q: Should I use --renumber?
**A:** Not mandatory, but **recommended**:
- **Without --renumber**: Faba will start playing from CP02 (should work)
- **With --renumber**: Clean playback from CP01, no gaps in numbering

### Q: How does renumbering work?
**A:** The script:
1. Decrypts each .MKI file to .mp3
2. Updates ID3 tag with new number (e.g., "K0015CP02" → "K0015CP01")
3. Re-encrypts file to .MKI
4. Renames file (e.g., CP02.MKI → CP01.MKI)

## 🛡️ Safety

- ✅ **Preview before action**: Shows what will be removed
- ✅ **Confirmation required**: Always asks before proceeding
- ✅ **Backup mode**: Safe alternative to deletion
- ✅ **Detailed logging**: Creates log file of all operations
- ✅ **Size-based identification**: Protects content with different sizes

## 🔗 Related Commands

- `backup_faba.py` - Create complete backup before changes
- `add_tracks.py` - Add new tracks to figures

---

📖 **[Versione Italiana](REMOVE_ADS.md)** | 🌍 **English Version** (current)
