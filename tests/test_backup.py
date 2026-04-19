"""Tests for backup_faba.py — backup creation and verification."""

import json
import zipfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


def make_faba_dir(tmp_path: Path) -> Path:
    """Create a minimal Faba directory structure with fake MKI files."""
    faba = tmp_path / "MKI01"
    for figure_id, n_tracks in [("K9001", 3), ("K9002", 2)]:
        fig_dir = faba / figure_id
        fig_dir.mkdir(parents=True)
        for i in range(1, n_tracks + 1):
            track = fig_dir / f"CP{i:02d}.MKI"
            track.write_bytes(bytes(range(256)) * 4)
    return faba


# --- scan_faba_directory ---

def test_scan_faba_directory(tmp_path):
    from backup_faba import scan_faba_directory
    faba = make_faba_dir(tmp_path)
    stats = scan_faba_directory(faba)
    assert stats["total_files"] == 5
    assert len(stats["figures"]) == 2
    assert stats["total_size"] > 0


def test_scan_faba_directory_empty(tmp_path):
    from backup_faba import scan_faba_directory
    faba = tmp_path / "MKI01"
    faba.mkdir()
    stats = scan_faba_directory(faba)
    assert stats["total_files"] == 0
    assert stats["figures"] == []


# --- create_backup ---

def test_create_backup_produces_zip(tmp_path):
    from backup_faba import create_backup
    faba = make_faba_dir(tmp_path)
    out_dir = tmp_path / "backups"
    out_dir.mkdir()

    backup_path, metadata = create_backup(faba, out_dir, compression_level=1, show_progress=False)

    assert backup_path.exists()
    assert backup_path.suffix == ".zip"
    assert zipfile.is_zipfile(backup_path)


def test_create_backup_metadata_in_zip(tmp_path):
    from backup_faba import create_backup
    faba = make_faba_dir(tmp_path)
    out_dir = tmp_path / "backups"
    out_dir.mkdir()

    backup_path, _ = create_backup(faba, out_dir, compression_level=1, show_progress=False)

    with zipfile.ZipFile(backup_path) as zf:
        meta = json.loads(zf.read("backup_metadata.json"))
        assert meta["statistics"]["total_files"] == 5
        assert len(meta["statistics"]["figures"]) == 2


def test_create_backup_contains_all_tracks(tmp_path):
    from backup_faba import create_backup
    faba = make_faba_dir(tmp_path)
    out_dir = tmp_path / "backups"
    out_dir.mkdir()

    backup_path, _ = create_backup(faba, out_dir, compression_level=1, show_progress=False)

    with zipfile.ZipFile(backup_path) as zf:
        names = zf.namelist()
        assert "K9001/CP01.MKI" in names
        assert "K9001/CP03.MKI" in names
        assert "K9002/CP02.MKI" in names


# --- verify_backup ---

def test_verify_backup_valid(tmp_path):
    from backup_faba import create_backup, verify_backup
    faba = make_faba_dir(tmp_path)
    out_dir = tmp_path / "backups"
    out_dir.mkdir()

    backup_path, _ = create_backup(faba, out_dir, compression_level=1, show_progress=False)
    assert verify_backup(backup_path) is True


def test_verify_backup_corrupt_file(tmp_path):
    from backup_faba import verify_backup
    bad_zip = tmp_path / "corrupt.zip"
    bad_zip.write_bytes(b"this is not a zip file")
    assert verify_backup(bad_zip) is False


def test_verify_backup_missing_file(tmp_path):
    from backup_faba import verify_backup
    assert verify_backup(tmp_path / "nonexistent.zip") is False


# --- calculate_checksum ---

def test_calculate_checksum_deterministic(tmp_path):
    from backup_faba import calculate_checksum
    f = tmp_path / "file.bin"
    f.write_bytes(b"hello world")
    assert calculate_checksum(f) == calculate_checksum(f)


def test_calculate_checksum_differs_on_content(tmp_path):
    from backup_faba import calculate_checksum
    f1 = tmp_path / "a.bin"
    f2 = tmp_path / "b.bin"
    f1.write_bytes(b"aaa")
    f2.write_bytes(b"bbb")
    assert calculate_checksum(f1) != calculate_checksum(f2)
