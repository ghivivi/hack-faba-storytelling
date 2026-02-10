#!/usr/bin/env python3
"""
remove_ads.py - Faba Advertisement Remover

Rimuove in modo sicuro i file CP01.MKI pubblicitari dalle cartelle Faba.

SICUREZZA:
- Identifica pubblicità basandosi sulla dimensione (440-470KB)
- Mostra anteprima prima di procedere
- Chiede conferma
- Crea backup prima di cancellare
- Log dettagliato delle operazioni

Usage: ./remove_ads.py <faba_directory> [--dry-run|--backup|--delete] [--renumber]
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Configuration
MIN_AD_SIZE = 440000  # 440KB
MAX_AD_SIZE = 470000  # 470KB

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
    BOLD = '\033[1m'
    NC = '\033[0m'

def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.NC}")

def log_message(log_file, message):
    """Write message to log file and console"""
    print(message)
    with open(log_file, 'a') as f:
        # Remove color codes for log file
        import re
        clean_message = re.sub(r'\033\[[0-9;]+m', '', message)
        f.write(clean_message + '\n')

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
        print_colored(f"⚠️  Warning: Could not update ID3 tag for {mp3_path.name}: {e}", Colors.YELLOW)
        print_colored("   Il file verrà comunque rinominato, ma il tag ID3 rimarrà invariato", Colors.YELLOW)

def renumber_tracks(faba_dir: Path, affected_folders: List[str], log_file, dry_run=False):
    """
    Renumber remaining tracks after CP01 removal.
    CP02 -> CP01, CP03 -> CP02, etc.
    Updates both filenames and ID3 tags.

    Args:
        faba_dir: Root Faba directory
        affected_folders: List of folder names where CP01 was removed
        log_file: Path to log file
        dry_run: If True, only show what would be done
    """
    if not affected_folders:
        return

    print()
    print_colored("═" * 60, Colors.BLUE)
    print_colored("  RINUMERAZIONE TRACCE", Colors.BLUE)
    print_colored("═" * 60, Colors.BLUE)
    print()

    if dry_run:
        print_colored("ℹ️  Modalità simulazione - mostra solo cosa verrebbe rinumerato", Colors.BLUE)
        print()

    renumbered_count = 0

    for folder_name in sorted(affected_folders):
        folder = faba_dir / folder_name

        # Find all CP*.MKI files (excluding CP01 which was removed)
        cp_files = sorted([f for f in folder.glob('CP*.MKI') if f.name != 'CP01.MKI'])

        if not cp_files:
            continue

        print_colored(f"📁 {folder_name}:", Colors.BOLD)
        log_message(log_file, f"Renumbering folder: {folder_name}")

        # Extract figure ID from folder name (K0015 -> 0015)
        figure_id = folder_name[1:]  # Remove 'K' prefix

        for new_num, old_file in enumerate(cp_files, start=1):
            # Extract old track number from filename (CP02.MKI -> 2)
            old_num = int(old_file.stem[2:])  # Remove 'CP' prefix

            if old_num == new_num:
                continue  # Already correct, skip

            new_filename = f"CP{new_num:02d}.MKI"

            if dry_run:
                print(f"  {old_file.name} → {new_filename}")
                log_message(log_file, f"  Would rename: {old_file.name} -> {new_filename}")
            else:
                # Process file: decipher, update tag, cipher back
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        temp_dir = Path(tmpdir)
                        temp_mp3 = temp_dir / f"temp_{new_num}.mp3"
                        temp_mki = temp_dir / new_filename

                        # Decipher .MKI to .mp3
                        decipher_file(old_file, temp_mp3)

                        # Update ID3 tag
                        update_id3_tag(temp_mp3, figure_id, new_num)

                        # Cipher back to .MKI
                        cipher_file(temp_mp3, temp_mki)

                        # Move to final location
                        new_path = folder / new_filename
                        shutil.move(str(temp_mki), str(new_path))

                        # Remove old file if different
                        if old_file.name != new_filename:
                            old_file.unlink()

                        print_colored(f"  ✓ {old_file.name} → {new_filename}", Colors.GREEN)
                        log_message(log_file, f"  Renamed: {old_file.name} -> {new_filename}")
                        renumbered_count += 1

                except Exception as e:
                    print_colored(f"  ✗ Errore con {old_file.name}: {e}", Colors.RED)
                    log_message(log_file, f"  Error: {old_file.name} - {e}")

        print()

    if not dry_run and renumbered_count > 0:
        print_colored("═" * 60, Colors.GREEN)
        print_colored(f"✓ Rinumerazione completata: {renumbered_count} file aggiornati", Colors.GREEN)
        print_colored("═" * 60, Colors.GREEN)
        print()

def analyze_cp01_files(faba_dir: Path) -> Tuple[List[Tuple[Path, int, str]], List[Tuple[Path, int, str]]]:
    """
    Analyze all CP01.MKI files in the directory.

    Returns:
        (ad_files, content_files) where each is a list of (path, size, folder_name) tuples
    """
    ad_files = []
    content_files = []

    for cp01 in faba_dir.glob('K*/CP01.MKI'):
        size = cp01.stat().st_size
        folder = cp01.parent.name

        if MIN_AD_SIZE <= size <= MAX_AD_SIZE:
            ad_files.append((cp01, size, folder))
        else:
            content_files.append((cp01, size, folder))

    return ad_files, content_files

def display_results(ad_files, content_files):
    """Display analysis results"""
    print()
    print_colored("═" * 60, Colors.YELLOW)
    print_colored("  RISULTATI ANALISI", Colors.YELLOW)
    print_colored("═" * 60, Colors.YELLOW)
    print()

    if ad_files:
        print_colored(f"🔴 PUBBLICITÀ IDENTIFICATE ({len(ad_files)} file):", Colors.RED)
        print_colored(f"   (Dimensione: {MIN_AD_SIZE}-{MAX_AD_SIZE} bytes / ~440-470KB)", Colors.RED)
        print()

        for path, size, folder in sorted(ad_files, key=lambda x: x[2]):
            size_kb = size / 1024
            print(f"  📢 {folder}/CP01.MKI ({size_kb:.1f}KB)")
        print()
    else:
        print_colored("✓ Nessuna pubblicità identificata", Colors.GREEN)
        print()

    if content_files:
        print_colored(f"✓ CONTENUTI DA PRESERVARE ({len(content_files)} file):", Colors.GREEN)
        print_colored("   (Dimensioni diverse, probabilmente contenuto vero)", Colors.GREEN)
        print()

        for path, size, folder in sorted(content_files, key=lambda x: x[2]):
            size_kb = size / 1024
            print(f"  🎵 {folder}/CP01.MKI ({size_kb:.1f}KB)")
        print()

    print_colored("═" * 60, Colors.YELLOW)
    print()

def dry_run_mode(with_renumber=False):
    """Display dry-run information"""
    print_colored("ℹ️  MODALITÀ DRY-RUN (simulazione)", Colors.BLUE)
    print("   Nessun file verrà modificato o cancellato.")
    print()
    if with_renumber:
        print("   Con --renumber: I file rimanenti verranno rinumerati")
        print("   (CP02→CP01, CP03→CP02, etc. con aggiornamento tag ID3)")
        print()
    print("Per procedere, usa:")
    print("  --backup           (sposta in backup, più sicuro)")
    print("  --delete           (cancella definitivamente)")
    print("  --backup --renumber (sposta e rinumera)")
    print("  --delete --renumber (cancella e rinumera)")

def backup_mode(ad_files, log_file, faba_dir=None, renumber=False):
    """Backup mode: move files to backup directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"faba_ads_backup_{timestamp}")

    print_colored("⚠️  MODALITÀ BACKUP", Colors.YELLOW)
    print(f"   I file CP01 pubblicitari verranno spostati in:")
    print(f"   {backup_dir}")
    if renumber:
        print()
        print_colored("   + RINUMERAZIONE ATTIVA", Colors.YELLOW)
        print("   I file rimanenti (CP02, CP03...) verranno rinumerati")
        print("   partendo da CP01 e i tag ID3 saranno aggiornati")
    print()

    confirm = input("Confermi? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operazione annullata.")
        return False, []

    backup_dir.mkdir(exist_ok=True)
    log_message(log_file, f"Backup directory: {backup_dir}")

    moved = 0
    affected_folders = []
    for path, size, folder in ad_files:
        folder_backup = backup_dir / folder
        folder_backup.mkdir(exist_ok=True)

        dest = folder_backup / path.name
        shutil.move(str(path), str(dest))

        print_colored(f"✓ Spostato: {folder}/CP01.MKI", Colors.GREEN)
        log_message(log_file, f"Moved: {path} -> {dest}")
        moved += 1
        affected_folders.append(folder)

    print()
    print_colored("═" * 60, Colors.GREEN)
    print_colored(f"✓ Completato! {moved} file spostati in backup", Colors.GREEN)
    print_colored(f"  Backup: {backup_dir}", Colors.GREEN)
    print_colored(f"  Log: {log_file}", Colors.GREEN)
    print_colored("═" * 60, Colors.GREEN)

    return True, affected_folders

def delete_mode(ad_files, log_file, faba_dir=None, renumber=False):
    """Delete mode: permanently delete files"""
    print_colored("⚠️⚠️⚠️  MODALITÀ DELETE - ATTENZIONE! ⚠️⚠️⚠️", Colors.RED)
    print_colored("   I file CP01 pubblicitari verranno CANCELLATI DEFINITIVAMENTE", Colors.RED)
    print()
    print(f"Questo cancellerà {len(ad_files)} file:")

    for path, size, folder in ad_files:
        print(f"  - {folder}/CP01.MKI")

    if renumber:
        print()
        print_colored("   + RINUMERAZIONE ATTIVA", Colors.YELLOW)
        print("   I file rimanenti (CP02, CP03...) verranno rinumerati")
        print("   partendo da CP01 e i tag ID3 saranno aggiornati")

    print()
    confirm = input("Sei ASSOLUTAMENTE SICURO? Digita 'DELETE' per confermare: ")
    if confirm != 'DELETE':
        print("Operazione annullata.")
        return False, []

    deleted = 0
    affected_folders = []
    for path, size, folder in ad_files:
        path.unlink()
        print_colored(f"✓ Cancellato: {folder}/CP01.MKI", Colors.RED)
        log_message(log_file, f"Deleted: {path}")
        deleted += 1
        affected_folders.append(folder)

    print()
    print_colored("═" * 60, Colors.RED)
    print_colored(f"Completato. {deleted} file cancellati definitivamente", Colors.RED)
    print_colored(f"Log: {log_file}", Colors.RED)
    print_colored("═" * 60, Colors.RED)

    return True, affected_folders

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: remove_ads.py <faba_directory> [--dry-run|--backup|--delete] [--renumber]")
        print()
        print("Modes:")
        print("  --dry-run    Mostra cosa verrebbe rimosso (default, sicuro)")
        print("  --backup     Sposta i file CP01 in backup invece di cancellarli")
        print("  --delete     ATTENZIONE: Cancella definitivamente i CP01 pubblicitari")
        print()
        print("Options:")
        print("  --renumber   Rinumera i file rimanenti (CP02→CP01, CP03→CP02, etc.)")
        print("               Aggiorna anche i tag ID3 per mantenere la compatibilità")
        print()
        print("Examples:")
        print("  ./remove_ads.py /mnt/faba/MKI01 --dry-run")
        print("  ./remove_ads.py /mnt/faba/MKI01 --backup")
        print("  ./remove_ads.py /mnt/faba/MKI01 --backup --renumber")
        print("  ./remove_ads.py /mnt/faba/MKI01 --delete --renumber")
        sys.exit(1)

    faba_dir = Path(sys.argv[1])

    # Parse arguments
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    mode = '--dry-run'  # default
    renumber = False

    for arg in args:
        if arg in ['--dry-run', '--backup', '--delete']:
            mode = arg
        elif arg == '--renumber':
            renumber = True
        else:
            print_colored(f"Errore: Argomento non valido '{arg}'", Colors.RED)
            sys.exit(1)

    if not faba_dir.is_dir():
        print_colored(f"Errore: Directory '{faba_dir}' non trovata", Colors.RED)
        sys.exit(1)

    # Check if mutagen is available for renumbering
    if renumber:
        try:
            import mutagen
            from mutagen.id3 import ID3, TIT2
            from mutagen.mp3 import MP3
        except ImportError:
            print_colored("Errore: Il modulo 'mutagen' è richiesto per --renumber", Colors.RED)
            print("Installa con: pip install mutagen")
            sys.exit(1)

    # Setup log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"remove_ads_log_{timestamp}.txt"

    # Header
    print_colored("╔════════════════════════════════════════════════════════╗", Colors.BLUE)
    print_colored("║  Faba Advertisement Remover - Analisi in corso...     ║", Colors.BLUE)
    print_colored("╚════════════════════════════════════════════════════════╝", Colors.BLUE)
    print()

    log_message(log_file, f"=== Analisi avviata: {datetime.now()} ===")
    log_message(log_file, f"Directory: {faba_dir}")
    log_message(log_file, f"Mode: {mode}")
    log_message(log_file, f"Renumber: {renumber}")
    log_message(log_file, "")

    # Analyze
    ad_files, content_files = analyze_cp01_files(faba_dir)

    print_colored("✓ Analisi completata", Colors.GREEN)

    # Display results
    display_results(ad_files, content_files)

    # Exit if no ads found
    if not ad_files:
        log_message(log_file, "Nessuna operazione necessaria.")
        print_colored("Nessuna pubblicità da rimuovere. Tutto OK!", Colors.GREEN)
        sys.exit(0)

    # Execute based on mode
    affected_folders = []
    operation_success = False

    if mode == '--dry-run':
        dry_run_mode(with_renumber=renumber)
        log_message(log_file, "Dry-run completato. Nessuna modifica effettuata.")

        # Show renumbering preview if requested
        if renumber:
            affected_folders = [folder for _, _, folder in ad_files]
            renumber_tracks(faba_dir, affected_folders, log_file, dry_run=True)
        operation_success = True

    elif mode == '--backup':
        operation_success, affected_folders = backup_mode(ad_files, log_file, faba_dir, renumber)

    elif mode == '--delete':
        operation_success, affected_folders = delete_mode(ad_files, log_file, faba_dir, renumber)

    else:
        print_colored(f"Errore: Modalità non valida '{mode}'", Colors.RED)
        sys.exit(1)

    # Perform renumbering if requested and operation was successful
    if renumber and operation_success and affected_folders and mode != '--dry-run':
        renumber_tracks(faba_dir, affected_folders, log_file, dry_run=False)

    log_message(log_file, f"=== Operazione completata: {datetime.now()} ===")

if __name__ == "__main__":
    main()
