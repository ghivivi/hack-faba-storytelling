# MyFaba Hacks

A collection of tools and scripts for customizing and enhancing your MyFaba and Faba+ storytelling box. Unlock new features, personalize your experience, and dive deeper into the world of interactive storytelling with this set of user-friendly hacks and mods.

## Features

- 🎵 Create custom audio figures for MyFaba and Faba+ devices
- 🔐 Encrypt/decrypt MyFaba audio files
- 🐍 Python GUI tool (Red Ele) for easy file management
- 🚫 Remove advertisements from your Faba device
- ➕ Add tracks to new or existing figures with automatic ID management
- 🔄 Automatic track renumbering and ID3 tag updates
- ☁️ Sync MP3 files from Google Drive (or other cloud storage)
- 💾 Complete backup system with maximum compression
- 📝 Comprehensive documentation and FAQ

## ⚠️ Backup Your Faba

**Before any modification, always create a backup!** The `backup_faba.py` script creates a compressed backup of your entire Faba disk.

**Quick Start:**

```bash
# Create backup with maximum compression
./backup_faba.py /mnt/faba/MKI01

# Fast backup (lower compression, faster)
./backup_faba.py /mnt/faba/MKI01 --fast

# Backup + upload to Google Drive
./backup_faba.py /mnt/faba/MKI01 --upload-to-drive
```

**Features:**
- 💾 **Maximum compression**: Reduces size by 60-70%
- 🔐 **SHA256 checksum**: Verify backup integrity
- ☁️ **Cloud upload**: Automatic upload to Google Drive
- 📊 **Detailed statistics**: File count, size, compression ratio
- ✅ **Auto-verification**: Ensures backup is valid

**Typical results:**
- Original: 150 MB → Backup: 45-50 MB (max compression)
- Backup time: 2-5 minutes for 150 MB

See **[BACKUP.md](BACKUP.md)** (IT) / **[BACKUP_EN.md](BACKUP_EN.md)** (EN) for detailed instructions and restore procedures.

## Sync from Google Drive

The `sync_from_drive.py` script allows you to easily receive MP3 files from others via Google Drive and automatically add them to your Faba device.

**Quick Start:**

```bash
# First-time setup (configure rclone)
./sync_from_drive.py --setup

# List available files on Google Drive
./sync_from_drive.py --list

# Download and process all new files
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01
```

**Perfect for:**
- 👵 Receiving recorded stories from grandparents
- 🎤 Getting custom recordings from family and friends
- 📚 Collaborative content creation
- ☁️ Cloud-based audio library management

**How it works:**
1. Someone uploads MP3 files to a shared Google Drive folder
2. Connect your Faba to your PC
3. Run the sync script - it downloads, encrypts, and adds files automatically
4. Processed files are archived on Drive

See **[SYNC_FROM_DRIVE.md](SYNC_FROM_DRIVE.md)** (IT) / **[SYNC_FROM_DRIVE_EN.md](SYNC_FROM_DRIVE_EN.md)** (EN) for setup instructions and detailed usage.

## Add Tracks to Faba

The `add_tracks.py` script makes it easy to add new MP3 files to your Faba device with automatic encryption, ID3 tag management, and track renumbering.

**Quick Start:**

```bash
# Create new figure with auto-incremental ID
./add_tracks.py /mnt/faba/MKI01 --new-figure track1.mp3 track2.mp3 track3.mp3

# Add tracks to existing figure
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 newtrack.mp3

# Insert track at specific position (renumbers subsequent tracks)
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 intro.mp3 --position 2
```

**Features:**
- 🆔 **Auto-incremental IDs**: Automatically finds the next available ID in your custom range (default: 9000-9999)
- 🏷️ **Custom ID ranges**: Use `--custom-prefix` to organize your content (e.g., 8xxx for audiobooks, 9xxx for music)
- 🔢 **Smart renumbering**: Insert tracks anywhere and all subsequent tracks are automatically renumbered
- 🏷️ **ID3 tag management**: Automatically updates all ID3 tags to match Faba's format (KxxxxCPyy)
- 🔐 **Automatic encryption**: Converts MP3 files to encrypted .MKI format

See **[ADD_TRACKS.md](ADD_TRACKS.md)** (IT) / **[ADD_TRACKS_EN.md](ADD_TRACKS_EN.md)** (EN) for detailed instructions and examples.

## Remove Advertisements

Many Faba figures include a short advertisement as the first track (CP01.MKI). You can safely remove these using the `remove_ads.py` script.

**Quick Start:**

```bash
# 1. Check what would be removed (safe, no changes)
./remove_ads.py /mnt/faba/MKI01 --dry-run

# 2. Move advertisements to backup folder (recommended)
./remove_ads.py /mnt/faba/MKI01 --backup
```

The script automatically identifies advertisements by file size (~448KB) and preserves all real content. See **[REMOVE_ADS.md](REMOVE_ADS.md)** (IT) / **[REMOVE_ADS_EN.md](REMOVE_ADS_EN.md)** (EN) for detailed instructions and safety information.

## Create your own figure (Original Faba)

For the original FABA (red cube), you can create custom figures with your own audio files.

**Method 1: Shell Script (Linux/macOS)**

1. Create a folder with your MP3 files
2. Run the creation script:
   ```bash
   ./createFigure.sh <figure_ID (4 digits)> <source_folder>
   ```

   Example for figure with ID 0742:
   ```bash
   ./createFigure.sh 0742 /home/user/mysongs
   ```

3. Copy the generated `K0742` folder to your Faba box
4. Write an NFC tag with the figure ID (see [FAQ](FAQ.md))
5. Enjoy your custom audio!

**Method 2: Python Tool (All platforms)**

For an alternative implementation with GUI, see the [Python Red Ele tool](python/README.md).

## Create your own figure (Faba+)

For Faba+ devices, the process is similar but uses a different file format (no encryption, just renamed MP3s with an info file).

1. Create a folder with your MP3 files
2. Run the Faba+ creation script:
   ```bash
   ./createFigureFabaPlus.sh <figure_ID (4 digits)> <source_folder>
   ```

   Example for figure with ID 0742:
   ```bash
   ./createFigureFabaPlus.sh 0742 /home/user/mysongs
   ```

3. Copy the generated files to your Faba+ box (requires opening the device, see [FAQ](FAQ.md))
4. Write an NFC tag with the figure ID
5. Enjoy your custom audio!

**Note:** Faba+ uses a MicroSD card inside the device. You'll need to open the device to access it (screws are under the red bottom pins).

## Cipher and Decipher Files

### Decipher (Decrypt) File
To decrypt a .MKI file from the Faba box back to MP3, use the Python Red Ele tool:
```bash
cd python && python3 redele.py decrypt --source-folder /mnt/faba/MKI01/K0403 --target-folder /home/user/decrypted
```

### Cipher (Encrypt) File
To encrypt a single MP3 file for use with Faba box:
```bash
python3 python/mki_cipher.py /home/user/mysong.mp3
# Output: mysong.mp3.MKI
```

---

## Known Figure IDs

For a list of known figure IDs and their corresponding characters, please check our [TAGS list](TAGS.md).

## FAQ

For frequently asked questions and troubleshooting tips, please check our [FAQ](FAQ.md).
This addition provides a link to a separate FAQ.md file where you can include frequently asked questions and their answers. Make sure to create the FAQ.md file in the same directory as the README.md file.

## 📚 Documentation Languages

All major tools have documentation available in both Italian and English:

| Tool | Italian 🇮🇹 | English 🇬🇧 |
|------|-----------|------------|
| **Backup** | [BACKUP.md](BACKUP.md) | [BACKUP_EN.md](BACKUP_EN.md) |
| **Add Tracks** | [ADD_TRACKS.md](ADD_TRACKS.md) | [ADD_TRACKS_EN.md](ADD_TRACKS_EN.md) |
| **Remove Ads** | [REMOVE_ADS.md](REMOVE_ADS.md) | [REMOVE_ADS_EN.md](REMOVE_ADS_EN.md) |
| **Sync from Drive** | [SYNC_FROM_DRIVE.md](SYNC_FROM_DRIVE.md) | [SYNC_FROM_DRIVE_EN.md](SYNC_FROM_DRIVE_EN.md) |

## Learn More

To understand how MyFaba works and the process of analyzing and customizing it, read our detailed article:
[Hacking MyFaba: An Educational Journey into Storytelling Box Customization](https://medium.com/@wansors/hacking-myfaba-an-educational-journey-into-storytelling-box-customization-cc6fc5db719d)