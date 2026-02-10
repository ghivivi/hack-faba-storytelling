#!/usr/bin/env python3
"""
add_tracks.py - Faba Track Manager

Aggiunge nuovi file MP3 al dispositivo Faba:
- Crea nuove figure con ID autoincrementale personalizzato
- Aggiunge tracce a figure esistenti con rinumerazione automatica
- Gestisce cifratura .MKI e aggiornamento tag ID3

Usage:
  # Crea nuova figura con ID autoincrementale
  ./add_tracks.py /mnt/faba/MKI01 --new-figure track1.mp3 track2.mp3 [--custom-id MYPREFIX]

  # Aggiunge a figura esistente alla fine
  ./add_tracks.py /mnt/faba/MKI01 --add-to K0015 track.mp3

  # Inserisce in posizione specifica con rinumerazione
  ./add_tracks.py /mnt/faba/MKI01 --add-to K0015 track.mp3 --position 2
"""

import os
import sys
import re
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional

# Cipher transformation tables (from MyFaba encryption algorithm)
BYTE_HIGH_NIBBLE = [
    [0x30, 0x30, 0x20, 0x20, 0x10, 0x10, 0x00, 0x00, 0x70, 0x70, 0x60, 0x60, 0x50, 0x50, 0x40, 0x40,
     0xB0, 0xB0, 0xA0, 0xA0, 0x90, 0x90, 0x80, 0x80, 0xF0, 0xF0, 0xE0, 0xE0, 0xD0, 0xD0, 0xC0, 0xC0],
    [0x00, 0x00, 0x10, 0x10, 0x20, 0x20, 0x30, 0x30, 0x40, 0x40, 0x50, 0x50, 0x60, 0x60, 0x70, 0x70,
     0x80, 0x80, 0x90, 0x90, 0xA0, 0xA0, 0xB0, 0xB0, 0xC0, 0xC0, 0xD0, 0xD0, 0xE0, 0xE0, 0xF0, 0xF0],
    [0x10, 0x10, 0x00, 0x00, 0x30, 0x30, 0x20, 0x20, 0x50, 0x50, 0x40, 0x40, 0x70, 0x70, 0x60, 0x60,
     0x90, 0x90, 0x80, 0x80, 0xB0, 0xB0, 0xA0, 0xA0, 0xD0, 0xD0, 0xC0, 0xC0, 0xF0, 0xF0, 0xE0, 0xE0],
    [0x20, 0x20, 0x30, 0x30, 0x00, 0x00, 0x10, 0x10, 0x60, 0x60, 0x70, 0x70, 0x40, 0x40, 0x50, 0x50,
     0xA0, 0xA0, 0xB0, 0xB0, 0x80, 0x80, 0x90, 0x90, 0xE0, 0xE0, 0xF0, 0xF0, 0xC0, 0xC0, 0xD0, 0xD0]
]

BYTE_LOW_NIBBLE_EVEN = [
    [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7],
    [0x4, 0x5, 0x6, 0x7, 0x0, 0x1, 0x2, 0x3],
    [0x2, 0x3, 0x0, 0x1, 0x6, 0x7, 0x4, 0x5],
    [0x6, 0x7, 0x4, 0x5, 0x2, 0x3, 0x0, 0x1]
]

BYTE_LOW_NIBBLE_ODD = [
    [0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF],
    [0xD, 0xC, 0xF, 0xE, 0x9, 0x8, 0xB, 0xA],
    [0x1, 0x0, 0x3, 0x2, 0x5, 0x4, 0x7, 0x6],
    [0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF]
]

# Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'

def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.NC}")

def cipher_file(input_path: Path, output_path: Path):
    """
    Cipher .mp3 file to .MKI using custom transformation.

    Args:
        input_path: Path to .mp3 file
        output_path: Path where encrypted .MKI will be saved
    """
    with open(input_path, "rb") as infile, open(output_path, "wb") as outfile:
        pos = 0
        while byte_read := infile.read(1):
            byte_val = byte_read[0]
            byte_pos = pos % 4

            # Apply high nibble transformation
            modified_byte = BYTE_HIGH_NIBBLE[byte_pos][byte_val % 32]

            # Apply low nibble transformation
            if byte_val % 2 == 0:
                modified_byte += BYTE_LOW_NIBBLE_EVEN[byte_pos][byte_val // 32]
            else:
                modified_byte += BYTE_LOW_NIBBLE_ODD[byte_pos][byte_val // 32]

            outfile.write(bytes([modified_byte]))
            pos += 1

def decipher_file(input_path: Path, output_path: Path):
    """
    Decipher .MKI file to .mp3 using reverse transformation.

    Args:
        input_path: Path to encrypted .MKI file
        output_path: Path where decrypted .mp3 will be saved
    """
    with open(input_path, "rb") as infile, open(output_path, "wb") as outfile:
        pos = 0
        while byte_read := infile.read(1):
            byte_val = byte_read[0]
            byte_pos = pos % 4

            # Extract high and low nibbles
            high_byte = byte_val & 0xF0
            low_byte = byte_val & 0x0F

            # Find indices in transformation tables
            index_high = BYTE_HIGH_NIBBLE[byte_pos].index(high_byte)
            if low_byte in BYTE_LOW_NIBBLE_EVEN[byte_pos]:
                index_low = BYTE_LOW_NIBBLE_EVEN[byte_pos].index(low_byte)
            else:
                index_low = BYTE_LOW_NIBBLE_ODD[byte_pos].index(low_byte)
                index_high += 1

            # Reconstruct original byte
            original_byte = index_low * 32 + index_high
            outfile.write(bytes([original_byte]))
            pos += 1

def update_id3_tag(mp3_path: Path, figure_id: str, track_num: int):
    """
    Update ID3 title tag in MP3 file with format KxxxxCPyy.

    Args:
        mp3_path: Path to MP3 file
        figure_id: 4-digit figure ID (e.g., "0015")
        track_num: Track number (e.g., 1, 2, 3...)
    """
    try:
        from mutagen.id3 import ID3, TIT2
        from mutagen.mp3 import MP3

        tags = MP3(str(mp3_path), ID3=ID3)
        # Clear all tags and set new title
        tags.delete()
        new_title = f"K{figure_id}CP{track_num:02d}"
        tags["TIT2"] = TIT2(encoding=3, text=new_title)
        tags.save()
    except Exception as e:
        raise Exception(f"Errore aggiornamento tag ID3 per {mp3_path.name}: {e}")

def scan_existing_ids(faba_dir: Path, custom_prefix: Optional[str] = None) -> List[str]:
    """
    Scan all existing figure IDs in the Faba directory.

    Args:
        faba_dir: Root Faba directory
        custom_prefix: Optional custom prefix to filter IDs (e.g., "9" for 9xxx IDs)

    Returns:
        Sorted list of figure IDs (4-digit strings)
    """
    ids = []
    pattern = re.compile(r'^K(\d{4})$')

    for folder in faba_dir.glob('K*'):
        if folder.is_dir():
            match = pattern.match(folder.name)
            if match:
                figure_id = match.group(1)
                if custom_prefix is None or figure_id.startswith(custom_prefix):
                    ids.append(figure_id)

    return sorted(ids)

def generate_next_id(faba_dir: Path, custom_prefix: Optional[str] = None) -> str:
    """
    Generate the next available figure ID.

    Args:
        faba_dir: Root Faba directory
        custom_prefix: Optional custom prefix (e.g., "9" for 9xxx range)

    Returns:
        Next available 4-digit ID as string
    """
    # Default to range 9xxx for custom figures if no prefix specified
    if custom_prefix is None:
        custom_prefix = "9"

    existing_ids = scan_existing_ids(faba_dir, custom_prefix)

    if not existing_ids:
        # No existing IDs with this prefix, start at X000
        return f"{custom_prefix}000"

    # Find the highest ID and increment
    last_id = existing_ids[-1]
    next_num = int(last_id) + 1

    # Check if we're still in the valid range for this prefix
    prefix_max = int(custom_prefix) * 1000 + 999
    if next_num > prefix_max:
        raise Exception(f"Errore: Raggiunto il limite massimo per il prefisso {custom_prefix} ({prefix_max})")

    if next_num > 9999:
        raise Exception("Errore: Raggiunto il limite massimo di ID (9999)")

    return f"{next_num:04d}"

def create_new_figure(faba_dir: Path, mp3_files: List[Path], custom_id: Optional[str] = None,
                     custom_prefix: Optional[str] = None) -> str:
    """
    Create a new figure folder with encrypted tracks.

    Args:
        faba_dir: Root Faba directory
        mp3_files: List of MP3 file paths to add
        custom_id: Optional specific ID to use (e.g., "9001")
        custom_prefix: Optional prefix for auto-generation (e.g., "9" for 9xxx)

    Returns:
        The figure ID that was created
    """
    # Determine figure ID
    if custom_id:
        figure_id = custom_id
        if len(figure_id) != 4 or not figure_id.isdigit():
            raise Exception("L'ID custom deve essere di 4 cifre numeriche (es. 9001)")
    else:
        figure_id = generate_next_id(faba_dir, custom_prefix)

    folder_name = f"K{figure_id}"
    figure_dir = faba_dir / folder_name

    # Check if folder already exists
    if figure_dir.exists():
        raise Exception(f"Errore: La cartella {folder_name} esiste già")

    print()
    print_colored("═" * 60, Colors.CYAN)
    print_colored("  CREAZIONE NUOVA FIGURA", Colors.CYAN)
    print_colored("═" * 60, Colors.CYAN)
    print()
    print_colored(f"📁 Cartella: {folder_name}", Colors.BOLD)
    print(f"   ID figura: {figure_id}")
    print(f"   Tracce: {len(mp3_files)}")
    print()

    for i, mp3_file in enumerate(mp3_files, start=1):
        print(f"   CP{i:02d}: {mp3_file.name}")
    print()

    confirm = input("Confermi la creazione? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operazione annullata.")
        return None

    # Create folder
    figure_dir.mkdir(parents=True, exist_ok=False)
    print()
    print_colored(f"✓ Cartella {folder_name} creata", Colors.GREEN)

    # Process each MP3 file
    for track_num, mp3_file in enumerate(mp3_files, start=1):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_dir = Path(tmpdir)
                temp_mp3 = temp_dir / f"temp_{track_num}.mp3"

                # Copy MP3 to temp location
                import shutil
                shutil.copy(str(mp3_file), str(temp_mp3))

                # Update ID3 tag
                update_id3_tag(temp_mp3, figure_id, track_num)

                # Cipher to .MKI
                mki_filename = f"CP{track_num:02d}.MKI"
                mki_path = figure_dir / mki_filename
                cipher_file(temp_mp3, mki_path)

                print_colored(f"✓ {mki_filename} creato da {mp3_file.name}", Colors.GREEN)

        except Exception as e:
            print_colored(f"✗ Errore con {mp3_file.name}: {e}", Colors.RED)
            # Cleanup on error
            if figure_dir.exists():
                import shutil
                shutil.rmtree(figure_dir)
            raise Exception(f"Creazione figura fallita: {e}")

    print()
    print_colored("═" * 60, Colors.GREEN)
    print_colored(f"✓ Figura {folder_name} creata con successo!", Colors.GREEN)
    print_colored(f"  Tracce: {len(mp3_files)}", Colors.GREEN)
    print_colored("═" * 60, Colors.GREEN)

    return figure_id

def add_to_existing_figure(faba_dir: Path, figure_id: str, mp3_files: List[Path],
                           position: Optional[int] = None):
    """
    Add tracks to an existing figure, optionally at a specific position.

    Args:
        faba_dir: Root Faba directory
        figure_id: Figure ID (e.g., "0015" from K0015)
        mp3_files: List of MP3 file paths to add
        position: Optional position to insert (1-based). None = append at end
    """
    folder_name = f"K{figure_id}"
    figure_dir = faba_dir / folder_name

    if not figure_dir.exists():
        raise Exception(f"Errore: La cartella {folder_name} non esiste")

    # Find existing tracks
    existing_tracks = sorted(figure_dir.glob('CP*.MKI'))
    num_existing = len(existing_tracks)

    if position is None:
        position = num_existing + 1  # Append at end

    if position < 1 or position > num_existing + 1:
        raise Exception(f"Posizione non valida. Deve essere tra 1 e {num_existing + 1}")

    print()
    print_colored("═" * 60, Colors.CYAN)
    print_colored("  AGGIUNTA TRACCE A FIGURA ESISTENTE", Colors.CYAN)
    print_colored("═" * 60, Colors.CYAN)
    print()
    print_colored(f"📁 Cartella: {folder_name}", Colors.BOLD)
    print(f"   Tracce esistenti: {num_existing}")
    print(f"   Nuove tracce: {len(mp3_files)}")
    print(f"   Posizione inserimento: {position}")
    print()

    print_colored("Nuove tracce da aggiungere:", Colors.YELLOW)
    for i, mp3_file in enumerate(mp3_files, start=position):
        print(f"   CP{i:02d}: {mp3_file.name}")
    print()

    if position <= num_existing:
        print_colored(f"⚠️  Le tracce dalla posizione {position} in poi verranno rinumerate:", Colors.YELLOW)
        tracks_to_renumber = existing_tracks[position-1:]
        for old_track in tracks_to_renumber:
            old_num = int(old_track.stem[2:])
            new_num = old_num + len(mp3_files)
            print(f"   CP{old_num:02d}.MKI → CP{new_num:02d}.MKI")
        print()

    confirm = input("Confermi l'operazione? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operazione annullata.")
        return

    print()

    # Step 1: Renumber existing tracks if needed (work backwards to avoid conflicts)
    if position <= num_existing:
        print_colored("📝 Rinumerazione tracce esistenti...", Colors.BLUE)
        tracks_to_renumber = sorted(existing_tracks[position-1:], reverse=True)

        for old_track in tracks_to_renumber:
            old_num = int(old_track.stem[2:])
            new_num = old_num + len(mp3_files)

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    temp_dir = Path(tmpdir)
                    temp_mp3 = temp_dir / "temp.mp3"
                    temp_mki = temp_dir / f"CP{new_num:02d}.MKI"

                    # Decipher
                    decipher_file(old_track, temp_mp3)

                    # Update ID3 tag
                    update_id3_tag(temp_mp3, figure_id, new_num)

                    # Cipher back
                    cipher_file(temp_mp3, temp_mki)

                    # Move to final location
                    new_path = figure_dir / f"CP{new_num:02d}.MKI"
                    import shutil
                    shutil.move(str(temp_mki), str(new_path))

                    # Remove old file
                    old_track.unlink()

                    print_colored(f"  ✓ CP{old_num:02d}.MKI → CP{new_num:02d}.MKI", Colors.GREEN)

            except Exception as e:
                print_colored(f"  ✗ Errore rinumerazione CP{old_num:02d}.MKI: {e}", Colors.RED)
                raise Exception(f"Rinumerazione fallita: {e}")
        print()

    # Step 2: Add new tracks
    print_colored("➕ Aggiunta nuove tracce...", Colors.BLUE)
    for i, mp3_file in enumerate(mp3_files):
        track_num = position + i
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_dir = Path(tmpdir)
                temp_mp3 = temp_dir / "temp.mp3"

                # Copy MP3
                import shutil
                shutil.copy(str(mp3_file), str(temp_mp3))

                # Update ID3 tag
                update_id3_tag(temp_mp3, figure_id, track_num)

                # Cipher to .MKI
                mki_filename = f"CP{track_num:02d}.MKI"
                mki_path = figure_dir / mki_filename
                cipher_file(temp_mp3, mki_path)

                print_colored(f"  ✓ {mki_filename} creato da {mp3_file.name}", Colors.GREEN)

        except Exception as e:
            print_colored(f"  ✗ Errore con {mp3_file.name}: {e}", Colors.RED)
            raise Exception(f"Aggiunta traccia fallita: {e}")

    print()
    print_colored("═" * 60, Colors.GREEN)
    print_colored(f"✓ Tracce aggiunte con successo a {folder_name}!", Colors.GREEN)
    print_colored(f"  Totale tracce: {num_existing + len(mp3_files)}", Colors.GREEN)
    print_colored("═" * 60, Colors.GREEN)

def show_usage():
    """Display usage information"""
    print("Usage: add_tracks.py <faba_directory> [options]")
    print()
    print("Crea nuova figura:")
    print("  --new-figure <mp3_files...>     Crea nuova figura con ID autoincrementale")
    print("  --custom-id XXXX                Usa ID specifico (4 cifre, es. 9001)")
    print("  --custom-prefix X               Usa prefisso per range custom (es. 9 per 9xxx)")
    print()
    print("Aggiunge a figura esistente:")
    print("  --add-to KXXXX <mp3_files...>   Aggiunge tracce a figura esistente")
    print("  --position N                    Inserisce alla posizione N (default: append)")
    print()
    print("Esempi:")
    print("  # Crea nuova figura con ID autoincrementale nel range 9xxx")
    print("  ./add_tracks.py /mnt/faba/MKI01 --new-figure track1.mp3 track2.mp3")
    print()
    print("  # Crea nuova figura con ID specifico")
    print("  ./add_tracks.py /mnt/faba/MKI01 --new-figure *.mp3 --custom-id 9100")
    print()
    print("  # Aggiunge tracce alla fine di una figura esistente")
    print("  ./add_tracks.py /mnt/faba/MKI01 --add-to K0015 newtrack.mp3")
    print()
    print("  # Inserisce traccia in posizione 2 (rinumera le successive)")
    print("  ./add_tracks.py /mnt/faba/MKI01 --add-to K0015 intro.mp3 --position 2")
    print()
    print("Requisiti:")
    print("  pip install mutagen")

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    # Check for mutagen
    try:
        import mutagen
        from mutagen.id3 import ID3, TIT2
        from mutagen.mp3 import MP3
    except ImportError:
        print_colored("Errore: Il modulo 'mutagen' è richiesto", Colors.RED)
        print("Installa con: pip install mutagen")
        sys.exit(1)

    faba_dir = Path(sys.argv[1])

    if not faba_dir.is_dir():
        print_colored(f"Errore: Directory '{faba_dir}' non trovata", Colors.RED)
        sys.exit(1)

    # Parse arguments
    args = sys.argv[2:]

    if not args:
        show_usage()
        sys.exit(1)

    mode = args[0]

    # Header
    print_colored("╔════════════════════════════════════════════════════════╗", Colors.BLUE)
    print_colored("║  Faba Track Manager                                    ║", Colors.BLUE)
    print_colored("╚════════════════════════════════════════════════════════╝", Colors.BLUE)

    try:
        if mode == '--new-figure':
            # Parse MP3 files and options
            mp3_files = []
            custom_id = None
            custom_prefix = None

            i = 1
            while i < len(args):
                arg = args[i]
                if arg == '--custom-id':
                    if i + 1 >= len(args):
                        raise Exception("--custom-id richiede un valore")
                    custom_id = args[i + 1]
                    i += 2
                elif arg == '--custom-prefix':
                    if i + 1 >= len(args):
                        raise Exception("--custom-prefix richiede un valore")
                    custom_prefix = args[i + 1]
                    i += 2
                else:
                    # Assume it's an MP3 file
                    mp3_path = Path(arg)
                    if not mp3_path.exists():
                        raise Exception(f"File non trovato: {arg}")
                    if not mp3_path.suffix.lower() in ['.mp3', '.MP3']:
                        raise Exception(f"File non è un MP3: {arg}")
                    mp3_files.append(mp3_path)
                    i += 1

            if not mp3_files:
                raise Exception("Nessun file MP3 specificato")

            create_new_figure(faba_dir, mp3_files, custom_id, custom_prefix)

        elif mode == '--add-to':
            if len(args) < 2:
                raise Exception("--add-to richiede un ID figura e file MP3")

            figure_id = args[1]
            # Remove 'K' prefix if present
            if figure_id.startswith('K'):
                figure_id = figure_id[1:]

            if len(figure_id) != 4 or not figure_id.isdigit():
                raise Exception("ID figura deve essere di 4 cifre (es. K0015 o 0015)")

            # Parse MP3 files and position
            mp3_files = []
            position = None

            i = 2
            while i < len(args):
                arg = args[i]
                if arg == '--position':
                    if i + 1 >= len(args):
                        raise Exception("--position richiede un valore numerico")
                    position = int(args[i + 1])
                    i += 2
                else:
                    # Assume it's an MP3 file
                    mp3_path = Path(arg)
                    if not mp3_path.exists():
                        raise Exception(f"File non trovato: {arg}")
                    if not mp3_path.suffix.lower() in ['.mp3', '.MP3']:
                        raise Exception(f"File non è un MP3: {arg}")
                    mp3_files.append(mp3_path)
                    i += 1

            if not mp3_files:
                raise Exception("Nessun file MP3 specificato")

            add_to_existing_figure(faba_dir, figure_id, mp3_files, position)

        else:
            print_colored(f"Errore: Modalità non valida '{mode}'", Colors.RED)
            print()
            show_usage()
            sys.exit(1)

    except Exception as e:
        print()
        print_colored(f"❌ Errore: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
