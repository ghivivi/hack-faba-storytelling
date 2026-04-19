#!/usr/bin/env python3
"""
backup_faba.py - Faba Backup Tool

Crea backup completo del disco Faba in formato ZIP altamente compresso.

Features:
- Compressione massima (DEFLATE level 9)
- Progress bar durante la compressione
- Verifica integrità backup
- Statistiche dettagliate
- Opzionale upload su Google Drive

Usage:
  # Linux/macOS - Faba montato su /mnt/faba
  python3 backup_faba.py /mnt/faba/MKI01

  # Windows - Faba montato come drive E:
  python backup_faba.py E:/MKI01

  # Specifica cartella di destinazione
  python3 backup_faba.py /mnt/faba/MKI01 --output ~/backups

  # Backup + upload su Google Drive
  python3 backup_faba.py /mnt/faba/MKI01 --upload-to-drive

  # Backup veloce (compressione normale)
  python3 backup_faba.py /mnt/faba/MKI01 --fast
"""

import os
import sys
import zipfile
import hashlib
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

from faba_utils import Colors, print_colored


def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def calculate_checksum(file_path: Path, algorithm='sha256'):
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_faba_directory(faba_dir: Path) -> Dict:
    stats = {
        'total_files': 0,
        'total_size': 0,
        'figures': [],
        'file_types': {}
    }

    for figure_dir in sorted(faba_dir.glob('K*')):
        if not figure_dir.is_dir():
            continue

        tracks = list(figure_dir.glob('CP*.MKI'))
        figure_size = sum(f.stat().st_size for f in tracks)

        stats['figures'].append({
            'id': figure_dir.name,
            'tracks': len(tracks),
            'size': figure_size
        })
        stats['total_files'] += len(tracks)
        stats['total_size'] += figure_size

        for track in tracks:
            ext = track.suffix
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1

    return stats


def create_backup(faba_dir: Path, output_dir: Path, compression_level=9,
                  show_progress=True) -> Tuple[Path, Dict]:
    print_colored("Faba Backup Tool - Creazione backup...", Colors.BLUE)
    print()

    print_colored("Scansione directory Faba...", Colors.BLUE)
    stats = scan_faba_directory(faba_dir)

    print()
    print_colored("Statistiche:", Colors.BOLD)
    print(f"  Figure trovate: {len(stats['figures'])}")
    print(f"  File totali: {stats['total_files']}")
    print(f"  Dimensione totale: {format_size(stats['total_size'])}")
    print()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"faba_backup_{timestamp}.zip"
    backup_path = output_dir / backup_name

    metadata = {
        'backup_date': datetime.now().isoformat(),
        'source_path': str(faba_dir),
        'compression_level': compression_level,
        'statistics': stats
    }

    print_colored(f"Creazione backup: {backup_name}", Colors.CYAN)
    if compression_level == 9:
        print_colored("   Compressione: Massima (puo richiedere tempo)", Colors.CYAN)
    elif compression_level >= 6:
        print_colored("   Compressione: Alta", Colors.CYAN)
    else:
        print_colored("   Compressione: Standard", Colors.CYAN)
    print()

    processed_files = 0

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED,
                         compresslevel=compression_level) as zipf:
        for figure in stats['figures']:
            figure_id = figure['id']
            figure_dir = faba_dir / figure_id

            if show_progress:
                print(f"  {figure_id} ({figure['tracks']} tracce)...", end=' ', flush=True)

            for track_file in sorted(figure_dir.glob('CP*.MKI')):
                zipf.write(track_file, f"{figure_id}/{track_file.name}")
                processed_files += 1

            if show_progress:
                print_colored("OK", Colors.GREEN)

        zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))

    print()

    backup_size = backup_path.stat().st_size
    compression_ratio = (1 - backup_size / stats['total_size']) * 100 if stats['total_size'] > 0 else 0

    print_colored("Backup creato con successo!", Colors.GREEN)
    print()
    print_colored("Dettagli backup:", Colors.BOLD)
    print(f"  File: {backup_path}")
    print(f"  Dimensione originale: {format_size(stats['total_size'])}")
    print(f"  Dimensione backup: {format_size(backup_size)}")
    print(f"  Compressione: {compression_ratio:.1f}%")
    print()

    print_colored("Calcolo checksum...", Colors.BLUE)
    checksum = calculate_checksum(backup_path)
    print(f"  SHA256: {checksum}")
    print()

    metadata['backup_size'] = backup_size
    metadata['compression_ratio'] = compression_ratio
    metadata['checksum_sha256'] = checksum

    metadata_path = output_dir / f"faba_backup_{timestamp}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print_colored(f"Metadata salvato in: {metadata_path}", Colors.BLUE)
    print()

    return backup_path, metadata


def verify_backup(backup_path: Path) -> bool:
    print_colored("Verifica integrita backup...", Colors.BLUE)

    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            corrupt_files = zipf.testzip()
            if corrupt_files:
                print_colored(f"File corrotto nel backup: {corrupt_files}", Colors.RED)
                return False

            try:
                metadata = json.loads(zipf.read('backup_metadata.json'))
                print_colored("Backup verificato correttamente", Colors.GREEN)
                print(f"  Figure nel backup: {len(metadata['statistics']['figures'])}")
                print(f"  Data backup: {metadata['backup_date']}")
                return True
            except KeyError:
                print_colored("Attenzione: Metadata mancante nel backup", Colors.YELLOW)
                return True

    except zipfile.BadZipFile:
        print_colored("File ZIP corrotto o non valido", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"Errore durante verifica: {e}", Colors.RED)
        return False


def upload_to_drive(backup_path: Path, remote_path='gdrive:Faba/backups'):
    print()
    print_colored("Upload su Google Drive...", Colors.CYAN)

    try:
        result = subprocess.run(['rclone', 'listremotes'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode != 0 or 'gdrive:' not in result.stdout:
            print_colored("rclone non configurato per Google Drive", Colors.RED)
            print("Esegui: python3 sync_from_drive.py --setup")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_colored("rclone non installato", Colors.RED)
        return False

    try:
        print(f"  Upload {backup_path.name}...")
        result = subprocess.run(
            ['rclone', 'copy', str(backup_path), remote_path, '-P'],
            timeout=3600
        )
        if result.returncode == 0:
            print_colored(f"Backup caricato su {remote_path}", Colors.GREEN)
            return True
        else:
            print_colored("Errore durante upload", Colors.RED)
            return False
    except subprocess.TimeoutExpired:
        print_colored("Timeout durante upload", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"Errore: {e}", Colors.RED)
        return False


def list_backups(backup_dir: Path):
    print_colored("Backup Disponibili", Colors.BLUE)
    print()

    backups = sorted(backup_dir.glob('faba_backup_*.zip'), reverse=True)

    if not backups:
        print_colored("Nessun backup trovato", Colors.YELLOW)
        return

    for backup_path in backups:
        backup_size = backup_path.stat().st_size
        backup_time = datetime.fromtimestamp(backup_path.stat().st_mtime)
        metadata_path = backup_path.with_name(backup_path.stem + '_metadata.json')

        print_colored(f"{backup_path.name}", Colors.BOLD)
        print(f"   Data: {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Dimensione: {format_size(backup_size)}")

        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    stats = metadata['statistics']
                    print(f"   Figure: {len(stats['figures'])}")
                    print(f"   File: {stats['total_files']}")
                    print(f"   Compressione: {metadata.get('compression_ratio', 0):.1f}%")
                    if 'checksum_sha256' in metadata:
                        print(f"   SHA256: {metadata['checksum_sha256'][:16]}...")
            except Exception:
                pass

        print()


def show_usage():
    print("Usage: python3 backup_faba.py <faba_directory> [options]")
    print()
    print("Options:")
    print("  --output DIR          Directory destinazione backup (default: ./backups)")
    print("  --fast                Usa compressione veloce invece di massima")
    print("  --upload-to-drive     Carica backup su Google Drive dopo creazione")
    print("  --list                Lista backup esistenti")
    print("  --verify FILE         Verifica integrita di un backup")
    print()
    print("Esempi:")
    print("  # Linux/macOS")
    print("  python3 backup_faba.py /mnt/faba/MKI01")
    print()
    print("  # Windows (Faba montato come E:)")
    print("  python backup_faba.py E:\\MKI01")
    print()
    print("  # Backup veloce + upload su Drive")
    print("  python3 backup_faba.py /mnt/faba/MKI01 --fast --upload-to-drive")
    print()
    print("  # Lista backup esistenti")
    print("  python3 backup_faba.py --list")
    print()
    print("  # Verifica backup")
    print("  python3 backup_faba.py --verify backups/faba_backup_20260210_143022.zip")


def main():
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    if sys.argv[1] == '--list':
        backup_dir = Path('./backups')
        if len(sys.argv) > 3 and sys.argv[2] == '--output':
            backup_dir = Path(sys.argv[3])
        list_backups(backup_dir)
        return

    if sys.argv[1] == '--verify':
        if len(sys.argv) < 3:
            print_colored("Errore: Specifica il file da verificare", Colors.RED)
            sys.exit(1)
        backup_path = Path(sys.argv[2])
        if not backup_path.exists():
            print_colored(f"Errore: File non trovato: {backup_path}", Colors.RED)
            sys.exit(1)
        sys.exit(0 if verify_backup(backup_path) else 1)

    faba_dir = Path(sys.argv[1])
    output_dir = Path('./backups')
    compression_level = 9
    upload_to_drive_flag = False

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--output':
            if i + 1 >= len(sys.argv):
                print_colored("Errore: --output richiede un percorso", Colors.RED)
                sys.exit(1)
            output_dir = Path(sys.argv[i + 1])
            i += 2
        elif arg == '--fast':
            compression_level = 6
            i += 1
        elif arg == '--upload-to-drive':
            upload_to_drive_flag = True
            i += 1
        else:
            print_colored(f"Errore: Argomento non valido '{arg}'", Colors.RED)
            sys.exit(1)

    if not faba_dir.exists() or not faba_dir.is_dir():
        print_colored(f"Errore: Directory non trovata: {faba_dir}", Colors.RED)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        backup_path, metadata = create_backup(faba_dir, output_dir, compression_level)

        if verify_backup(backup_path):
            print_colored("Backup completato e verificato!", Colors.GREEN)
        else:
            print_colored("Backup creato ma verifica fallita!", Colors.YELLOW)

        if upload_to_drive_flag:
            upload_to_drive(backup_path)

        print()
        print_colored(f"Backup salvato in: {backup_path}", Colors.BOLD)
        print()

    except KeyboardInterrupt:
        print()
        print_colored("Operazione interrotta dall'utente", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_colored(f"Errore: {e}", Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
