#!/usr/bin/env python3
"""
sync_from_drive.py - Faba Google Drive Sync

Sincronizza MP3 da Google Drive e li aggiunge al Faba.

Workflow:
1. Mostra file disponibili su Google Drive
2. Scarica i file selezionati
3. Li processa automaticamente con add_tracks.py
4. Sposta i file processati in "completed" su Drive

Requisiti:
- rclone installato e configurato
- mutagen (pip install mutagen)

Usage:
  # Prima configurazione (solo una volta)
  ./sync_from_drive.py --setup

  # Lista file disponibili su Drive
  ./sync_from_drive.py --list

  # Scarica e processa tutti i nuovi file
  ./sync_from_drive.py --sync-all

  # Scarica e processa file specifici
  ./sync_from_drive.py --sync file1.mp3 file2.mp3
"""

import os
import sys
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

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

def check_rclone_installed():
    """Check if rclone is installed"""
    try:
        result = subprocess.run(['rclone', 'version'],
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def check_rclone_configured(remote_name='gdrive'):
    """Check if rclone remote is configured"""
    try:
        result = subprocess.run(['rclone', 'listremotes'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            remotes = result.stdout.strip().split('\n')
            return f"{remote_name}:" in remotes
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def setup_rclone():
    """Guide user through rclone setup"""
    print_colored("╔════════════════════════════════════════════════════════╗", Colors.BLUE)
    print_colored("║  Setup Google Drive con rclone                         ║", Colors.BLUE)
    print_colored("╚════════════════════════════════════════════════════════╝", Colors.BLUE)
    print()

    # Check if rclone is installed
    if not check_rclone_installed():
        print_colored("❌ rclone non è installato", Colors.RED)
        print()
        print("Installazione:")
        print()
        print("  Linux/macOS:")
        print("    curl https://rclone.org/install.sh | sudo bash")
        print()
        print("  Windows:")
        print("    Scarica da: https://rclone.org/downloads/")
        print()
        sys.exit(1)

    print_colored("✓ rclone è installato", Colors.GREEN)
    print()

    # Check if already configured
    if check_rclone_configured():
        print_colored("✓ Remote 'gdrive' già configurato", Colors.GREEN)
        print()
        print("Se vuoi riconfigurare, usa:")
        print("  rclone config")
        print()
        return

    # Guide through configuration
    print_colored("Configurazione Google Drive:", Colors.YELLOW)
    print()
    print("Segui questi passaggi:")
    print()
    print("1. Esegui: rclone config")
    print("2. Seleziona: n (New remote)")
    print("3. Nome: gdrive")
    print("4. Storage type: drive (Google Drive)")
    print("5. Client ID/Secret: premi Invio (usa default)")
    print("6. Scope: 1 (Full access)")
    print("7. Root folder: premi Invio")
    print("8. Service account: premi Invio")
    print("9. Auto config: y (Yes)")
    print("10. Si aprirà il browser per autenticarti con Google")
    print("11. Shared drive: premi Invio")
    print("12. Conferma: y (Yes)")
    print()

    confirm = input("Vuoi eseguire 'rclone config' ora? (yes/no): ")
    if confirm.lower() == 'yes':
        subprocess.run(['rclone', 'config'])
    else:
        print()
        print("Esegui manualmente:")
        print("  rclone config")
        print()

def list_remote_files(remote_path='gdrive:Faba/incoming', pattern='*.mp3'):
    """List files in remote directory"""
    try:
        # Use rclone lsjson for better parsing
        result = subprocess.run(
            ['rclone', 'lsjson', remote_path],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            raise Exception(f"rclone error: {result.stderr}")

        files = json.loads(result.stdout)

        # Filter MP3 files
        mp3_files = [
            f for f in files
            if f['Name'].lower().endswith('.mp3') and not f['IsDir']
        ]

        return mp3_files

    except json.JSONDecodeError as e:
        raise Exception(f"Errore parsing JSON da rclone: {e}")
    except subprocess.TimeoutExpired:
        raise Exception("Timeout durante la connessione a Google Drive")
    except Exception as e:
        raise Exception(f"Errore listing files: {e}")

def download_file(remote_path, local_path):
    """Download a file from remote"""
    try:
        result = subprocess.run(
            ['rclone', 'copy', remote_path, str(local_path)],
            capture_output=True, text=True, timeout=300
        )

        if result.returncode != 0:
            raise Exception(f"rclone error: {result.stderr}")

        return True

    except subprocess.TimeoutExpired:
        raise Exception("Timeout durante il download")
    except Exception as e:
        raise Exception(f"Errore download: {e}")

def move_remote_file(remote_source, remote_dest):
    """Move a file on remote storage"""
    try:
        result = subprocess.run(
            ['rclone', 'moveto', remote_source, remote_dest],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            raise Exception(f"rclone error: {result.stderr}")

        return True

    except subprocess.TimeoutExpired:
        raise Exception("Timeout durante lo spostamento file")
    except Exception as e:
        raise Exception(f"Errore spostamento: {e}")

def process_files_with_add_tracks(faba_dir: Path, mp3_files: List[Path],
                                  custom_prefix: Optional[str] = None):
    """Process MP3 files with add_tracks.py"""

    # Import add_tracks functions
    sys.path.insert(0, str(Path(__file__).parent))
    from add_tracks import create_new_figure

    print()
    print_colored("═" * 60, Colors.CYAN)
    print_colored("  PROCESSAMENTO FILE", Colors.CYAN)
    print_colored("═" * 60, Colors.CYAN)
    print()

    # Ask user what to do
    print("Come vuoi processare questi file?")
    print()
    print("1. Crea nuova figura con tutti i file")
    print("2. Crea una figura per ogni file")
    print("3. Annulla")
    print()

    choice = input("Scelta (1-3): ")

    if choice == '1':
        # Create single figure with all files
        try:
            figure_id = create_new_figure(faba_dir, mp3_files,
                                         custom_prefix=custom_prefix)
            if figure_id:
                print()
                print_colored(f"✓ Figura K{figure_id} creata con successo!", Colors.GREEN)
                return True
        except Exception as e:
            print_colored(f"❌ Errore: {e}", Colors.RED)
            return False

    elif choice == '2':
        # Create separate figure for each file
        success_count = 0
        for mp3_file in mp3_files:
            try:
                figure_id = create_new_figure(faba_dir, [mp3_file],
                                             custom_prefix=custom_prefix)
                if figure_id:
                    success_count += 1
            except Exception as e:
                print_colored(f"❌ Errore con {mp3_file.name}: {e}", Colors.RED)

        print()
        print_colored(f"✓ {success_count}/{len(mp3_files)} figure create", Colors.GREEN)
        return success_count > 0

    else:
        print("Operazione annullata")
        return False

def sync_all(faba_dir: Path, remote_base='gdrive:Faba', custom_prefix: Optional[str] = None):
    """Sync all files from remote"""

    remote_incoming = f"{remote_base}/incoming"
    remote_processed = f"{remote_base}/processed"

    print_colored("╔════════════════════════════════════════════════════════╗", Colors.BLUE)
    print_colored("║  Sincronizzazione da Google Drive                      ║", Colors.BLUE)
    print_colored("╚════════════════════════════════════════════════════════╝", Colors.BLUE)
    print()

    # List available files
    print_colored("📂 Scansione Google Drive...", Colors.BLUE)
    try:
        files = list_remote_files(remote_incoming)
    except Exception as e:
        print_colored(f"❌ Errore: {e}", Colors.RED)
        print()
        print("Suggerimenti:")
        print("- Verifica che la cartella 'Faba/incoming' esista su Google Drive")
        print("- Controlla la configurazione rclone: rclone config")
        print("- Testa la connessione: rclone ls gdrive:")
        return

    if not files:
        print_colored("✓ Nessun nuovo file da processare", Colors.GREEN)
        return

    print()
    print_colored(f"📁 Trovati {len(files)} file:", Colors.GREEN)
    print()

    total_size = 0
    for f in files:
        size_mb = f['Size'] / (1024 * 1024)
        total_size += f['Size']
        print(f"  • {f['Name']} ({size_mb:.2f} MB)")

    print()
    print(f"Dimensione totale: {total_size / (1024 * 1024):.2f} MB")
    print()

    confirm = input("Procedere con il download e processamento? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operazione annullata")
        return

    # Download files to temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        downloaded_files = []

        print()
        print_colored("⬇️  Download in corso...", Colors.BLUE)

        for file_info in files:
            filename = file_info['Name']
            remote_file = f"{remote_incoming}/{filename}"

            try:
                print(f"  Downloading {filename}...", end=' ')
                download_file(remote_file, temp_dir)

                local_file = temp_dir / filename
                if local_file.exists():
                    downloaded_files.append(local_file)
                    print_colored("✓", Colors.GREEN)
                else:
                    print_colored("✗", Colors.RED)

            except Exception as e:
                print_colored(f"✗ Errore: {e}", Colors.RED)

        if not downloaded_files:
            print_colored("❌ Nessun file scaricato con successo", Colors.RED)
            return

        print()
        print_colored(f"✓ {len(downloaded_files)} file scaricati", Colors.GREEN)

        # Process files
        success = process_files_with_add_tracks(faba_dir, downloaded_files, custom_prefix)

        if success:
            # Move processed files to completed folder
            print()
            print_colored("📦 Spostamento file processati...", Colors.BLUE)

            for file_info in files:
                filename = file_info['Name']
                remote_source = f"{remote_incoming}/{filename}"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                remote_dest = f"{remote_processed}/{timestamp}_{filename}"

                try:
                    move_remote_file(remote_source, remote_dest)
                    print_colored(f"  ✓ {filename} → processed/", Colors.GREEN)
                except Exception as e:
                    print_colored(f"  ⚠️  Impossibile spostare {filename}: {e}", Colors.YELLOW)

            print()
            print_colored("═" * 60, Colors.GREEN)
            print_colored("✓ Sincronizzazione completata!", Colors.GREEN)
            print_colored("═" * 60, Colors.GREEN)

def list_command(remote_base='gdrive:Faba'):
    """List available files on remote"""
    remote_incoming = f"{remote_base}/incoming"

    print_colored("╔════════════════════════════════════════════════════════╗", Colors.BLUE)
    print_colored("║  File disponibili su Google Drive                      ║", Colors.BLUE)
    print_colored("╚════════════════════════════════════════════════════════╝", Colors.BLUE)
    print()

    try:
        files = list_remote_files(remote_incoming)
    except Exception as e:
        print_colored(f"❌ Errore: {e}", Colors.RED)
        return

    if not files:
        print_colored("Nessun file MP3 trovato in Faba/incoming", Colors.YELLOW)
        return

    print_colored(f"📁 {len(files)} file trovati:", Colors.GREEN)
    print()

    for f in files:
        size_mb = f['Size'] / (1024 * 1024)
        mod_time = f['ModTime']
        print(f"  • {f['Name']}")
        print(f"    Dimensione: {size_mb:.2f} MB")
        print(f"    Modificato: {mod_time}")
        print()

def show_usage():
    """Display usage information"""
    print("Usage: sync_from_drive.py [command] [options]")
    print()
    print("Commands:")
    print("  --setup           Configura rclone per Google Drive (prima volta)")
    print("  --list            Mostra file disponibili su Google Drive")
    print("  --sync-all        Scarica e processa tutti i file disponibili")
    print()
    print("Options:")
    print("  --faba-dir DIR    Percorso al disco Faba (default: /mnt/faba/MKI01)")
    print("  --remote PATH     Percorso remoto base (default: gdrive:Faba)")
    print("  --prefix X        Prefisso ID per nuove figure (default: 9)")
    print()
    print("Esempi:")
    print("  # Prima configurazione")
    print("  ./sync_from_drive.py --setup")
    print()
    print("  # Lista file disponibili")
    print("  ./sync_from_drive.py --list")
    print()
    print("  # Sincronizza tutto")
    print("  ./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01")
    print()
    print("Struttura cartelle richiesta su Google Drive:")
    print("  Faba/")
    print("    ├── incoming/      (carica qui i nuovi MP3)")
    print("    └── processed/     (file processati verranno spostati qui)")

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    # Parse arguments
    command = sys.argv[1]
    faba_dir = Path('/mnt/faba/MKI01')
    remote_base = 'gdrive:Faba'
    custom_prefix = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--faba-dir':
            if i + 1 >= len(sys.argv):
                print_colored("Errore: --faba-dir richiede un percorso", Colors.RED)
                sys.exit(1)
            faba_dir = Path(sys.argv[i + 1])
            i += 2
        elif arg == '--remote':
            if i + 1 >= len(sys.argv):
                print_colored("Errore: --remote richiede un percorso", Colors.RED)
                sys.exit(1)
            remote_base = sys.argv[i + 1]
            i += 2
        elif arg == '--prefix':
            if i + 1 >= len(sys.argv):
                print_colored("Errore: --prefix richiede un valore", Colors.RED)
                sys.exit(1)
            custom_prefix = sys.argv[i + 1]
            i += 2
        else:
            print_colored(f"Errore: Argomento sconosciuto '{arg}'", Colors.RED)
            sys.exit(1)

    # Execute command
    try:
        if command == '--setup':
            setup_rclone()

        elif command == '--list':
            if not check_rclone_configured():
                print_colored("❌ rclone non configurato", Colors.RED)
                print("Esegui prima: ./sync_from_drive.py --setup")
                sys.exit(1)
            list_command(remote_base)

        elif command == '--sync-all':
            if not check_rclone_configured():
                print_colored("❌ rclone non configurato", Colors.RED)
                print("Esegui prima: ./sync_from_drive.py --setup")
                sys.exit(1)

            if not faba_dir.exists():
                print_colored(f"❌ Directory Faba non trovata: {faba_dir}", Colors.RED)
                sys.exit(1)

            sync_all(faba_dir, remote_base, custom_prefix)

        else:
            print_colored(f"Errore: Comando non valido '{command}'", Colors.RED)
            print()
            show_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print_colored("Operazione interrotta dall'utente", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print()
        print_colored(f"❌ Errore: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
