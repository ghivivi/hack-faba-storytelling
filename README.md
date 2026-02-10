# MyFaba Hacks

A collection of tools and scripts for customizing and enhancing your MyFaba and Faba+ storytelling box. Unlock new features, personalize your experience, and dive deeper into the world of interactive storytelling with this set of user-friendly hacks and mods.

## Features

- 🎵 Create custom audio figures for MyFaba and Faba+ devices
- 🔐 Encrypt/decrypt MyFaba audio files
- 🐍 Python GUI tool (Red Ele) for easy file management
- 🐳 Docker support for cross-platform compatibility
- 🚫 Remove advertisements from your Faba device
- ➕ Add tracks to new or existing figures with automatic ID management
- 🔄 Automatic track renumbering and ID3 tag updates
- ☁️ Sync MP3 files from Google Drive (or other cloud storage)
- 📝 Comprehensive documentation and FAQ

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

See **[SYNC_FROM_DRIVE.md](SYNC_FROM_DRIVE.md)** for setup instructions and detailed usage.

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

See **[ADD_TRACKS.md](ADD_TRACKS.md)** for detailed instructions and examples.

## Remove Advertisements

Many Faba figures include a short advertisement as the first track (CP01.MKI). You can safely remove these using the `remove_ads.py` script.

**Quick Start:**

```bash
# 1. Check what would be removed (safe, no changes)
./remove_ads.py /mnt/faba/MKI01 --dry-run

# 2. Move advertisements to backup folder (recommended)
./remove_ads.py /mnt/faba/MKI01 --backup
```

The script automatically identifies advertisements by file size (~448KB) and preserves all real content. See **[REMOVE_ADS.md](REMOVE_ADS.md)** for detailed instructions and safety information.

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

### Prerequisites
First, compile the Java files:
```bash
javac MKICipher.java MKIDecipher.java
```

### Decipher (Decrypt) File
To decrypt a .MKI file from the Faba box back to MP3:
```bash
java MKIDecipher /path/to/encrypted/file
```

Example:
```bash
java MKIDecipher /mnt/faba/MKI01/K0403/CP01
# Output: CP01.mp3
```

### Cipher (Encrypt) File
To encrypt an MP3 file for use with Faba box:
```bash
java MKICipher /path/to/mp3/file
```

Example:
```bash
java MKICipher /home/user/mysong.mp3
# Output: mysong.mp3.MKI
```

---

## Using the Docker Image

If you're using Windows or prefer not to set up the scripts and dependencies manually, you can use a Docker-based alternative to run the scripts in a containerized environment. This method eliminates the need to install Java or other tools on your system and provides a clean, portable setup.

>Note: This Docker-based solution is completely optional. It is an alternative to running the scripts directly on your system. If you already have the environment set up or prefer manual execution, you can skip this section.

To use Docker, follow these instructions. Please note that **Docker must be installed** on your system for these steps to work. You can download Docker from [here](https://www.docker.com/get-started).

### Step 1: Build the Docker Image

First, build the Docker image from the provided Dockerfile. This step only needs to be done once.

Open a terminal (Linux/macOS) or Command Prompt/PowerShell (Windows) and run:

#### On Linux/macOS:

```bash
docker build -t createfigure-image .
```

#### On Windows:

Open **Command Prompt** or **PowerShell**, then run the same command:
```bash
docker build -t createfigure-image .
```

This will create a Docker image named `createfigure-image` with all the necessary dependencies to run the script.

### Step 2: Run the Docker Container

Once the image is built, use the following command to run the `createFigure.sh` script inside the container.

For example, to create a figure with ID `999` using your song files from a folder named `my-songs`, use this command:

#### On Linux/macOS:

```bash
docker run --rm -v /path/to/my-songs:/source-folder createfigure-image 0999 /source-folder
```

#### On Windows:

Open **Command Prompt** or **PowerShell** and run this command:
```bash
docker run --rm -v C:\path\to\my-songs:/source-folder createfigure-image 999 /source-folder
```

Make sure to replace `C:\path\to\my-songs` with the actual path to the folder containing your songs in `.mp3` format. This folder will be mounted to the `/source-folder` directory inside the Docker container. You can use this exact name.

#### Explanation of the Command:

- `docker run`: Runs a Docker container.
- `--rm`: Automatically removes the container once it finishes running.
- `-v /path/to/my-songs:/source-folder`: Maps your local `my-songs` folder to the `/source-folder` directory inside the container. Ensure this path is correct based on your operating system.
- `createfigure-image`: The name of the Docker image you created in Step 1.
- `0999 /source-folder`: These are the arguments passed to the `createFigure.sh` script, where `0999` is the figure ID and `/source-folder` is the path to the source folder inside the container.

This will run the script inside the Docker container and output the files into the `/source-folder` directory, which is mapped to your local `my-songs` folder.

### What Happens After Running the Command

The script processes your `.mp3` files and creates a `K0999` folder inside your `my-songs` directory. This folder contains the modified files (e.g., `CP01`, `CP02`, etc.) and can be copied to your Faba box.

### Step 3: Follow the Remaining Instructions

After running the Docker container, follow the rest of the instructions in the [Create your own figure](#create-your-own-figure) section of this README to copy the generated files to your Faba box and write the NFC tag.

---

## Known Figure IDs

For a list of known figure IDs and their corresponding characters, please check our [TAGS list](TAGS.md).

## FAQ

For frequently asked questions and troubleshooting tips, please check our [FAQ](FAQ.md).
This addition provides a link to a separate FAQ.md file where you can include frequently asked questions and their answers. Make sure to create the FAQ.md file in the same directory as the README.md file.

## Learn More

To understand how MyFaba works and the process of analyzing and customizing it, read our detailed article:
[Hacking MyFaba: An Educational Journey into Storytelling Box Customization](https://medium.com/@wansors/hacking-myfaba-an-educational-journey-into-storytelling-box-customization-cc6fc5db719d)