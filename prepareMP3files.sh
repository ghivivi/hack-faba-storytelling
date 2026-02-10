#!/bin/bash

# prepareMP3files.sh
# Rename all MP3 files and edit song title ID3 tags
# Requires: id3v2 (install with: sudo apt-get install id3v2)
#
# Usage: ./prepareMP3files.sh <figure_ID (4 digits)>
# Where XXXX is the 4-digit ID number after the K
# Example: ./prepareMP3files.sh 1234  -->  K1234CP01, K1234CP02, ...

# Exit immediately if a command exits with a non-zero status
set -e

if [ -z "$1" ]; then
    echo "Error: Missing figure ID argument"
    echo "Usage: $0 <figure_ID (4 digits)>"
    exit 1
fi

# Validate that figure ID is exactly 4 digits
if ! [[ "$1" =~ ^[0-9]{4}$ ]]; then
    echo "Error: Figure ID must be exactly 4 digits"
    exit 1
fi

# Check if id3v2 is installed
if ! command -v id3v2 >/dev/null 2>&1; then
    echo "Error: id3v2 is not installed. Please install it with: sudo apt-get install id3v2"
    exit 1
fi

base="$1"
count=1
processed=0

# Check if there are any MP3 files in the current directory
if ! ls *.mp3 >/dev/null 2>&1; then
    echo "Error: No MP3 files found in current directory"
    exit 1
fi

for f in *.mp3; do
    # Skip if file doesn't exist (glob didn't match)
    [ -e "$f" ] || continue

    # Generate new filename with zero padding (CP01.mp3, CP02.mp3, ...)
    new=$(printf "CP%02d.mp3" $count)

    echo "Renaming: $f → $new"
    if ! mv -n "$f" "$new"; then
        echo "Error: Failed to rename $f to $new"
        exit 1
    fi

    # Set tag definition: KxxxxCPyy
    song_id=$(printf "K%sCP%02d" "$base" $count)
    echo "  Setting ID3 tag: $song_id"

    # Clear all existing tags and set the song title
    if ! id3v2 -a "" -A "" -c "" -g "" -y "" -T "" --song "$song_id" "$new" >/dev/null 2>&1; then
        echo "Warning: Failed to set ID3 tag for $new"
    fi

    count=$((count + 1))
    processed=$((processed + 1))
done

echo ""
echo "Processing complete! Successfully processed $processed MP3 files."
