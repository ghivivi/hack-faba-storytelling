"""Tests for add_tracks.py — figure creation and track management."""

import shutil
import pytest
from pathlib import Path
from unittest.mock import patch

# add_tracks imports mutagen at runtime; mock it where needed
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


def make_fake_mp3(path: Path, size: int = 2048) -> Path:
    data = bytes((i * 17 + 5) % 256 for i in range(size))
    path.write_bytes(data)
    return path


def make_faba_dir(tmp_path: Path) -> Path:
    faba = tmp_path / "MKI01"
    faba.mkdir()
    return faba


# --- scan_existing_ids ---

def test_scan_existing_ids_empty(tmp_path):
    from add_tracks import scan_existing_ids
    faba = make_faba_dir(tmp_path)
    assert scan_existing_ids(faba) == []


def test_scan_existing_ids_finds_folders(tmp_path):
    from add_tracks import scan_existing_ids
    faba = make_faba_dir(tmp_path)
    (faba / "K9001").mkdir()
    (faba / "K9003").mkdir()
    (faba / "K0010").mkdir()
    (faba / "notafigure").mkdir()
    ids = scan_existing_ids(faba)
    assert "9001" in ids
    assert "9003" in ids
    assert "0010" in ids
    assert len(ids) == 3


def test_scan_existing_ids_with_prefix(tmp_path):
    from add_tracks import scan_existing_ids
    faba = make_faba_dir(tmp_path)
    (faba / "K9001").mkdir()
    (faba / "K8001").mkdir()
    ids = scan_existing_ids(faba, custom_prefix="9")
    assert ids == ["9001"]


# --- generate_next_id ---

def test_generate_next_id_empty_dir(tmp_path):
    from add_tracks import generate_next_id
    faba = make_faba_dir(tmp_path)
    assert generate_next_id(faba) == "9000"


def test_generate_next_id_increments(tmp_path):
    from add_tracks import generate_next_id
    faba = make_faba_dir(tmp_path)
    (faba / "K9000").mkdir()
    (faba / "K9001").mkdir()
    assert generate_next_id(faba) == "9002"


def test_generate_next_id_custom_prefix(tmp_path):
    from add_tracks import generate_next_id
    faba = make_faba_dir(tmp_path)
    (faba / "K8000").mkdir()
    assert generate_next_id(faba, custom_prefix="8") == "8001"


def test_generate_next_id_overflow(tmp_path):
    from add_tracks import generate_next_id
    faba = make_faba_dir(tmp_path)
    (faba / "K9999").mkdir()
    with pytest.raises(Exception, match="limite massimo"):
        generate_next_id(faba)


# --- create_new_figure ---

def test_create_new_figure(tmp_path):
    from add_tracks import create_new_figure
    faba = make_faba_dir(tmp_path)
    mp3 = make_fake_mp3(tmp_path / "track.mp3")

    with patch("builtins.input", return_value="yes"), \
         patch("add_tracks.update_id3_tag"):
        figure_id = create_new_figure(faba, [mp3], custom_id="9001")

    assert figure_id == "9001"
    assert (faba / "K9001").is_dir()
    assert (faba / "K9001" / "CP01.MKI").exists()


def test_create_new_figure_multiple_tracks(tmp_path):
    from add_tracks import create_new_figure
    faba = make_faba_dir(tmp_path)
    mp3s = [make_fake_mp3(tmp_path / f"track{i}.mp3") for i in range(3)]

    with patch("builtins.input", return_value="yes"), \
         patch("add_tracks.update_id3_tag"):
        figure_id = create_new_figure(faba, mp3s, custom_id="9010")

    assert (faba / "K9010" / "CP01.MKI").exists()
    assert (faba / "K9010" / "CP02.MKI").exists()
    assert (faba / "K9010" / "CP03.MKI").exists()


def test_create_new_figure_cancelled(tmp_path):
    from add_tracks import create_new_figure
    faba = make_faba_dir(tmp_path)
    mp3 = make_fake_mp3(tmp_path / "track.mp3")

    with patch("builtins.input", return_value="no"):
        result = create_new_figure(faba, [mp3], custom_id="9001")

    assert result is None
    assert not (faba / "K9001").exists()


def test_create_new_figure_existing_folder_raises(tmp_path):
    from add_tracks import create_new_figure
    faba = make_faba_dir(tmp_path)
    (faba / "K9001").mkdir()
    mp3 = make_fake_mp3(tmp_path / "track.mp3")

    with pytest.raises(Exception, match="esiste"):
        create_new_figure(faba, [mp3], custom_id="9001")


def test_create_new_figure_invalid_id(tmp_path):
    from add_tracks import create_new_figure
    faba = make_faba_dir(tmp_path)
    mp3 = make_fake_mp3(tmp_path / "track.mp3")

    with pytest.raises(Exception, match="4 cifre"):
        create_new_figure(faba, [mp3], custom_id="abc")
