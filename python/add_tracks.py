#!/usr/bin/env python3
"""
add_tracks.py - Faba Track Manager

Aggiunge nuovi file MP3 al dispositivo Faba:
- Crea nuove figure con ID autoincrementale personalizzato
- Aggiunge tracce a figure esistenti con rinumerazione automatica
- Gestisce cifratura .MKI e aggiornamento tag ID3

Usage:
  # Linux/macOS
  python3 add_tracks.py /mnt/faba/MKI01 --new-figure track1.mp3 track2.mp3

  # Windows (Faba montato come E:)
  python add_tracks.py E:/MKI01 --new-figure track1.mp3 track2.mp3

  # Aggiunge a figura esistente
  python3 add_tracks.py /mnt/faba/MKI01 --add-to K0015 track.mp3

  # Inserisce in posizione specifica con rinumerazione
  python3 add_tracks.py /mnt/faba/MKI01 --add-to K0015 track.mp3 --position 2
"""

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

from faba_utils import Colors, print_colored

# cipher.py is in the python/ subdirectory
from cipher import encrypt_file, decrypt_file


def update_id3_tag(mp3_path: Path, figure_id: str, track_num: int):
    try:
        from mutagen.id3 import ID3, TIT2
        from mutagen.mp3 import MP3
        tags = MP3(str(mp3_path), ID3=ID3)
        tags.delete()
        tags["TIT2"] = TIT2(encoding=3, text=f"K{figure_id}CP{track_num:02d}")
        tags.save()
    except Exception as e:
        raise Exception(f"Errore aggiornamento tag ID3 per {mp3_path.name}: {e}")


def scan_existing_ids(faba_dir: Path, custom_prefix: Optional[str] = None) -> List[str]:
    pattern = re.compile(r'^K(\d{4})$')
    ids = []
    for folder in faba_dir.glob('K*'):
        if folder.is_dir():
            match = pattern.match(folder.name)
            if match:
                figure_id = match.group(1)
                if custom_prefix is None or figure_id.startswith(custom_prefix):
                    ids.append(figure_id)
    return sorted(ids)


def generate_next_id(faba_dir: Path, custom_prefix: Optional[str] = None) -> str:
    if custom_prefix is None:
        custom_prefix = "9"

    existing_ids = scan_existing_ids(faba_dir, custom_prefix)

    if not existing_ids:
        return f"{custom_prefix}000"

    next_num = int(existing_ids[-1]) + 1
    prefix_max = int(custom_prefix) * 1000 + 999

    if next_num > prefix_max:
        raise Exception(f"Raggiunto il limite massimo per il prefisso {custom_prefix} ({prefix_max})")
    if next_num > 9999:
        raise Exception("Raggiunto il limite massimo di ID (9999)")

    return f"{next_num:04d}"


def create_new_figure(faba_dir: Path, mp3_files: List[Path],
                      custom_id: Optional[str] = None,
                      custom_prefix: Optional[str] = None) -> Optional[str]:
    if custom_id:
        if len(custom_id) != 4 or not custom_id.isdigit():
            raise Exception("L'ID custom deve essere di 4 cifre numeriche (es. 9001)")
        figure_id = custom_id
    else:
        figure_id = generate_next_id(faba_dir, custom_prefix)

    folder_name = f"K{figure_id}"
    figure_dir = faba_dir / folder_name

    if figure_dir.exists():
        raise Exception(f"La cartella {folder_name} esiste gia")

    print()
    print_colored("CREAZIONE NUOVA FIGURA", Colors.CYAN)
    print()
    print_colored(f"Cartella: {folder_name}", Colors.BOLD)
    print(f"   ID figura: {figure_id}")
    print(f"   Tracce: {len(mp3_files)}")
    print()
    for i, mp3_file in enumerate(mp3_files, start=1):
        print(f"   CP{i:02d}: {mp3_file.name}")
    print()

    if input("Confermi la creazione? (yes/no): ").lower() != 'yes':
        print("Operazione annullata.")
        return None

    figure_dir.mkdir(parents=True, exist_ok=False)
    print_colored(f"Cartella {folder_name} creata", Colors.GREEN)

    for track_num, mp3_file in enumerate(mp3_files, start=1):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_mp3 = Path(tmpdir) / f"temp_{track_num}.mp3"
                shutil.copy(str(mp3_file), str(temp_mp3))
                update_id3_tag(temp_mp3, figure_id, track_num)
                mki_path = figure_dir / f"CP{track_num:02d}.MKI"
                encrypt_file(str(temp_mp3))
                shutil.move(str(temp_mp3) + ".MKI", str(mki_path))
            print_colored(f"CP{track_num:02d}.MKI creato da {mp3_file.name}", Colors.GREEN)
        except Exception as e:
            print_colored(f"Errore con {mp3_file.name}: {e}", Colors.RED)
            if figure_dir.exists():
                shutil.rmtree(figure_dir)
            raise Exception(f"Creazione figura fallita: {e}")

    print()
    print_colored(f"Figura {folder_name} creata con successo! ({len(mp3_files)} tracce)", Colors.GREEN)
    return figure_id


def add_to_existing_figure(faba_dir: Path, figure_id: str, mp3_files: List[Path],
                            position: Optional[int] = None):
    folder_name = f"K{figure_id}"
    figure_dir = faba_dir / folder_name

    if not figure_dir.exists():
        raise Exception(f"La cartella {folder_name} non esiste")

    existing_tracks = sorted(figure_dir.glob('CP*.MKI'))
    num_existing = len(existing_tracks)

    if position is None:
        position = num_existing + 1

    if position < 1 or position > num_existing + 1:
        raise Exception(f"Posizione non valida. Deve essere tra 1 e {num_existing + 1}")

    print()
    print_colored("AGGIUNTA TRACCE A FIGURA ESISTENTE", Colors.CYAN)
    print()
    print_colored(f"Cartella: {folder_name}", Colors.BOLD)
    print(f"   Tracce esistenti: {num_existing}")
    print(f"   Nuove tracce: {len(mp3_files)}")
    print(f"   Posizione inserimento: {position}")
    print()

    print_colored("Nuove tracce da aggiungere:", Colors.YELLOW)
    for i, mp3_file in enumerate(mp3_files, start=position):
        print(f"   CP{i:02d}: {mp3_file.name}")
    print()

    if position <= num_existing:
        print_colored(f"Le tracce dalla posizione {position} in poi verranno rinumerate:", Colors.YELLOW)
        for old_track in existing_tracks[position - 1:]:
            old_num = int(old_track.stem[2:])
            print(f"   CP{old_num:02d}.MKI -> CP{old_num + len(mp3_files):02d}.MKI")
        print()

    if input("Confermi l'operazione? (yes/no): ").lower() != 'yes':
        print("Operazione annullata.")
        return

    print()

    # Renumber existing tracks backwards to avoid conflicts
    if position <= num_existing:
        print_colored("Rinumerazione tracce esistenti...", Colors.BLUE)
        for old_track in sorted(existing_tracks[position - 1:], reverse=True):
            old_num = int(old_track.stem[2:])
            new_num = old_num + len(mp3_files)
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    temp_mp3 = Path(tmpdir) / "temp.mp3"
                    temp_mki = Path(tmpdir) / f"CP{new_num:02d}.MKI"
                    decrypt_file(str(old_track), str(temp_mp3))
                    update_id3_tag(temp_mp3, figure_id, new_num)
                    encrypt_file(str(temp_mp3))
                    shutil.move(str(temp_mp3) + ".MKI", str(figure_dir / f"CP{new_num:02d}.MKI"))
                    old_track.unlink()
                print_colored(f"  CP{old_num:02d}.MKI -> CP{new_num:02d}.MKI", Colors.GREEN)
            except Exception as e:
                print_colored(f"  Errore rinumerazione CP{old_num:02d}.MKI: {e}", Colors.RED)
                raise Exception(f"Rinumerazione fallita: {e}")
        print()

    # Add new tracks
    print_colored("Aggiunta nuove tracce...", Colors.BLUE)
    for i, mp3_file in enumerate(mp3_files):
        track_num = position + i
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_mp3 = Path(tmpdir) / "temp.mp3"
                shutil.copy(str(mp3_file), str(temp_mp3))
                update_id3_tag(temp_mp3, figure_id, track_num)
                mki_path = figure_dir / f"CP{track_num:02d}.MKI"
                encrypt_file(str(temp_mp3))
                shutil.move(str(temp_mp3) + ".MKI", str(mki_path))
            print_colored(f"  CP{track_num:02d}.MKI creato da {mp3_file.name}", Colors.GREEN)
        except Exception as e:
            print_colored(f"  Errore con {mp3_file.name}: {e}", Colors.RED)
            raise Exception(f"Aggiunta traccia fallita: {e}")

    print()
    print_colored(f"Tracce aggiunte con successo a {folder_name}! "
                  f"(Totale: {num_existing + len(mp3_files)})", Colors.GREEN)


def show_usage():
    print("Usage: python3 add_tracks.py <faba_directory> [options]")
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
    print("  # Linux/macOS")
    print("  python3 add_tracks.py /mnt/faba/MKI01 --new-figure track1.mp3 track2.mp3")
    print()
    print("  # Windows")
    print("  python add_tracks.py E:\\MKI01 --new-figure track1.mp3 track2.mp3")
    print()
    print("  # Aggiunge tracce alla fine di una figura esistente")
    print("  python3 add_tracks.py /mnt/faba/MKI01 --add-to K0015 newtrack.mp3")
    print()
    print("  # Inserisce traccia in posizione 2 (rinumera le successive)")
    print("  python3 add_tracks.py /mnt/faba/MKI01 --add-to K0015 intro.mp3 --position 2")
    print()
    print("Requisiti:")
    print("  pip install mutagen colorama")


def main():
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    try:
        from mutagen.id3 import ID3, TIT2
        from mutagen.mp3 import MP3
    except ImportError:
        print_colored("Errore: Il modulo 'mutagen' e richiesto", Colors.RED)
        print("Installa con: pip install mutagen")
        sys.exit(1)

    faba_dir = Path(sys.argv[1])

    if not faba_dir.is_dir():
        print_colored(f"Errore: Directory '{faba_dir}' non trovata", Colors.RED)
        sys.exit(1)

    args = sys.argv[2:]
    if not args:
        show_usage()
        sys.exit(1)

    print_colored("Faba Track Manager", Colors.BLUE)

    try:
        mode = args[0]

        if mode == '--new-figure':
            mp3_files, custom_id, custom_prefix = [], None, None
            i = 1
            while i < len(args):
                if args[i] == '--custom-id':
                    custom_id = args[i + 1]; i += 2
                elif args[i] == '--custom-prefix':
                    custom_prefix = args[i + 1]; i += 2
                else:
                    mp3_path = Path(args[i])
                    if not mp3_path.exists():
                        raise Exception(f"File non trovato: {args[i]}")
                    if mp3_path.suffix.lower() != '.mp3':
                        raise Exception(f"File non e un MP3: {args[i]}")
                    mp3_files.append(mp3_path)
                    i += 1
            if not mp3_files:
                raise Exception("Nessun file MP3 specificato")
            create_new_figure(faba_dir, mp3_files, custom_id, custom_prefix)

        elif mode == '--add-to':
            if len(args) < 2:
                raise Exception("--add-to richiede un ID figura e file MP3")
            figure_id = args[1].lstrip('K')
            if len(figure_id) != 4 or not figure_id.isdigit():
                raise Exception("ID figura deve essere di 4 cifre (es. K0015 o 0015)")
            mp3_files, position = [], None
            i = 2
            while i < len(args):
                if args[i] == '--position':
                    position = int(args[i + 1]); i += 2
                else:
                    mp3_path = Path(args[i])
                    if not mp3_path.exists():
                        raise Exception(f"File non trovato: {args[i]}")
                    if mp3_path.suffix.lower() != '.mp3':
                        raise Exception(f"File non e un MP3: {args[i]}")
                    mp3_files.append(mp3_path)
                    i += 1
            if not mp3_files:
                raise Exception("Nessun file MP3 specificato")
            add_to_existing_figure(faba_dir, figure_id, mp3_files, position)

        else:
            print_colored(f"Errore: Modalita non valida '{mode}'", Colors.RED)
            print()
            show_usage()
            sys.exit(1)

    except Exception as e:
        print()
        print_colored(f"Errore: {e}", Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
