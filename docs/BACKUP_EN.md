# 💾 Faba Backup Tool

Complete backup system for Faba disk with maximum compression. **Essential** before any disk modification operations.

## 🎯 Why Backup?

Before operations like:
- ❌ **Advertisement removal** (`remove_ads.py`)
- ➕ **Adding tracks** (`add_tracks.py`)
- 🔄 **File renumbering**
- 🔧 **Manual modifications**

**A complete backup protects you** from:
- Errors during operations
- Corrupted files
- Accidental data loss
- Hardware disk problems

## 🚀 Quick Start

### 1. Basic Backup (Maximum Compression)

```bash
./backup_faba.py /mnt/faba/MKI01
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║  Faba Backup Tool - Creating backup...                 ║
╚════════════════════════════════════════════════════════╝

📂 Scanning Faba directory...

Statistics:
  Figures found: 15
  Total files: 120
  Total size: 150.45 MB

📦 Creating backup: faba_backup_20260210_143022.zip
   Compression: Maximum (may take time)

  📁 K0010 (8 tracks)... ✓
  📁 K0011 (8 tracks)... ✓
  ...

✓ Backup created successfully!

Details:
  File: ./backups/faba_backup_20260210_143022.zip
  Original size: 150.45 MB
  Backup size: 48.23 MB
  Compression: 67.9%

🔐 Calculating checksum...
  SHA256: a3f5c8e9...

📝 Metadata saved to:
  ./backups/faba_backup_20260210_143022_metadata.json

🔍 Verifying backup integrity...
✓ Backup verified successfully
  Figures in backup: 15
  Backup date: 2026-02-10T14:30:22

═══════════════════════════════════════════════════════════
✓ Backup completed and verified!
═══════════════════════════════════════════════════════════
```

### 2. Fast Backup (Standard Compression)

```bash
./backup_faba.py /mnt/faba/MKI01 --fast
```

**When to use:**
- Quick backups during work sessions
- Frequent testing
- Slow SSD write speeds

**Differences:**
- 🚀 3-4x faster
- 💾 File ~20-30% larger
- ✅ Still safe

### 3. Backup + Google Drive Upload

```bash
./backup_faba.py /mnt/faba/MKI01 --upload-to-drive
```

**Requirements:**
- rclone configured (`./sync_from_drive.py --setup`)
- Internet connection

**Result:**
- Local backup created
- Automatic upload to `gdrive:Faba/backups/`
- Double security (local + cloud)

### 4. Backup to Specific Folder

```bash
./backup_faba.py /mnt/faba/MKI01 --output ~/my-backups
```

**Useful for:**
- Saving to external drive
- Organizing backups by date
- NAS archival

## 📋 Advanced Commands

### List Available Backups

```bash
./backup_faba.py --list
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║  Available Backups                                     ║
╚════════════════════════════════════════════════════════╝

📦 faba_backup_20260210_143022.zip
   Date: 2026-02-10 14:30:22
   Size: 48.23 MB
   Figures: 15
   Files: 120
   Compression: 67.9%
   SHA256: a3f5c8e9...

📦 faba_backup_20260209_093015.zip
   Date: 2026-02-09 09:30:15
   Size: 47.89 MB
   Figures: 14
   Files: 112
   Compression: 68.2%
   SHA256: b2e4d7a1...
```

### Verify Backup Integrity

```bash
./backup_faba.py --verify backups/faba_backup_20260210_143022.zip
```

## 🔄 Restore from Backup

### Complete Restore

```bash
# Extract the backup
unzip backups/faba_backup_20260210_143022.zip -d /mnt/faba/MKI01/

# Verify everything was extracted
ls -la /mnt/faba/MKI01/
```

### Restore Single Figure

```bash
# Extract only a specific figure
unzip backups/faba_backup_20260210_143022.zip "K0015/*" -d /mnt/faba/MKI01/
```

### Restore Specific File

```bash
# Extract a single file
unzip backups/faba_backup_20260210_143022.zip "K0015/CP03.MKI" -d /mnt/faba/MKI01/
```

## 📝 Recommended Workflow

### Before Important Changes

```bash
# 1. Connect Faba
sudo mount /dev/sdb1 /mnt/faba

# 2. Create backup
./backup_faba.py /mnt/faba/MKI01

# 3. Make changes
./remove_ads.py /mnt/faba/MKI01 --backup --renumber

# 4. If everything OK, unmount
sudo umount /mnt/faba

# 5. (Optional) Archive old backups after a few days
```

## 💡 Best Practices

### 1. **3-2-1 Strategy**
- **3** copies of data (original + 2 backups)
- **2** different media types (local + cloud)
- **1** off-site copy (Google Drive, remote NAS)

Example:
```bash
# Local backup
./backup_faba.py /mnt/faba/MKI01

# External drive backup
./backup_faba.py /mnt/faba/MKI01 --output /media/external/backups

# Cloud backup
./backup_faba.py /mnt/faba/MKI01 --upload-to-drive
```

### 2. **Backup Frequency**
- ✅ **Before every modification**: Always
- ✅ **After important additions**: After adding new figures
- ✅ **Periodically**: Every 1-2 months even without changes

### 3. **Backup Retention**
- **Recent backups** (last 3): Always keep
- **Weekly backups**: Keep last month
- **Monthly backups**: Keep last year
- **Low on space?** Upload to cloud and remove old local ones

## ❓ FAQ

### Q: How much space do backups take?
**A:** Depends on content:
- **Maximum compression**: ~30-40% of original size
- **Fast compression**: ~50-60% of original size
- **Example**: 150MB original → 45-50MB compressed (max) or 75-90MB (fast)

### Q: How long does a backup take?
**A:** Depends on:
- **Maximum compression**: 2-5 minutes for 150MB
- **Fast compression**: 30-90 seconds for 150MB
- **Drive upload**: +2-10 minutes (depends on connection)

### Q: Can I interrupt a backup?
**A:** Yes, press `Ctrl+C`. Partial file will be created but won't be valid. Use `--verify` to check.

### Q: Are backups compatible with Windows/Mac?
**A:** Yes, they're standard ZIP files. Extract with any tool:
- **Windows**: Right-click → Extract
- **Mac**: Double-click
- **Linux**: `unzip backup.zip`

### Q: Does checksum guarantee integrity?
**A:** Yes, SHA256 is secure. If checksum matches, backup is identical to original.

### Q: Can I automate backups?
**A:** Yes, see "Periodic Automated Backups" section. You can use:
- Cron jobs
- udev rules (Linux)
- Automator (Mac)
- Task Scheduler (Windows)

### Q: What if backup fails?
**A:**
1. Check disk space: `df -h`
2. Verify permissions: `ls -la /mnt/faba`
3. Try fast compression: `--fast`
4. Check if Faba disk is readable

## 🔐 Security & Privacy

### Backup Encryption (Optional)

If you want to encrypt backups before uploading to cloud:

```bash
# 1. Create normal backup
./backup_faba.py /mnt/faba/MKI01

# 2. Encrypt with GPG
gpg --symmetric --cipher-algo AES256 backups/faba_backup_20260210_143022.zip

# 3. Upload .gpg file to Drive
rclone copy backups/faba_backup_20260210_143022.zip.gpg gdrive:Faba/backups/

# 4. To decrypt:
gpg --decrypt backups/faba_backup_20260210_143022.zip.gpg > restored_backup.zip
```

## 📊 Typical Results

| Original Size | Max Compression | Fast Compression | Time (Max) | Time (Fast) |
|--------------|----------------|------------------|------------|-------------|
| 50 MB        | ~17 MB (66%)   | ~28 MB (44%)     | 1 min      | 20 sec      |
| 150 MB       | ~48 MB (68%)   | ~85 MB (43%)     | 3 min      | 45 sec      |
| 500 MB       | ~160 MB (68%)  | ~285 MB (43%)    | 10 min     | 2.5 min     |

## 🔗 Related Commands

- `add_tracks.py` - Manually add tracks to Faba
- `remove_ads.py` - Remove advertisements
- `sync_from_drive.py` - Sync from Google Drive
- `rclone config` - Manage remote configurations

---

📖 **[Versione Italiana](BACKUP.md)** | 🌍 **English Version** (current)
