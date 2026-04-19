#!/usr/bin/env python3
"""Encrypt an MP3 file into MyFaba .MKI format."""

import sys
from cipher import encrypt_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: mki_cipher.py <input-file>")
        sys.exit(1)
    out = encrypt_file(sys.argv[1])
    print(f"File processed successfully. Output file: {out}")
