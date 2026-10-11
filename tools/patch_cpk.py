#!/usr/bin/env python3
"""
Patch files into CRI CPK archives for Arabians Lost (PSP).
Appends modified files at aligned sector offsets and updates CpkTocInfo records.
"""

import os
import sys
import struct
import shutil
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from typing import Dict, Union

def patch_cpk(orig_cpk_path: str, replacements: Dict[str, Union[bytes, str]], output_cpk_path: str):
    """
    replacements: dict of {'relative/path.ext': bytes_data or local_file_path}
    """
    with open(orig_cpk_path, 'rb') as f:
        magic = f.read(4)
        if magic != b'CPK ':
            raise ValueError(f"Invalid CPK magic: {magic}")
        
        # Read header UTF table to get TocOffset, TocSize, Align
        f.seek(16)
        hdr_utf = f.read(4096)
        
    from tools.cpk import UtfTable
    hdr_table = UtfTable.from_bytes(hdr_utf)
    hdr_row = hdr_table.rows[0]
    
    toc_offset = hdr_row['TocOffset']
    toc_size = hdr_row['TocSize']
    align = hdr_row.get('Align', 2048)
    
    with open(orig_cpk_path, 'rb') as f:
        f.seek(toc_offset + 16)
        toc_bytes = bytearray(f.read(toc_size))
        
    rows_offset, strings_offset, data_offset, table_name_offset = struct.unpack_from('>IIII', toc_bytes, 8)
    rows_base = 8 + rows_offset
    strings_base = 8 + strings_offset
    num_cols, row_len, num_rows = struct.unpack_from('>HHI', toc_bytes, 24)
    
    def get_str(off: int) -> str:
        end = toc_bytes.find(b'\x00', strings_base + off)
        return toc_bytes[strings_base + off:end].decode('utf-8', errors='replace')
        
    # Build map of normalized rel_path -> row index
    toc_file_map = {}
    for r in range(num_rows):
        row_curr = rows_base + r * row_len
        d_off, f_off = struct.unpack_from('>II', toc_bytes, row_curr)
        d_name = get_str(d_off)
        f_name = get_str(f_off)
        full_path = f"{d_name}/{f_name}" if d_name else f_name
        full_path_norm = full_path.replace('\\', '/').lstrip('/')
        toc_file_map[full_path_norm] = r
        toc_file_map[f_name] = r # also map by filename
        
    # Copy original CPK to output
    if orig_cpk_path != output_cpk_path:
        shutil.copyfile(orig_cpk_path, output_cpk_path)
        
    with open(output_cpk_path, 'r+b') as out_f:
        out_f.seek(0, 2)
        current_end = out_f.tell()
        
        for rel_path, data_or_path in replacements.items():
            norm_key = rel_path.replace('\\', '/').lstrip('/')
            if norm_key not in toc_file_map:
                basename = os.path.basename(norm_key)
                if basename not in toc_file_map:
                    raise KeyError(f"File '{rel_path}' not found in CPK TOC")
                row_idx = toc_file_map[basename]
            else:
                row_idx = toc_file_map[norm_key]
                
            if isinstance(data_or_path, str):
                with open(data_or_path, 'rb') as in_f:
                    new_bytes = in_f.read()
            else:
                new_bytes = data_or_path
                
            # Align write position
            aligned_pos = ((current_end + align - 1) // align) * align
            out_f.seek(aligned_pos)
            out_f.write(new_bytes)
            # Pad to alignment
            pad_len = (align - (len(new_bytes) % align)) % align
            if pad_len:
                out_f.write(b'\x00' * pad_len)
            current_end = out_f.tell()
            
            # Update TOC row
            row_pos = rows_base + row_idx * row_len
            new_file_offset = aligned_pos - toc_offset
            new_size = len(new_bytes)
            # Write FileSize, ExtractSize, FileOffset
            struct.pack_into('>IIQ', toc_bytes, row_pos + 8, new_size, new_size, new_file_offset)
            print(f"Patched '{rel_path}': offset=0x{aligned_pos:x} (rel 0x{new_file_offset:x}), size={new_size}")
            
        # Write back updated TOC table
        out_f.seek(toc_offset + 16)
        out_f.write(toc_bytes)
        
    print(f"Successfully updated CPK archive: {output_cpk_path}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: patch_cpk.py <orig_cpk> <rel_path> <replacement_file> <output_cpk>")
        sys.exit(1)
    patch_cpk(sys.argv[1], {sys.argv[2]: sys.argv[3]}, sys.argv[4])
