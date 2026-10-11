#!/usr/bin/env python3
"""
Arabians Lost (PSP) — Distributable Translation Patch Generator.
Generates an xdelta3 patch between the untouched Japanese ISO and the translated English ISO.
"""

import os
import sys
import hashlib
import time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import pyxdelta

EXPECTED_ORIGINAL_SHA256 = "5eddbb1bb87bc88f4efa380826276cd605fe65dac0c8beee73b64d7e91be110e"

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def make_patch(
    orig_iso: str = 'input/original.iso',
    trans_iso: str = 'build/ArabiansLost_English.iso',
    output_patch: str = 'release/ArabiansLost_English_v1.0.xdelta'
):
    print("=" * 60)
    print("ARABIANS LOST — TRANSLATION PATCH CREATOR")
    print("=" * 60)
    
    if not os.path.exists(orig_iso):
        print(f"Error: Original ISO '{orig_iso}' not found!")
        sys.exit(1)
    if not os.path.exists(trans_iso):
        print(f"Error: Translated ISO '{trans_iso}' not found!")
        sys.exit(1)
        
    os.makedirs('release', exist_ok=True)
    
    print("Verifying original ISO SHA-256...")
    orig_hash = compute_sha256(orig_iso)
    print(f"Original ISO Hash: {orig_hash}")
    if orig_hash != EXPECTED_ORIGINAL_SHA256:
        print(f"Warning: Original ISO hash does not match reference ULJM06104!")
        print(f"Expected: {EXPECTED_ORIGINAL_SHA256}")
    else:
        print("[OK] Source ISO cryptographic identity verified.")
        
    print("Computing translated ISO SHA-256...")
    trans_hash = compute_sha256(trans_iso)
    print(f"Translated ISO Hash: {trans_hash}")
    
    print(f"Generating xdelta3 patch: {output_patch}...")
    start_time = time.time()
    pyxdelta.run(orig_iso, trans_iso, output_patch)
    elapsed = time.time() - start_time
    patch_size = os.path.getsize(output_patch)
    patch_hash = compute_sha256(output_patch)
    print(f"Patch created in {elapsed:.2f} seconds ({patch_size:,} bytes).")
    print(f"Patch SHA-256: {patch_hash}")
    
    # Write release SHA256SUMS.txt
    sums_path = 'release/SHA256SUMS.txt'
    with open(sums_path, 'w', encoding='utf-8') as f:
        f.write(f"# Arabians Lost (PSP) — English Fan Translation v1.0\n")
        f.write(f"# Original Japanese ISO (ULJM06104 v1.02):\n")
        f.write(f"{orig_hash} *original.iso\n\n")
        f.write(f"# Patched English ISO:\n")
        f.write(f"{trans_hash} *ArabiansLost_English.iso\n\n")
        f.write(f"# Distributable xdelta3 Patch:\n")
        f.write(f"{patch_hash} *{os.path.basename(output_patch)}\n")
        
    print(f"Updated {sums_path}")
    print("=" * 60)
    print("PATCH GENERATION COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    orig = sys.argv[1] if len(sys.argv) > 1 else 'input/original.iso'
    trans = sys.argv[2] if len(sys.argv) > 2 else 'build/ArabiansLost_English.iso'
    patch = sys.argv[3] if len(sys.argv) > 3 else 'release/ArabiansLost_English_v1.0.xdelta'
    make_patch(orig, trans, patch)
