# 🎵 Faba Track Manager

Script to add new MP3 files to Faba device with automatic management of:
- Auto-incremental custom IDs
- .MKI encryption
- Correct ID3 tag format
- Automatic track renumbering

## 🔧 Requirements

```bash
pip install mutagen
```

## 🚀 Usage

### 1. Create New Figure

#### Option A: Auto-incremental ID (Recommended)

Script scans disk, finds highest ID in custom range (default: 9xxx) and increments by 1:

```bash
./add_tracks.py /mnt/faba/MKI01 --new-figure track1.mp3 track2.mp3 track3.mp3
```

**Result:**
- Scans all existing K* folders
- Finds highest ID in 9xxx range (e.g., K9005)
- Creates new figure with ID 9006
- Processes files:
  - `track1.mp3` → `K9006/CP01.MKI` (ID3 tag: "K9006CP01")
  - `track2.mp3` → `K9006/CP02.MKI` (ID3 tag: "K9006CP02")
  - `track3.mp3` → `K9006/CP03.MKI` (ID3 tag: "K9006CP03")

#### Option B: Specific ID

```bash
./add_tracks.py /mnt/faba/MKI01 --new-figure *.mp3 --custom-id 9100
```

#### Option C: Custom Prefix

For different range (e.g., 8xxx instead of 9xxx):

```bash
./add_tracks.py /mnt/faba/MKI01 --new-figure *.mp3 --custom-prefix 8
```

### 2. Add Tracks to Existing Figure

#### Option A: Append (Add at End)

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 newtrack.mp3
```

#### Option B: Insert with Renumbering

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 intro.mp3 --position 2
```

**Process:**
1. 🔓 Decrypts all files from position N onwards
2. 🔄 Renumbers files (CP02→CP03, CP03→CP04, etc.)
3. 🏷️ Updates ID3 tags for each renumbered file
4. 🔐 Re-encrypts all modified files
5. ➕ Inserts new file at requested position

## 📝 Practical Examples

### Example 1: Create Custom Story

```bash
cd /home/user/my-story/
./add_tracks.py /mnt/faba/MKI01 --new-figure intro.mp3 chapter1.mp3 chapter2.mp3 epilogue.mp3
```

### Example 2: Add Missing Chapter

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K9001 chapter1-bis.mp3 --position 3
```

## ❓ FAQ

### Q: Which ID range should I use for custom content?
**A:** We recommend **9000-9999** range for custom content to avoid conflicts with original Faba figures (range 0000-8999).

### Q: What happens to existing ID3 tags in my MP3s?
**A:** Script **overwrites** all ID3 tags with Faba-required format (`KxxxxCPyy`). Other tags like artist, album, etc. are removed.

### Q: How do I organize my custom content?
**A:** Suggestions:
```
9000-9099: Audiobooks
9100-9199: Custom music
9200-9299: Recorded stories
9300-9399: Kids podcasts
9400-9999: Other content
```

## 🛡️ Safety

- ✅ **Confirmation required**: Script always asks before modifying files
- ✅ **ID validation**: Checks that ID doesn't already exist
- ✅ **Error handling**: On error during figure creation, folder is removed
- ✅ **Backup recommended**: Always backup microSD before mass operations

## 🔗 Related Commands

- `backup_faba.py` - Create complete backup before changes
- `remove_ads.py` - Remove ads and renumber tracks
- `sync_from_drive.py` - Sync MP3s from Google Drive

---

📖 **[Versione Italiana](ADD_TRACKS.md)** | 🌍 **English Version** (current)
