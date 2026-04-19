# 📦 Faba Google Drive Sync

Script to sync MP3 files from Google Drive to Faba device. Ideal for receiving audio recordings from others and automatically adding them to Faba.

## 🎯 Use Case

**Typical scenario:**
1. Grandparents/relatives/friends record stories on smartphone
2. They upload to shared Google Drive folder
3. You connect Faba to PC
4. Run script to download and process new files automatically
5. Files are added to Faba with auto-incremental ID
6. Processed files are archived on Drive

## 🔧 Requirements

### 1. Install rclone

**Linux/macOS:**
```bash
curl https://rclone.org/install.sh | sudo bash
```

**Windows:**
- Download from: https://rclone.org/downloads/
- Extract and add to PATH

### 2. Install Python dependencies

```bash
pip install mutagen
```

### 3. Configure Google Drive (First Time)

```bash
./sync_from_drive.py --setup
```

This guides you through:
1. rclone configuration
2. Google authentication
3. Creating "gdrive" remote

**Notes:**
- Browser will open for Google authentication
- Authorize rclone to access your Google Drive
- Token will be saved locally securely

## 📁 Google Drive Folder Structure

Create this structure on your Google Drive:

```
Faba/
  ├── incoming/      ← Upload new MP3s here
  └── processed/     ← Processed files moved here automatically
```

**How to create:**
1. Go to drive.google.com
2. Create "Faba" folder
3. Inside it, create "incoming" and "processed"
4. Share "incoming" folder with whoever needs to upload files

## 🚀 Usage

### 1. List Available Files

See which files are ready to download:

```bash
./sync_from_drive.py --list
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║  Available files on Google Drive                       ║
╚════════════════════════════════════════════════════════╝

📁 3 files found:

  • grandma_story.mp3
    Size: 2.34 MB
    Modified: 2026-02-10 14:30:00

  • uncle_song.mp3
    Size: 1.87 MB
    Modified: 2026-02-10 15:45:00

  • mom_tale.mp3
    Size: 3.12 MB
    Modified: 2026-02-10 16:20:00
```

### 2. Sync All Files

Download and automatically process all available files:

```bash
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01
```

**Automatic process:**
1. 📂 Scans Google Drive
2. ⬇️  Downloads MP3 files
3. 🎵 Shows processing options:
   - Option 1: All files in one figure (e.g., album/multi-part story)
   - Option 2: One figure per file (e.g., separate stories)
4. 🔐 Encrypts and adds to Faba
5. 📦 Moves processed files to "processed/"

### 3. Advanced Options

#### Specify custom ID prefix

```bash
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01 --prefix 8
```

Uses 8xxx range instead of default 9xxx.

#### Use different Google Drive folder

```bash
./sync_from_drive.py --sync-all --remote gdrive:MyCustomFolder
```

## 📝 Complete Examples

### Example 1: Initial Setup

```bash
# 1. First-time configuration
./sync_from_drive.py --setup

# 2. Create folders on Google Drive (via browser)
# drive.google.com → Create "Faba/incoming" and "Faba/processed"

# 3. Share "Faba/incoming" with people who need to upload files

# 4. Test connection
./sync_from_drive.py --list
```

### Example 2: Typical Workflow

```bash
# 1. Check for new files
./sync_from_drive.py --list

# 2. Connect Faba to PC
# (e.g., /dev/sdb1 mounted at /mnt/faba)

# 3. Sync
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01

# 4. Unmount Faba
sudo umount /mnt/faba
```

### Example 3: Multi-Part Story

If someone uploads a story in multiple parts:

```
Drive/Faba/incoming:
  part1.mp3
  part2.mp3
  part3.mp3
```

```bash
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01

# Choose option 1: "Create single figure with all files"
# Result: K9001 with CP01.MKI, CP02.MKI, CP03.MKI
```

## ❓ FAQ

### Q: Can I use Dropbox instead of Google Drive?
**A:** Yes! rclone supports many providers. Configure with:
```bash
rclone config
# Select "dropbox" instead of "drive"
```
Then use: `--remote dropbox:Faba`

### Q: What if someone uploads files while I'm syncing?
**A:** Script only downloads files present at scan time. New files will be available at next sync.

### Q: Are files deleted from Google Drive?
**A:** No, they're **moved** to "processed/" folder with timestamp. You can manually delete them later.

### Q: Can I sync without manual confirmation?
**A:** Currently script always asks for confirmation. To fully automate, you could modify the script, but manual confirmation is safer.

### Q: What if download fails halfway?
**A:** Files are downloaded to temporary folder. If process fails, temp folder is cleaned automatically.

### Q: How do I verify rclone configuration?
**A:**
```bash
# List configured remotes
rclone listremotes

# Test connection
rclone ls gdrive:

# List files in folder
rclone ls gdrive:Faba/incoming
```

## 🔐 Security & Privacy

### Access Tokens
- rclone saves tokens in `~/.config/rclone/rclone.conf`
- Tokens are encrypted
- Only you can access your Drive
- Revoke access from: https://myaccount.google.com/permissions

### Folder Sharing
- Share only "incoming" folder, not entire "Faba" folder
- Other users can only upload, not view or modify processed files
- You can revoke access anytime from Google Drive

## 🔗 Related Commands

- `add_tracks.py` - Manually add tracks to Faba
- `remove_ads.py` - Remove advertisements
- `backup_faba.py` - Create complete backup
- `rclone config` - Manage remote configurations

---

📖 **[Versione Italiana](SYNC_FROM_DRIVE.md)** | 🌍 **English Version** (current)
