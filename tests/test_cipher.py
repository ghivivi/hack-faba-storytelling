"""Tests for cipher.py — encrypt/decrypt roundtrip."""

import os
import pytest
from pathlib import Path
from cipher import encrypt_file, decrypt_file


def make_mp3(path: Path, size: int = 1024) -> Path:
    """Create a fake MP3 file with random-ish bytes."""
    data = bytes((i * 37 + 13) % 256 for i in range(size))
    path.write_bytes(data)
    return path


def test_encrypt_produces_mki_file(tmp_path):
    src = make_mp3(tmp_path / "track.mp3")
    out = encrypt_file(str(src))
    assert out == str(src) + ".MKI"
    assert Path(out).exists()
    assert Path(out).stat().st_size == src.stat().st_size


def test_encrypt_changes_content(tmp_path):
    src = make_mp3(tmp_path / "track.mp3")
    original = src.read_bytes()
    out = encrypt_file(str(src))
    assert Path(out).read_bytes() != original


def test_decrypt_roundtrip(tmp_path):
    src = make_mp3(tmp_path / "track.mp3")
    original = src.read_bytes()

    mki = tmp_path / "track.mp3.MKI"
    encrypt_file(str(src))

    restored = tmp_path / "restored.mp3"
    decrypt_file(str(mki), str(restored))

    assert restored.read_bytes() == original


def test_encrypt_empty_file(tmp_path):
    src = tmp_path / "empty.mp3"
    src.write_bytes(b"")
    out = encrypt_file(str(src))
    assert Path(out).read_bytes() == b""


def test_decrypt_empty_file(tmp_path):
    src = tmp_path / "empty.MKI"
    src.write_bytes(b"")
    out = tmp_path / "empty.mp3"
    decrypt_file(str(src), str(out))
    assert out.read_bytes() == b""


def test_roundtrip_large_file(tmp_path):
    src = make_mp3(tmp_path / "large.mp3", size=100_000)
    original = src.read_bytes()
    mki = tmp_path / "large.mp3.MKI"
    encrypt_file(str(src))
    restored = tmp_path / "restored.mp3"
    decrypt_file(str(mki), str(restored))
    assert restored.read_bytes() == original


def test_encrypt_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        encrypt_file(str(tmp_path / "nonexistent.mp3"))


def test_decrypt_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        decrypt_file(str(tmp_path / "nonexistent.MKI"), str(tmp_path / "out.mp3"))
