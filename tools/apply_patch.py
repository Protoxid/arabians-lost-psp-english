#!/usr/bin/env python3
"""
Arabians Lost (PSP) — Distributable Translation Patch Installer.
Applies the English xdelta3 patch to a user-provided Japanese ISO.
"""

import os
import sys
import hashlib
import time
import pyxdelta

EXPECTED_ORIGINAL_SHA256 = "5eddbb1bb87bc88f4efa380826276cd605fe65dac0c8beee73b64d7e91be110e"

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def apply_patch(
    orig_iso: str,
    patch_file: str,
    output_iso: str
):
    print("=" * 60)
    print("ARABIANS LOST — ENGLISH TRANSLATION INSTALLER")
    print("=" * 60)
    
    if not os.path.exists(orig_iso):
        print(f"Error: Original ISO '{orig_iso}' not found!")
        sys.exit(1)
    if not os.path.exists(patch_file):
        print(f"Error: Patch file '{patch_file}' not found!")
        sys.exit(1)
        
    print("Verifying source ISO SHA-256...")
    orig_hash = compute_sha256(orig_iso)
    if orig_hash != EXPECTED_ORIGINAL_SHA256:
        print(f"Warning: Source ISO hash '{orig_hash}' does not match official ULJM06104!")
        print("Patching may fail or produce an invalid image.")
    else:
        print("[OK] Source ISO verified (Arabians Lost ULJM06104 v1.02).")
        
    print(f"Applying patch '{patch_file}' -> '{output_iso}'...")
    start_time = time.time()
    pyxdelta.decode(orig_iso, patch_file, output_iso)
    elapsed = time.time() - start_time
    
    out_size = os.path.getsize(output_iso)
    out_hash = compute_sha256(output_iso)
    print(f"Patch applied successfully in {elapsed:.2f} seconds.")
    print(f"Output File:   {output_iso}")
    print(f"Output Size:   {out_size:,} bytes")
    print(f"Output SHA-256: {out_hash}")
    print("=" * 60)
    print("SUCCESS! Ready to play on PPSSPP or real PSP hardware.")
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python tools/apply_patch.py <original.iso> <patch.xdelta> <output_english.iso>")
        sys.exit(1)
    apply_patch(sys.argv[1], sys.argv[2], sys.argv[3])
