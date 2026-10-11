#!/usr/bin/env python3
"""
Round-trip test for Arabians Lost scenario extraction and repacking.
Tests byte-identical preservation when no translations are applied.
"""

import os
import sys
import glob

sys.path.insert(0, os.path.abspath('.'))
from tools.extract import extract_file
from tools.repack import repack_file

def test_roundtrip():
    scenario_dir = 'extracted/data_cpk/scenario'
    ks_files = glob.glob(os.path.join(scenario_dir, '**', '*.ks'), recursive=True)
    
    tested = 0
    passed = 0
    failed = []
    
    print(f"Testing round-trip fidelity on {len(ks_files)} scenario files...")
    for fpath in ks_files:
        rel = os.path.relpath(fpath, scenario_dir).replace('\\', '/')
        with open(fpath, 'rb') as fp:
            orig_bytes = fp.read()
            
        repacked_str = repack_file(fpath, {}, rel)
        repacked_bytes = repacked_str.encode('cp932')
        
        tested += 1
        if orig_bytes == repacked_bytes:
            passed += 1
        else:
            failed.append((rel, len(orig_bytes), len(repacked_bytes)))
            
    print(f"Round-trip results: {passed}/{tested} files 100% byte-identical!")
    if failed:
        print(f"Mismatches ({len(failed)} files):")
        for f, o_sz, r_sz in failed[:10]:
            print(f"  {f}: orig {o_sz} vs repacked {r_sz}")
        return False
    else:
        print("PERFECT: 100% Byte-identical round-trip verified across all scripts!")
        return True

if __name__ == '__main__':
    success = test_roundtrip()
    if not success:
        exit(1)
