#!/usr/bin/env python3
"""
PSP ISO patcher and builder for Arabians Lost.
Allows replacing ISO 9660 files either in-place or appended to the ISO image.
"""

import os
import sys
import struct
import shutil
from typing import Dict, Union

def patch_iso(orig_iso_path: str, replacements: Dict[str, Union[bytes, str]], output_iso_path: str):
    """
    replacements: dict of {'PSP_GAME/USRDIR/data.cpk': new_data_or_path, ...}
    """
    print(f"Opening original ISO: {orig_iso_path}")
    
    # Copy original ISO to output if different
    if orig_iso_path != output_iso_path:
        print(f"Creating copy at: {output_iso_path}...")
        shutil.copyfile(orig_iso_path, output_iso_path)
        
    with open(output_iso_path, 'r+b') as iso_f:
        # Read PVD
        iso_f.seek(16 * 2048)
        pvd = bytearray(iso_f.read(2048))
        if pvd[1:6] != b'CD001':
            raise ValueError("Not a valid ISO 9660 image")
            
        vol_space_size, = struct.unpack_from('<I', pvd, 80)
        root_lba, = struct.unpack_from('<I', pvd, 156 + 2)
        root_size, = struct.unpack_from('<I', pvd, 156 + 10)
        
        # Locate all directory records and file positions
        def scan_dir(lba: int, size: int, prefix: str = '') -> Dict[str, Dict]:
            iso_f.seek(lba * 2048)
            dir_data = iso_f.read(size)
            pos = 0
            entries = {}
            while pos < len(dir_data):
                rec_len = dir_data[pos]
                if rec_len == 0:
                    next_sec = ((pos // 2048) + 1) * 2048
                    if next_sec < len(dir_data):
                        pos = next_sec
                        continue
                    else:
                        break
                rec = dir_data[pos:pos+rec_len]
                sec_loc, = struct.unpack_from('<I', rec, 2)
                data_len, = struct.unpack_from('<I', rec, 10)
                flags = rec[25]
                name_len = rec[32]
                name = rec[33:33+name_len].decode('ascii', errors='replace').split(';')[0]
                if name not in ('\x00', '\x01'):
                    full_p = f"{prefix}/{name}" if prefix else name
                    is_dir = bool(flags & 2)
                    entries[full_p] = {
                        'dir_lba': lba,
                        'dir_offset': pos,
                        'file_lba': sec_loc,
                        'file_size': data_len,
                        'is_dir': is_dir,
                        'rec_len': rec_len
                    }
                    if is_dir:
                        sub = scan_dir(sec_loc, data_len, full_p)
                        entries.update(sub)
                pos += rec_len
            return entries

        file_map = scan_dir(root_lba, root_size)
        
        # Find next available LBA at end of ISO
        max_lba = vol_space_size
        for info in file_map.values():
            end_lba = info['file_lba'] + (info['file_size'] + 2047) // 2048
            if end_lba > max_lba:
                max_lba = end_lba

        for rel_path, data_or_path in replacements.items():
            norm_key = rel_path.replace('\\', '/').lstrip('/')
            if norm_key not in file_map:
                raise KeyError(f"File '{rel_path}' not found in ISO image")
                
            entry = file_map[norm_key]
            if isinstance(data_or_path, str):
                with open(data_or_path, 'rb') as f:
                    new_bytes = f.read()
            else:
                new_bytes = data_or_path
                
            new_size = len(new_bytes)
            new_sectors = (new_size + 2047) // 2048
            old_sectors = (entry['file_size'] + 2047) // 2048
            
            if new_sectors <= old_sectors:
                # Can write in-place
                target_lba = entry['file_lba']
                print(f"Writing in-place for '{norm_key}' at LBA {target_lba} ({new_size} bytes)")
            else:
                # Append at end of ISO
                target_lba = max_lba
                max_lba += new_sectors
                print(f"Appending '{norm_key}' at end of ISO at LBA {target_lba} ({new_size} bytes)")
                
            # Write file payload
            iso_f.seek(target_lba * 2048)
            iso_f.write(new_bytes)
            pad = (new_sectors * 2048) - new_size
            if pad:
                iso_f.write(b'\x00' * pad)
                
            # Update directory record (both little-endian and big-endian)
            dir_pos = entry['dir_lba'] * 2048 + entry['dir_offset']
            iso_f.seek(dir_pos)
            rec = bytearray(iso_f.read(entry['rec_len']))
            
            # Pack LBA: LE at +2, BE at +6
            struct.pack_into('<I', rec, 2, target_lba)
            struct.pack_into('>I', rec, 6, target_lba)
            # Pack Data Size: LE at +10, BE at +14
            struct.pack_into('<I', rec, 10, new_size)
            struct.pack_into('>I', rec, 14, new_size)
            
            iso_f.seek(dir_pos)
            iso_f.write(rec)
            
        # Update PVD VolumeSpaceSize if max_lba changed
        if max_lba > vol_space_size:
            struct.pack_into('<I', pvd, 80, max_lba)
            struct.pack_into('>I', pvd, 84, max_lba)
            iso_f.seek(16 * 2048)
            iso_f.write(pvd)
            print(f"Updated PVD VolumeSpaceSize to {max_lba} sectors ({max_lba * 2048} bytes)")
            
    print(f"Successfully patched ISO: {output_iso_path}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: iso.py <orig_iso> <file_in_iso> <replacement_file> <output_iso>")
        sys.exit(1)
    patch_iso(sys.argv[1], {sys.argv[2]: sys.argv[3]}, sys.argv[4])
