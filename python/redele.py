#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Red Ele - MyFaba Box MP3 Encryption/Decryption Tool"""

import codecs
import mutagen
import os
import re
import shutil
import sys
import utils

from pathlib import Path
from gooey import GooeyParser
from mutagen.id3 import ID3, TIT2
from mutagen.mp3 import MP3
from cipher import encrypt_file, decrypt_file

FIGURE_ID_PATTERN = r"^\d{4}$"
FIGURE_DIR_PATTERN = r'[\\/]K(\d{4})$'


def clear_and_set_title(mp3_file, new_title):
    try:
        tags = MP3(mp3_file, ID3=ID3)
        tags.delete()
        tags["TIT2"] = TIT2(encoding=3, text=new_title)
        tags.save()
    except Exception as e:
        print(f"Error processing {mp3_file}: {e}")
        sys.exit(1)


def run_encrypt(args):
    mutagen.id3._tags.ID3Header.__init__ = utils.id3header_constructor_monkeypatch

    mp3_files = {}
    count = 0

    if args.extract_figure:
        for root, _, filenames in os.walk(args.source_folder):
            match = re.search(FIGURE_DIR_PATTERN, root)
            for filename in filenames:
                if filename.lower().endswith(".mp3") and match:
                    mp3_files.setdefault(match.group(1), []).append(Path(root) / filename)
                    count += 1
    else:
        if not re.match(FIGURE_ID_PATTERN, args.figure_id):
            print("Error: Figure ID must be exactly 4 digits (0001-9999).")
            sys.exit(1)
        for root, _, filenames in os.walk(args.source_folder):
            for filename in filenames:
                if filename.lower().endswith(".mp3"):
                    mp3_files.setdefault(args.figure_id, []).append(Path(root) / filename)
                    count += 1

    if count == 0:
        print("No MP3 files found in the source folder.")
        sys.exit(1)

    iterator = 1
    for figure, files in mp3_files.items():
        os.makedirs(Path(args.target_folder) / f"K{figure}", exist_ok=True)
        for filenum, source_file in enumerate(files, start=1):
            print(f"=========================[{iterator}/{count}]")
            print(f"Processing {source_file}...")
            filenum_str = f"{filenum:02d}"
            new_title = f"K{figure}CP{filenum_str}"
            target_file = str(Path(args.target_folder) / f"K{figure}" / f"CP{filenum_str}")
            shutil.copy(source_file, target_file)
            clear_and_set_title(target_file, new_title)
            encrypt_file(target_file)
            os.remove(target_file)
            iterator += 1

    print(f"Processing complete. Copy the files from '{args.target_folder}' directory to your Faba box.")


def run_decrypt(args):
    mki_files = {}
    count = 0

    for root, _, filenames in os.walk(args.source_folder):
        rel_path = Path(root).relative_to(args.source_folder)
        for filename in filenames:
            if filename.lower().endswith(".mki"):
                mki_files.setdefault(str(rel_path), []).append(filename)
                count += 1

    if count == 0:
        print("No MKI files found in the source folder.")
        sys.exit(1)

    mki_re = re.compile(re.escape('.mki'), re.IGNORECASE)
    iterator = 1
    for subdir, files in mki_files.items():
        os.makedirs(Path(args.target_folder) / subdir, exist_ok=True)
        for filename in files:
            print(f"=========================[{iterator}/{count}]")
            print(f"Processing {Path(subdir) / filename}...")
            source_file = str(Path(args.source_folder) / subdir / filename)
            target_file = mki_re.sub('.mp3', str(Path(args.target_folder) / subdir / filename))
            decrypt_file(source_file, target_file)
            iterator += 1

    print("Processing complete.")


def main():
    parser = GooeyParser(
        prog="Red Ele",
        description="Encrypt/Decrypt myfaba box MP3s",
    )
    subs = parser.add_subparsers(help="commands", dest="command")

    encrypt_group = subs.add_parser("encrypt", prog="Encrypt").add_argument_group("")
    encrypt_group.add_argument("-f", "--figure-id", metavar="Figure ID",
                               help="Faba NFC chip identifier (4 digit number 0001-9999)", default="0000")
    encrypt_group.add_argument("-x", "--extract-figure", metavar="Extract Figure ID", action="store_true",
                               help="Get figure ID from directory name (MP3 files have to be located in folder named K0001-K9999)")
    encrypt_group.add_argument("-s", "--source-folder", metavar="Source Folder",
                               help="Folder with MP3 files to process.",
                               widget='DirChooser', gooey_options={'full_width': True})
    encrypt_group.add_argument("-t", "--target-folder", metavar="Target Folder",
                               help="Folder where generated FABA .MKI files will be stored. Subfolder for the figure will be created.",
                               widget='DirChooser', gooey_options={'full_width': True})

    decrypt_group = subs.add_parser("decrypt", prog="Decrypt").add_argument_group("")
    decrypt_group.add_argument("-s", "--source-folder", metavar="Source Folder",
                               help="Folder with MKI files to process. Supports recursion.",
                               widget='DirChooser', gooey_options={'full_width': True})
    decrypt_group.add_argument("-t", "--target-folder", metavar="Target Folder",
                               help="Folder for decrypted MP3 files.",
                               widget='DirChooser', gooey_options={'full_width': True})

    args = parser.parse_args()

    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = utils.Unbuffered(codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict'))
    if sys.stderr.encoding != 'UTF-8':
        sys.stderr = utils.Unbuffered(codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict'))

    if not os.path.isdir(args.source_folder):
        print(f"Error: Source folder '{args.source_folder}' does not exist or is not a directory.")
        sys.exit(1)

    if args.command == "encrypt":
        run_encrypt(args)
    elif args.command == "decrypt":
        run_decrypt(args)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        from gooey import Gooey
        main = Gooey(program_name='Red Ele',
                     default_size=(600, 600),
                     progress_regex=r"^=+\[(\d+)/(\d+)]$",
                     progress_expr="x[0] / x[1] * 100",
                     encoding='UTF-8',
                     navigation="TABBED",
                     )(main)
    if '--ignore-gooey' in sys.argv:
        sys.argv.remove('--ignore-gooey')
    main()
