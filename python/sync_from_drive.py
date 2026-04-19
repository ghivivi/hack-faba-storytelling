#!/usr/bin/env python3
"""
sync_from_drive.py - Faba Google Drive Sync

Sincronizza MP3 da Google Drive e li aggiunge al Faba.

Workflow:
1. Mostra file disponibili su Google Drive
2. Scarica i file selezionati
3. Li processa automaticamente con add_tracks.py
4. Sposta i file processati in "processed" su Drive

Requisiti:
- rclone installato e configurato (https://rclone.org/downloads/)
- pip install mutagen colorama

Usage:
  # Prima configurazione (solo una volta)
  python3 sync_from_drive.py --setup

  # Lista file disponibili su Drive
  python3 sync_from_drive.py --list

  # Scarica e processa tutti i nuovi file
  # Linux/macOS:
  python3 sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01
  # Windows:
  python sync_from_drive.py --sync-all --faba-dir E:/MKI01
"""

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from faba_utils import Colors, print_colored


def check_rclone_installed():
    try:
        result = subprocess.run(['rclone', 'version'],
                                capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_rclone_configured(remote_name='gdrive'):
    try:
        result = subprocess.run(['rclone', 'listremotes'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return f"{remote_name}:" in result.stdout.strip().split('\n')
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def setup_rclone():
    print_colored("Setup Google Drive con rclone", Colors.BLUE)
    print()

    if not check_rclone_installed():
        print_colored("rclone non e installato", Colors.RED)
        print()
        print("Installazione:")
        print("  Linux/macOS:  curl https://rclone.org/install.sh | sudo bash")
        print("  Windows:      scarica da https://rclone.org/downloads/")
        print()
        sys.exit(1)

    print_colored("rclone e installato", Colors.GREEN)
    print()

    if check_rclone_configured():
        print_colored("Remote 'gdrive' gia configurato", Colors.GREEN)
        print()
        print("Per riconfigurare: rclone config")
        return

    print_colored("Configurazione Google Drive:", Colors.YELLOW)
    print()
    print("Segui questi passaggi:")
    print("1. Esegui: rclone config")
    print("2. Seleziona: n (New remote)")
    print("3. Nome: gdrive")
    print("4. Storage type: drive (Google Drive)")
    print("5. Client ID/Secret: premi Invio (usa default)")
    print("6. Scope: 1 (Full access)")
    print("7. Root folder: premi Invio")
    print("8. Service account: premi Invio")
    print("9. Auto config: y (Yes) - si apre il browser per autenticarsi")
    print("10. Shared drive: premi Invio")
    print("11. Conferma: y (Yes)")
    print()

    if input("Vuoi eseguire 'rclone config' ora? (yes/no): ").lower() == 'yes':
        subprocess.run(['rclone', 'config'])
    else:
        print("\nEsegui manualmente: rclone config")


def list_remote_files(remote_path='gdrive:Faba/incoming'):
    try:
        result = subprocess.run(
            ['rclone', 'lsjson', remote_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise Exception(f"rclone error: {result.stderr}")
        files = json.loads(result.stdout)
        return [f for f in files if f['Name'].lower().endswith('.mp3') and not f['IsDir']]
    except json.JSONDecodeError as e:
        raise Exception(f"Errore parsing risposta rclone: {e}")
    except subprocess.TimeoutExpired:
        raise Exception("Timeout durante la connessione a Google Drive")
    except Exception as e:
        raise Exception(f"Errore listing files: {e}")


def download_file(remote_path, local_dir):
    try:
        result = subprocess.run(
            ['rclone', 'copy', remote_path, str(local_dir)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            raise Exception(f"rclone error: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception("Timeout durante il download")


def move_remote_file(remote_source, remote_dest):
    try:
        result = subprocess.run(
            ['rclone', 'moveto', remote_source, remote_dest],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise Exception(f"rclone error: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception("Timeout durante lo spostamento file")


def process_files_with_add_tracks(faba_dir: Path, mp3_files: List[Path],
                                  custom_prefix: Optional[str] = None):
    from add_tracks import create_new_figure

    print()
    print_colored("PROCESSAMENTO FILE", Colors.CYAN)
    print()
    print("Come vuoi processare questi file?")
    print()
    print("1. Crea nuova figura con tutti i file")
    print("2. Crea una figura per ogni file")
    print("3. Annulla")
    print()

    choice = input("Scelta (1-3): ")

    if choice == '1':
        try:
            figure_id = create_new_figure(faba_dir, mp3_files, custom_prefix=custom_prefix)
            if figure_id:
                print_colored(f"Figura K{figure_id} creata con successo!", Colors.GREEN)
                return True
        except Exception as e:
            print_colored(f"Errore: {e}", Colors.RED)
        return False

    elif choice == '2':
        success_count = 0
        for mp3_file in mp3_files:
            try:
                figure_id = create_new_figure(faba_dir, [mp3_file], custom_prefix=custom_prefix)
                if figure_id:
                    success_count += 1
            except Exception as e:
                print_colored(f"Errore con {mp3_file.name}: {e}", Colors.RED)
        print_colored(f"{success_count}/{len(mp3_files)} figure create", Colors.GREEN)
        return success_count > 0

    else:
        print("Operazione annullata")
        return False


def sync_all(faba_dir: Path, remote_base='gdrive:Faba', custom_prefix: Optional[str] = None):
    remote_incoming = f"{remote_base}/incoming"
    remote_processed = f"{remote_base}/processed"

    print_colored("Sincronizzazione da Google Drive", Colors.BLUE)
    print()

    print_colored("Scansione Google Drive...", Colors.BLUE)
    try:
        files = list_remote_files(remote_incoming)
    except Exception as e:
        print_colored(f"Errore: {e}", Colors.RED)
        print()
        print("Suggerimenti:")
        print("- Verifica che la cartella 'Faba/incoming' esista su Google Drive")
        print("- Controlla la configurazione rclone: rclone config")
        print("- Testa la connessione: rclone ls gdrive:")
        return

    if not files:
        print_colored("Nessun nuovo file da processare", Colors.GREEN)
        return

    print()
    print_colored(f"Trovati {len(files)} file:", Colors.GREEN)
    print()

    total_size = 0
    for f in files:
        size_mb = f['Size'] / (1024 * 1024)
        total_size += f['Size']
        print(f"  - {f['Name']} ({size_mb:.2f} MB)")

    print()
    print(f"Dimensione totale: {total_size / (1024 * 1024):.2f} MB")
    print()

    if input("Procedere con il download e processamento? (yes/no): ").lower() != 'yes':
        print("Operazione annullata")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        downloaded_files = []

        print()
        print_colored("Download in corso...", Colors.BLUE)

        for file_info in files:
            filename = file_info['Name']
            remote_file = f"{remote_incoming}/{filename}"
            try:
                print(f"  Downloading {filename}...", end=' ', flush=True)
                download_file(remote_file, temp_dir)
                local_file = temp_dir / filename
                if local_file.exists():
                    downloaded_files.append(local_file)
                    print_colored("OK", Colors.GREEN)
                else:
                    print_colored("FALLITO", Colors.RED)
            except Exception as e:
                print_colored(f"Errore: {e}", Colors.RED)

        if not downloaded_files:
            print_colored("Nessun file scaricato con successo", Colors.RED)
            return

        print()
        print_colored(f"{len(downloaded_files)} file scaricati", Colors.GREEN)

        success = process_files_with_add_tracks(faba_dir, downloaded_files, custom_prefix)

        if success:
            print()
            print_colored("Spostamento file processati...", Colors.BLUE)
            for file_info in files:
                filename = file_info['Name']
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    move_remote_file(
                        f"{remote_incoming}/{filename}",
                        f"{remote_processed}/{timestamp}_{filename}"
                    )
                    print_colored(f"  {filename} -> processed/", Colors.GREEN)
                except Exception as e:
                    print_colored(f"  Impossibile spostare {filename}: {e}", Colors.YELLOW)

            print()
            print_colored("Sincronizzazione completata!", Colors.GREEN)


def list_command(remote_base='gdrive:Faba'):
    remote_incoming = f"{remote_base}/incoming"

    print_colored("File disponibili su Google Drive", Colors.BLUE)
    print()

    try:
        files = list_remote_files(remote_incoming)
    except Exception as e:
        print_colored(f"Errore: {e}", Colors.RED)
        return

    if not files:
        print_colored("Nessun file MP3 trovato in Faba/incoming", Colors.YELLOW)
        return

    print_colored(f"{len(files)} file trovati:", Colors.GREEN)
    print()
    for f in files:
        print(f"  - {f['Name']} ({f['Size'] / (1024 * 1024):.2f} MB)  [{f['ModTime']}]")


def show_usage():
    print("Usage: python3 sync_from_drive.py [command] [options]")
    print()
    print("Commands:")
    print("  --setup           Configura rclone per Google Drive (prima volta)")
    print("  --list            Mostra file disponibili su Google Drive")
    print("  --sync-all        Scarica e processa tutti i file disponibili")
    print()
    print("Options:")
    print("  --faba-dir DIR    Percorso al disco Faba")
    print("  --remote PATH     Percorso remoto base (default: gdrive:Faba)")
    print("  --prefix X        Prefisso ID per nuove figure (default: 9)")
    print()
    print("Esempi:")
    print("  # Prima configurazione")
    print("  python3 sync_from_drive.py --setup")
    print()
    print("  # Linux/macOS - sincronizza tutto")
    print("  python3 sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01")
    print()
    print("  # Windows - sincronizza tutto (Faba montato come E:)")
    print("  python sync_from_drive.py --sync-all --faba-dir E:\\MKI01")
    print()
    print("Struttura cartelle richiesta su Google Drive:")
    print("  Faba/")
    print("    +-- incoming/      (carica qui i nuovi MP3)")
    print("    +-- processed/     (file processati verranno spostati qui)")


def main():
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    command = sys.argv[1]
    faba_dir = None
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

    try:
        if command == '--setup':
            setup_rclone()

        elif command == '--list':
            if not check_rclone_configured():
                print_colored("rclone non configurato. Esegui prima: python3 sync_from_drive.py --setup", Colors.RED)
                sys.exit(1)
            list_command(remote_base)

        elif command == '--sync-all':
            if not check_rclone_configured():
                print_colored("rclone non configurato. Esegui prima: python3 sync_from_drive.py --setup", Colors.RED)
                sys.exit(1)
            if faba_dir is None:
                print_colored("Errore: --faba-dir e obbligatorio per --sync-all", Colors.RED)
                print("Esempio: python3 sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01")
                sys.exit(1)
            if not faba_dir.exists():
                print_colored(f"Directory Faba non trovata: {faba_dir}", Colors.RED)
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
        print_colored(f"Errore: {e}", Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
