"""Tests for remove_ads.py — ad detection and backup/delete modes."""

import pytest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

AD_SIZE = 455_000    # within 440-470KB range
CONTENT_SIZE = 2_000_000  # well outside ad range


def make_mki(path: Path, size: int) -> Path:
    path.write_bytes(b"\x00" * size)
    return path


def make_faba_dir(tmp_path: Path, figures: dict) -> Path:
    """
    figures = {"K0010": {"CP01": AD_SIZE, "CP02": CONTENT_SIZE}, ...}
    """
    faba = tmp_path / "MKI01"
    for fig_name, tracks in figures.items():
        fig_dir = faba / fig_name
        fig_dir.mkdir(parents=True)
        for track_name, size in tracks.items():
            make_mki(fig_dir / f"{track_name}.MKI", size)
    return faba


# --- analyze_cp01_files ---

def test_analyze_detects_ads(tmp_path):
    from remove_ads import analyze_cp01_files
    faba = make_faba_dir(tmp_path, {
        "K0010": {"CP01": AD_SIZE, "CP02": CONTENT_SIZE},
        "K0011": {"CP01": CONTENT_SIZE},
    })
    ad_files, content_files = analyze_cp01_files(faba)
    assert len(ad_files) == 1
    assert len(content_files) == 1
    assert ad_files[0][2] == "K0010"
    assert content_files[0][2] == "K0011"


def test_analyze_no_ads(tmp_path):
    from remove_ads import analyze_cp01_files
    faba = make_faba_dir(tmp_path, {
        "K0010": {"CP01": CONTENT_SIZE},
    })
    ad_files, content_files = analyze_cp01_files(faba)
    assert ad_files == []
    assert len(content_files) == 1


def test_analyze_empty_dir(tmp_path):
    from remove_ads import analyze_cp01_files
    faba = tmp_path / "MKI01"
    faba.mkdir()
    ad_files, content_files = analyze_cp01_files(faba)
    assert ad_files == []
    assert content_files == []


def test_analyze_multiple_ads(tmp_path):
    from remove_ads import analyze_cp01_files
    faba = make_faba_dir(tmp_path, {
        "K0010": {"CP01": 445_000},
        "K0011": {"CP01": 460_000},
        "K0012": {"CP01": CONTENT_SIZE},
    })
    ad_files, content_files = analyze_cp01_files(faba)
    assert len(ad_files) == 2
    assert len(content_files) == 1


# --- backup_mode ---

def test_backup_mode_moves_files(tmp_path):
    from remove_ads import backup_mode
    faba = make_faba_dir(tmp_path, {
        "K0010": {"CP01": AD_SIZE, "CP02": CONTENT_SIZE},
    })
    cp01 = faba / "K0010" / "CP01.MKI"
    ad_files = [(cp01, AD_SIZE, "K0010")]
    log_file = str(tmp_path / "log.txt")

    with patch("builtins.input", return_value="yes"):
        success, affected = backup_mode(ad_files, log_file)

    assert success is True
    assert "K0010" in affected
    assert not cp01.exists()
    assert (faba / "K0010" / "CP02.MKI").exists()


def test_backup_mode_cancelled(tmp_path):
    from remove_ads import backup_mode
    faba = make_faba_dir(tmp_path, {"K0010": {"CP01": AD_SIZE}})
    cp01 = faba / "K0010" / "CP01.MKI"
    ad_files = [(cp01, AD_SIZE, "K0010")]
    log_file = str(tmp_path / "log.txt")

    with patch("builtins.input", return_value="no"):
        success, affected = backup_mode(ad_files, log_file)

    assert success is False
    assert cp01.exists()


# --- delete_mode ---

def test_delete_mode_removes_files(tmp_path):
    from remove_ads import delete_mode
    faba = make_faba_dir(tmp_path, {"K0010": {"CP01": AD_SIZE, "CP02": CONTENT_SIZE}})
    cp01 = faba / "K0010" / "CP01.MKI"
    ad_files = [(cp01, AD_SIZE, "K0010")]
    log_file = str(tmp_path / "log.txt")

    with patch("builtins.input", return_value="DELETE"):
        success, affected = delete_mode(ad_files, log_file)

    assert success is True
    assert not cp01.exists()
    assert (faba / "K0010" / "CP02.MKI").exists()


def test_delete_mode_cancelled(tmp_path):
    from remove_ads import delete_mode
    faba = make_faba_dir(tmp_path, {"K0010": {"CP01": AD_SIZE}})
    cp01 = faba / "K0010" / "CP01.MKI"
    ad_files = [(cp01, AD_SIZE, "K0010")]
    log_file = str(tmp_path / "log.txt")

    with patch("builtins.input", return_value="no"):
        success, _ = delete_mode(ad_files, log_file)

    assert success is False
    assert cp01.exists()
