#!/usr/bin/env python3
"""
High-performance CRI Layla decompression for Arabians Lost (PSP).
Uses Numba JIT acceleration if available (0.9ms per file), with pure Python fallback.
"""

import struct
import numpy as np

try:
    from numba import njit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

if HAS_NUMBA:
    @njit
    def _decompress_core_jit(src, comp_size, decomp_size, dst):
        sbuf_pos = comp_size - 1
        dbuf_pos = decomp_size + 255
        bitcnt = 0
        bitdat = 0
        
        while True:
            if dbuf_pos < 256:
                break

            # get 1 bit
            if bitcnt < 1:
                data_bytes = ((24 - bitcnt) >> 3) + 1
                bitcnt += data_bytes * 8
                while data_bytes > 0:
                    bitdat = (bitdat << 8) | src[sbuf_pos]
                    sbuf_pos -= 1
                    data_bytes -= 1
            b = (bitdat >> (bitcnt - 1)) & 1
            bitcnt -= 1
            
            if b == 0:
                # Literal byte (8 bits)
                if bitcnt < 8:
                    data_bytes = ((24 - bitcnt) >> 3) + 1
                    bitcnt += data_bytes * 8
                    while data_bytes > 0:
                        bitdat = (bitdat << 8) | src[sbuf_pos]
                        sbuf_pos -= 1
                        data_bytes -= 1
                byte = (bitdat >> (bitcnt - 8)) & 0xFF
                bitcnt -= 8
                dst[dbuf_pos] = byte
                dbuf_pos -= 1
            else:
                # Back reference
                # get 13 bits (offset)
                if bitcnt < 13:
                    data_bytes = ((24 - bitcnt) >> 3) + 1
                    bitcnt += data_bytes * 8
                    while data_bytes > 0:
                        bitdat = (bitdat << 8) | src[sbuf_pos]
                        sbuf_pos -= 1
                        data_bytes -= 1
                poffset = (bitdat >> (bitcnt - 13)) & 0x1FFF
                bitcnt -= 13
                
                # get 2 bits (length)
                if bitcnt < 2:
                    data_bytes = ((24 - bitcnt) >> 3) + 1
                    bitcnt += data_bytes * 8
                    while data_bytes > 0:
                        bitdat = (bitdat << 8) | src[sbuf_pos]
                        sbuf_pos -= 1
                        data_bytes -= 1
                plen = (bitdat >> (bitcnt - 2)) & 3
                bitcnt -= 2
                
                if plen == 3:
                    if bitcnt < 3:
                        data_bytes = ((24 - bitcnt) >> 3) + 1
                        bitcnt += data_bytes * 8
                        while data_bytes > 0:
                            bitdat = (bitdat << 8) | src[sbuf_pos]
                            sbuf_pos -= 1
                            data_bytes -= 1
                    plen += (bitdat >> (bitcnt - 3)) & 7
                    bitcnt -= 3
                    
                    if plen == 10:
                        if bitcnt < 5:
                            data_bytes = ((24 - bitcnt) >> 3) + 1
                            bitcnt += data_bytes * 8
                            while data_bytes > 0:
                                bitdat = (bitdat << 8) | src[sbuf_pos]
                                sbuf_pos -= 1
                                data_bytes -= 1
                        plen += (bitdat >> (bitcnt - 5)) & 0x1F
                        bitcnt -= 5
                        
                        if plen == 41:
                            while True:
                                if bitcnt < 8:
                                    data_bytes = ((24 - bitcnt) >> 3) + 1
                                    bitcnt += data_bytes * 8
                                    while data_bytes > 0:
                                        bitdat = (bitdat << 8) | src[sbuf_pos]
                                        sbuf_pos -= 1
                                        data_bytes -= 1
                                byte = (bitdat >> (bitcnt - 8)) & 0xFF
                                bitcnt -= 8
                                plen += byte
                                if byte != 255:
                                    break
                                    
                pbuf = dbuf_pos + poffset + 3
                plen += 3
                while plen > 0:
                    if dbuf_pos < 256:
                        break
                    byte = dst[pbuf]
                    pbuf -= 1
                    dst[dbuf_pos] = byte
                    dbuf_pos -= 1
                    plen -= 1

def decompress(data: bytes) -> bytes:
    if data[:8] != b'CRILAYLA':
        raise ValueError("Not CRILAYLA compressed data")

    decomp_size = struct.unpack_from('<I', data, 8)[0]
    comp_size = struct.unpack_from('<I', data, 12)[0]

    src = bytearray(data[16:16 + comp_size])
    trailer = bytearray(data[16 + comp_size : 16 + comp_size + 256])

    if HAS_NUMBA:
        src_np = np.frombuffer(src, dtype=np.uint8)
        dst_np = np.zeros(256 + decomp_size + 8192, dtype=np.uint8)
        dst_np[:256] = np.frombuffer(trailer, dtype=np.uint8)
        _decompress_core_jit(src_np, comp_size, decomp_size, dst_np)
        return bytes(dst_np[:256 + decomp_size])
    else:
        dst = bytearray(256 + decomp_size + 8192)
        dst[:256] = trailer
        sbuf_pos = comp_size - 1
        dbuf_pos = decomp_size + 255
        bitcnt = 0
        bitdat = 0

        def get_bits(n):
            nonlocal bitcnt, bitdat, sbuf_pos
            if bitcnt < n:
                data_bytes = ((24 - bitcnt) >> 3) + 1
                bitcnt += data_bytes * 8
                while data_bytes:
                    bitdat = (bitdat << 8) | src[sbuf_pos]
                    sbuf_pos -= 1
                    data_bytes -= 1
            result = (bitdat >> (bitcnt - n)) & ((1 << n) - 1)
            bitcnt -= n
            return result

        while True:
            if dbuf_pos < 256:
                break
            if get_bits(1) == 0:
                dst[dbuf_pos] = get_bits(8)
                dbuf_pos -= 1
            else:
                poffset = get_bits(13)
                plen = get_bits(2)
                if plen == 3:
                    plen += get_bits(3)
                    if plen == 10:
                        plen += get_bits(5)
                        if plen == 41:
                            while True:
                                b = get_bits(8)
                                plen += b
                                if b != 255:
                                    break
                pbuf = dbuf_pos + poffset + 3
                plen += 3
                while plen:
                    if dbuf_pos < 256:
                        break
                    dst[dbuf_pos] = dst[pbuf]
                    pbuf -= 1
                    dbuf_pos -= 1
                    plen -= 1
        return bytes(dst[:256 + decomp_size])

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: crilayla.py decompress <input> <output>")
        sys.exit(1)
    with open(sys.argv[2], 'rb') as f:
        comp = f.read()
    dec = decompress(comp)
    with open(sys.argv[3], 'wb') as f:
        f.write(dec)
    print(f"Decompressed: {len(comp)} -> {len(dec)} bytes")
