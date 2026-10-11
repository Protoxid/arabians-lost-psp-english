#!/usr/bin/env python3
"""
CRI Middleware CPK archive parser, extractor, and packer for Arabians Lost (PSP).
Supports @UTF table decoding/encoding and CRILAYLA decompression.
"""

import os
import sys
import struct
import json
from typing import List, Dict, Any, Tuple, Optional
from tools.crilayla import decompress as crilayla_decompress

STORAGE_NONE = 0x00
STORAGE_ZERO = 0x10
STORAGE_CONSTANT = 0x30
STORAGE_PERROW = 0x50

TYPE_UINT8 = 0
TYPE_INT8 = 1
TYPE_UINT16 = 2
TYPE_INT16 = 3
TYPE_UINT32 = 4
TYPE_INT32 = 5
TYPE_UINT64 = 6
TYPE_INT64 = 7
TYPE_FLOAT = 8
TYPE_STRING = 0xa
TYPE_DATA = 0xb

TYPES_SIZES = {
    TYPE_UINT8: 1, TYPE_INT8: 1,
    TYPE_UINT16: 2, TYPE_INT16: 2,
    TYPE_UINT32: 4, TYPE_INT32: 4,
    TYPE_UINT64: 8, TYPE_INT64: 8,
    TYPE_FLOAT: 4,
    TYPE_STRING: 4,
    TYPE_DATA: 8
}

class UtfTable:
    def __init__(self, name: str = ""):
        self.name = name
        self.columns: List[Dict[str, Any]] = []
        self.rows: List[Dict[str, Any]] = []

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> 'UtfTable':
        magic = data[offset:offset+4]
        if magic != b'@UTF':
            raise ValueError(f"Expected @UTF magic at 0x{offset:x}, got {magic}")
        
        table_size, = struct.unpack_from('>I', data, offset + 4)
        rows_offset, strings_offset, data_offset, table_name_offset = struct.unpack_from('>IIII', data, offset + 8)
        num_cols, row_len, num_rows = struct.unpack_from('>HHI', data, offset + 24)
        
        strings_base = offset + 8 + strings_offset
        data_base = offset + 8 + data_offset
        rows_base = offset + 8 + rows_offset
        
        def get_string(str_off: int) -> str:
            if str_off == 0:
                # Often offset 0 is empty string or <NULL>
                pass
            end = data.find(b'\x00', strings_base + str_off)
            if end == -1:
                return ""
            return data[strings_base + str_off:end].decode('utf-8', errors='replace')

        table_name = get_string(table_name_offset)
        table = cls(name=table_name)
        
        curr = offset + 32
        for i in range(num_cols):
            col_type = data[curr]
            name_off, = struct.unpack_from('>I', data, curr + 1)
            name = get_string(name_off)
            curr += 5
            
            storage_type = col_type & 0xF0
            data_type = col_type & 0x0F
            constant_val = None
            
            if storage_type == STORAGE_CONSTANT:
                if data_type in (TYPE_UINT8, TYPE_INT8):
                    constant_val = data[curr]
                    curr += 1
                elif data_type in (TYPE_UINT16, TYPE_INT16):
                    constant_val, = struct.unpack_from('>H', data, curr)
                    curr += 2
                elif data_type in (TYPE_UINT32, TYPE_INT32):
                    constant_val, = struct.unpack_from('>I', data, curr)
                    curr += 4
                elif data_type in (TYPE_UINT64, TYPE_INT64):
                    constant_val, = struct.unpack_from('>Q', data, curr)
                    curr += 8
                elif data_type == TYPE_FLOAT:
                    constant_val, = struct.unpack_from('>f', data, curr)
                    curr += 4
                elif data_type == TYPE_STRING:
                    str_off, = struct.unpack_from('>I', data, curr)
                    constant_val = get_string(str_off)
                    curr += 4
                elif data_type == TYPE_DATA:
                    b_off, b_len = struct.unpack_from('>II', data, curr)
                    constant_val = data[data_base + b_off: data_base + b_off + b_len]
                    curr += 8

            table.columns.append({
                'name': name,
                'type': col_type,
                'storage': storage_type,
                'data_type': data_type,
                'constant': constant_val
            })
            
        for r in range(num_rows):
            row_dict = {}
            row_curr = rows_base + r * row_len
            for col in table.columns:
                storage = col['storage']
                dtype = col['data_type']
                name = col['name']
                
                if storage == STORAGE_CONSTANT:
                    row_dict[name] = col['constant']
                elif storage == STORAGE_ZERO:
                    row_dict[name] = 0 if dtype != TYPE_STRING else ""
                elif storage == STORAGE_PERROW:
                    if dtype in (TYPE_UINT8, TYPE_INT8):
                        row_dict[name] = data[row_curr]
                        row_curr += 1
                    elif dtype in (TYPE_UINT16, TYPE_INT16):
                        row_dict[name], = struct.unpack_from('>H', data, row_curr)
                        row_curr += 2
                    elif dtype in (TYPE_UINT32, TYPE_INT32):
                        row_dict[name], = struct.unpack_from('>I', data, row_curr)
                        row_curr += 4
                    elif dtype in (TYPE_UINT64, TYPE_INT64):
                        row_dict[name], = struct.unpack_from('>Q', data, row_curr)
                        row_curr += 8
                    elif dtype == TYPE_FLOAT:
                        row_dict[name], = struct.unpack_from('>f', data, row_curr)
                        row_curr += 4
                    elif dtype == TYPE_STRING:
                        str_off, = struct.unpack_from('>I', data, row_curr)
                        row_dict[name] = get_string(str_off)
                        row_curr += 4
                    elif dtype == TYPE_DATA:
                        b_off, b_len = struct.unpack_from('>II', data, row_curr)
                        row_dict[name] = data[data_base + b_off: data_base + b_off + b_len]
                        row_curr += 8
            table.rows.append(row_dict)
            
        return table


class CpkArchive:
    def __init__(self, cpk_path: str):
        self.cpk_path = cpk_path
        self.header: Dict[str, Any] = {}
        self.files: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        with open(self.cpk_path, 'rb') as f:
            magic = f.read(4)
            if magic != b'CPK ':
                raise ValueError(f"Invalid CPK magic: {magic}")
            
            # Read CPK header @UTF table
            f.seek(16)
            hdr_bytes = f.read(4096)
            hdr_table = UtfTable.from_bytes(hdr_bytes, 0)
            self.header = hdr_table.rows[0]
            
            toc_offset = self.header.get('TocOffset', 0)
            toc_size = self.header.get('TocSize', 0)
            if not toc_offset:
                raise ValueError("No TocOffset found in CPK header")
            
            # Read TOC @UTF table
            f.seek(toc_offset + 16)
            toc_bytes = f.read(toc_size)
            toc_table = UtfTable.from_bytes(toc_bytes, 0)
            
            for row in toc_table.rows:
                dirname = row.get('DirName', '')
                filename = row.get('FileName', '')
                if dirname:
                    rel_path = f"{dirname}/{filename}"
                else:
                    rel_path = filename
                
                self.files.append({
                    'id': row.get('ID', 0),
                    'dir_name': dirname,
                    'file_name': filename,
                    'rel_path': rel_path,
                    'file_size': row.get('FileSize', 0),
                    'extract_size': row.get('ExtractSize', 0),
                    'file_offset': row.get('FileOffset', 0),
                    # FileOffset in TOC is relative to TocOffset
                    'abs_offset': toc_offset + row.get('FileOffset', 0)
                })

    def extract_file(self, file_entry: Dict[str, Any], decompress_if_needed: bool = True) -> bytes:
        with open(self.cpk_path, 'rb') as f:
            f.seek(file_entry['abs_offset'])
            data = f.read(file_entry['file_size'])
            
        if decompress_if_needed and data[:8] == b'CRILAYLA':
            return crilayla_decompress(data)
        return data

    def extract_all(self, output_dir: str, decompress: bool = True):
        os.makedirs(output_dir, exist_ok=True)
        total = len(self.files)
        print(f"Extracting {total} files from {self.cpk_path} to {output_dir}...")
        for i, entry in enumerate(self.files):
            out_path = os.path.join(output_dir, entry['rel_path'].replace('/', os.sep))
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            data = self.extract_file(entry, decompress_if_needed=decompress)
            with open(out_path, 'wb') as out_f:
                out_f.write(data)
            if (i + 1) % 500 == 0 or (i + 1) == total:
                print(f"  [{i+1}/{total}] Extracted {entry['rel_path']}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python cpk.py <cpk_path> <output_dir>")
        sys.exit(1)
    cpk = CpkArchive(sys.argv[1])
    print(f"Loaded CPK: {len(cpk.files)} files, Align={cpk.header.get('Align')}")
    cpk.extract_all(sys.argv[2])

if __name__ == '__main__':
    main()
