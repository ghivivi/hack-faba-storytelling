#!/usr/bin/env python3
"""
remove_ads.py - Faba Advertisement Remover

Rimuove in modo sicuro i file CP01.MKI pubblicitari dalle cartelle Faba.

SICUREZZA:
- Identifica pubblicita basandosi sulla dimensione (440-470KB)
- Mostra anteprima prima di procedere
- Chiede conferma
- Crea backup prima di cancellare
- Log dettagliato delle operazioni

Usage:
  # Linux/macOS
  python3 remove_ads.py /mnt/faba/MKI01 [--dry-run|--backup|--delete] [--renumber]

  # Windows (Faba montato come E:)
  python remove_ads.py E:/MKI01 [--dry-run|--backup|--delete] [--renumber]
"""

import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from faba_utils import Colors, print_colored

from cipher import encrypt_file, decrypt_file

MIN_AD_SIZE = 440000
MAX_AD_SIZE = 470000


def log_message(log_file, message):
    print(message)
    with open(log_file, 'a') as f:
        f.write(re.sub(r'\033\[[0-9;]+m', '', message) + '\n')


def update_id3_tag(mp3_path: Path, figure_id: str, track_num: int):
    try:
        from mutagen.id3 import ID3, TIT2
        from mutagen.mp3 import MP3
        tags = MP3(str(mp3_path), ID3=ID3)
        tags.delete()
        tags["TIT2"] = TIT2(encoding=3, text=f"K{figure_id}CP{track_num:02d}")
        tags.save()
    except Exception as e:
        print_colored(f"Attenzione: Could not update ID3 tag for {mp3_path.name}: {e}", Colors.YELLOW)


def renumber_tracks(faba_dir: Path, affected_folders: List[str], log_file, dry_run=False):
    if not affected_folders:
        return

    print()
    print_colored("RINUMERAZIONE TRACCE", Colors.BLUE)
    print()

    if dry_run:
        print_colored("Modalita simulazione - mostra solo cosa verrebbe rinumerato", Colors.BLUE)
        print()

    renumbered_count = 0

    for folder_name in sorted(affected_folders):
        folder = faba_dir / folder_name
        cp_files = sorted([f for f in folder.glob('CP*.MKI') if f.name != 'CP01.MKI'])

        if not cp_files:
            continue

        print_colored(f"{folder_name}:", Colors.BOLD)
        log_message(log_file, f"Renumbering folder: {folder_name}")
        figure_id = folder_name[1:]

        for new_num, old_file in enumerate(cp_files, start=1):
            old_num = int(old_file.stem[2:])
            if old_num == new_num:
                continue

            new_filename = f"CP{new_num:02d}.MKI"

            if dry_run:
                print(f"  {old_file.name} -> {new_filename}")
                log_message(log_file, f"  Would rename: {old_file.name} -> {new_filename}")
            else:
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        temp_mp3 = Path(tmpdir) / f"temp_{new_num}.mp3"
                        decrypt_file(str(old_file), str(temp_mp3))
                        update_id3_tag(temp_mp3, figure_id, new_num)
                        encrypt_file(str(temp_mp3))
                        shutil.move(str(temp_mp3) + ".MKI", str(folder / new_filename))
                        old_file.unlink()
                    print_colored(f"  {old_file.name} -> {new_filename}", Colors.GREEN)
                    log_message(log_file, f"  Renamed: {old_file.name} -> {new_filename}")
                    renumbered_count += 1
                except Exception as e:
                    print_colored(f"  Errore con {old_file.name}: {e}", Colors.RED)
                    log_message(log_file, f"  Error: {old_file.name} - {e}")

        print()

    if not dry_run and renumbered_count > 0:
        print_colored(f"Rinumerazione completata: {renumbered_count} file aggiornati", Colors.GREEN)
        print()


def analyze_cp01_files(faba_dir: Path) -> Tuple[List, List]:
    ad_files, content_files = [], []
    for cp01 in faba_dir.glob('K*/CP01.MKI'):
        size = cp01.stat().st_size
        folder = cp01.parent.name
        if MIN_AD_SIZE <= size <= MAX_AD_SIZE:
            ad_files.append((cp01, size, folder))
        else:
            content_files.append((cp01, size, folder))
    return ad_files, content_files


def display_results(ad_files, content_files):
    print()
    print_colored("RISULTATI ANALISI", Colors.YELLOW)
    print()

    if ad_files:
        print_colored(f"PUBBLICITA IDENTIFICATE ({len(ad_files)} file):", Colors.RED)
        print_colored(f"   (Dimensione: {MIN_AD_SIZE}-{MAX_AD_SIZE} bytes / ~440-470KB)", Colors.RED)
        print()
        for path, size, folder in sorted(ad_files, key=lambda x: x[2]):
            print(f"  {folder}/CP01.MKI ({size / 1024:.1f}KB)")
        print()
    else:
        print_colored("Nessuna pubblicita identificata", Colors.GREEN)
        print()

    if content_files:
        print_colored(f"CONTENUTI DA PRESERVARE ({len(content_files)} file):", Colors.GREEN)
        print()
        for path, size, folder in sorted(content_files, key=lambda x: x[2]):
            print(f"  {folder}/CP01.MKI ({size / 1024:.1f}KB)")
        print()


def backup_mode(ad_files, log_file, renumber=False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"faba_ads_backup_{timestamp}")

    print_colored("MODALITA BACKUP", Colors.YELLOW)
    print(f"   I file CP01 pubblicitari verranno spostati in: {backup_dir}")
    if renumber:
        print_colored("   + RINUMERAZIONE ATTIVA", Colors.YELLOW)
    print()

    if input("Confermi? (yes/no): ").lower() != 'yes':
        print("Operazione annullata.")
        return False, []

    backup_dir.mkdir(exist_ok=True)
    log_message(log_file, f"Backup directory: {backup_dir}")

    affected_folders = []
    for path, size, folder in ad_files:
        folder_backup = backup_dir / folder
        folder_backup.mkdir(exist_ok=True)
        shutil.move(str(path), str(folder_backup / path.name))
        print_colored(f"Spostato: {folder}/CP01.MKI", Colors.GREEN)
        log_message(log_file, f"Moved: {path} -> {folder_backup / path.name}")
        affected_folders.append(folder)

    print()
    print_colored(f"Completato! {len(ad_files)} file spostati in {backup_dir}", Colors.GREEN)
    return True, affected_folders


def delete_mode(ad_files, log_file, renumber=False):
    print_colored("MODALITA DELETE - ATTENZIONE!", Colors.RED)
    print_colored("   I file CP01 pubblicitari verranno CANCELLATI DEFINITIVAMENTE", Colors.RED)
    print()
    print(f"Questo cancellera {len(ad_files)} file:")
    for path, size, folder in ad_files:
        print(f"  - {folder}/CP01.MKI")
    if renumber:
        print_colored("   + RINUMERAZIONE ATTIVA", Colors.YELLOW)
    print()

    if input("Sei ASSOLUTAMENTE SICURO? Digita 'DELETE' per confermare: ") != 'DELETE':
        print("Operazione annullata.")
        return False, []

    affected_folders = []
    for path, size, folder in ad_files:
        path.unlink()
        print_colored(f"Cancellato: {folder}/CP01.MKI", Colors.RED)
        log_message(log_file, f"Deleted: {path}")
        affected_folders.append(folder)

    print()
    print_colored(f"Completato. {len(ad_files)} file cancellati definitivamente", Colors.RED)
    return True, affected_folders


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 remove_ads.py <faba_directory> [--dry-run|--backup|--delete] [--renumber]")
        print()
        print("Modes:")
        print("  --dry-run    Mostra cosa verrebbe rimosso (default, sicuro)")
        print("  --backup     Sposta i file CP01 in backup invece di cancellarli")
        print("  --delete     ATTENZIONE: Cancella definitivamente i CP01 pubblicitari")
        print()
        print("Options:")
        print("  --renumber   Rinumera i file rimanenti (CP02->CP01, CP03->CP02, etc.)")
        print()
        print("Esempi:")
        print("  # Linux/macOS")
        print("  python3 remove_ads.py /mnt/faba/MKI01 --dry-run")
        print("  python3 remove_ads.py /mnt/faba/MKI01 --backup --renumber")
        print()
        print("  # Windows")
        print("  python remove_ads.py E:\\MKI01 --backup")
        sys.exit(1)

    faba_dir = Path(sys.argv[1])
    args = sys.argv[2:]
    mode = '--dry-run'
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

    if renumber:
        try:
            import mutagen
        except ImportError:
            print_colored("Errore: Il modulo 'mutagen' e richiesto per --renumber", Colors.RED)
            print("Installa con: pip install mutagen")
            sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"remove_ads_log_{timestamp}.txt"

    print_colored("Faba Advertisement Remover - Analisi in corso...", Colors.BLUE)
    print()

    log_message(log_file, f"=== Analisi avviata: {datetime.now()} ===")
    log_message(log_file, f"Directory: {faba_dir}")
    log_message(log_file, f"Mode: {mode}, Renumber: {renumber}")
    log_message(log_file, "")

    ad_files, content_files = analyze_cp01_files(faba_dir)
    print_colored("Analisi completata", Colors.GREEN)
    display_results(ad_files, content_files)

    if not ad_files:
        log_message(log_file, "Nessuna operazione necessaria.")
        print_colored("Nessuna pubblicita da rimuovere. Tutto OK!", Colors.GREEN)
        sys.exit(0)

    affected_folders = []
    operation_success = False

    if mode == '--dry-run':
        print_colored("MODALITA DRY-RUN (simulazione) - nessun file verra modificato.", Colors.BLUE)
        print()
        print("Per procedere, usa:  --backup  oppure  --delete")
        if renumber:
            affected_folders = [folder for _, _, folder in ad_files]
            renumber_tracks(faba_dir, affected_folders, log_file, dry_run=True)
        operation_success = True

    elif mode == '--backup':
        operation_success, affected_folders = backup_mode(ad_files, log_file, renumber)

    elif mode == '--delete':
        operation_success, affected_folders = delete_mode(ad_files, log_file, renumber)

    if renumber and operation_success and affected_folders and mode != '--dry-run':
        renumber_tracks(faba_dir, affected_folders, log_file, dry_run=False)

    log_message(log_file, f"=== Operazione completata: {datetime.now()} ===")


if __name__ == "__main__":
    main()
