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

Usage: ./remove_ads.py <faba_directory> [--dry-run|--backup|--delete]
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Configuration
MIN_AD_SIZE = 440000  # 440KB
MAX_AD_SIZE = 470000  # 470KB

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

def dry_run_mode():
    """Display dry-run information"""
    print_colored("ℹ️  MODALITÀ DRY-RUN (simulazione)", Colors.BLUE)
    print("   Nessun file verrà modificato o cancellato.")
    print()
    print("Per procedere, usa:")
    print("  --backup  (sposta in backup, più sicuro)")
    print("  --delete  (cancella definitivamente)")

def backup_mode(ad_files, log_file):
    """Backup mode: move files to backup directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"faba_ads_backup_{timestamp}")

    print_colored("⚠️  MODALITÀ BACKUP", Colors.YELLOW)
    print(f"   I file CP01 pubblicitari verranno spostati in:")
    print(f"   {backup_dir}")
    print()

    confirm = input("Confermi? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operazione annullata.")
        return False

    backup_dir.mkdir(exist_ok=True)
    log_message(log_file, f"Backup directory: {backup_dir}")

    moved = 0
    for path, size, folder in ad_files:
        folder_backup = backup_dir / folder
        folder_backup.mkdir(exist_ok=True)

        dest = folder_backup / path.name
        shutil.move(str(path), str(dest))

        print_colored(f"✓ Spostato: {folder}/CP01.MKI", Colors.GREEN)
        log_message(log_file, f"Moved: {path} -> {dest}")
        moved += 1

    print()
    print_colored("═" * 60, Colors.GREEN)
    print_colored(f"✓ Completato! {moved} file spostati in backup", Colors.GREEN)
    print_colored(f"  Backup: {backup_dir}", Colors.GREEN)
    print_colored(f"  Log: {log_file}", Colors.GREEN)
    print_colored("═" * 60, Colors.GREEN)

    return True

def delete_mode(ad_files, log_file):
    """Delete mode: permanently delete files"""
    print_colored("⚠️⚠️⚠️  MODALITÀ DELETE - ATTENZIONE! ⚠️⚠️⚠️", Colors.RED)
    print_colored("   I file CP01 pubblicitari verranno CANCELLATI DEFINITIVAMENTE", Colors.RED)
    print()
    print(f"Questo cancellerà {len(ad_files)} file:")

    for path, size, folder in ad_files:
        print(f"  - {folder}/CP01.MKI")

    print()
    confirm = input("Sei ASSOLUTAMENTE SICURO? Digita 'DELETE' per confermare: ")
    if confirm != 'DELETE':
        print("Operazione annullata.")
        return False

    deleted = 0
    for path, size, folder in ad_files:
        path.unlink()
        print_colored(f"✓ Cancellato: {folder}/CP01.MKI", Colors.RED)
        log_message(log_file, f"Deleted: {path}")
        deleted += 1

    print()
    print_colored("═" * 60, Colors.RED)
    print_colored(f"Completato. {deleted} file cancellati definitivamente", Colors.RED)
    print_colored(f"Log: {log_file}", Colors.RED)
    print_colored("═" * 60, Colors.RED)

    return True

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: remove_ads.py <faba_directory> [--dry-run|--backup|--delete]")
        print()
        print("Modes:")
        print("  --dry-run    Mostra cosa verrebbe rimosso (default, sicuro)")
        print("  --backup     Sposta i file CP01 in backup invece di cancellarli")
        print("  --delete     ATTENZIONE: Cancella definitivamente i CP01 pubblicitari")
        print()
        print("Example:")
        print("  ./remove_ads.py /mnt/faba/MKI01 --dry-run")
        print("  ./remove_ads.py /mnt/faba/MKI01 --backup")
        sys.exit(1)

    faba_dir = Path(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else '--dry-run'

    if not faba_dir.is_dir():
        print_colored(f"Errore: Directory '{faba_dir}' non trovata", Colors.RED)
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
    if mode == '--dry-run':
        dry_run_mode()
        log_message(log_file, "Dry-run completato. Nessuna modifica effettuata.")
    elif mode == '--backup':
        backup_mode(ad_files, log_file)
    elif mode == '--delete':
        delete_mode(ad_files, log_file)
    else:
        print_colored(f"Errore: Modalità non valida '{mode}'", Colors.RED)
        sys.exit(1)

    log_message(log_file, f"=== Operazione completata: {datetime.now()} ===")

if __name__ == "__main__":
    main()
