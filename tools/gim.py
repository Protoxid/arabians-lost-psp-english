#!/usr/bin/env python3
"""
Sony PSP GIM Texture Decoder and Encoder for Arabians Lost.
Supports 8-bit indexed swizzled textures with RGBA8888 palettes.
"""

import os
import sys
import struct
from PIL import Image

def unswizzle_8bpp(src: bytes, width: int, height: int) -> bytearray:
    stride = ((width + 15) // 16) * 16
    rowblocks = stride // 16
    dest = bytearray(width * height)
    
    for y in range(height):
        for x in range(width):
            blockx = x // 16
            blocky = y // 8
            x_in_block = x % 16
            y_in_block = y % 8
            src_idx = (blocky * rowblocks + blockx) * 128 + y_in_block * 16 + x_in_block
            if src_idx < len(src):
                dest[y * width + x] = src[src_idx]
                
    return dest

def swizzle_8bpp(src: bytes, width: int, height: int) -> bytearray:
    stride = ((width + 15) // 16) * 16
    rowblocks = stride // 16
    total_blocks_y = (height + 7) // 8
    dest = bytearray(total_blocks_y * rowblocks * 128)
    
    for y in range(height):
        for x in range(width):
            blockx = x // 16
            blocky = y // 8
            x_in_block = x % 16
            y_in_block = y % 8
            dest_idx = (blocky * rowblocks + blockx) * 128 + y_in_block * 16 + x_in_block
            dest[dest_idx] = src[y * width + x]
            
    return dest

def decode_gim(gim_path: str, png_path: str):
    with open(gim_path, 'rb') as f:
        data = f.read()

    # Verify GIM header
    if not data.startswith(b'MIG.00.1PSP\x00'):
        raise ValueError(f"Not a valid PSP GIM file: {gim_path}")

    # Palette data is at 0x70
    pal_data = data[0x70 : 0x70 + 1024]
    
    # Image dimensions
    w = struct.unpack_from('<H', data, 0x480 + 0x18)[0]
    h = struct.unpack_from('<H', data, 0x480 + 0x1A)[0]
    
    # Pixel payload at 0x4D0
    raw_pixels = data[0x4D0 :]
    pixels = unswizzle_8bpp(raw_pixels, w, h)
    
    img = Image.new('RGBA', (w, h))
    pix = img.load()
    for y in range(h):
        for x in range(w):
            idx = pixels[y * w + x]
            r = pal_data[idx * 4]
            g = pal_data[idx * 4 + 1]
            b = pal_data[idx * 4 + 2]
            a = pal_data[idx * 4 + 3]
            pix[x, y] = (r, g, b, a)
            
    os.makedirs(os.path.dirname(os.path.abspath(png_path)), exist_ok=True)
    img.save(png_path)
    return img

def encode_gim_from_template(png_path: str, template_gim_path: str, out_gim_path: str):
    """
    Encodes an edited PNG image back into GIM format using the template GIM's header and palette.
    """
    with open(template_gim_path, 'rb') as f:
        template_data = bytearray(f.read())
        
    img = Image.open(png_path).convert('RGBA')
    w, h = img.size
    
    template_w = struct.unpack_from('<H', template_data, 0x480 + 0x18)[0]
    template_h = struct.unpack_from('<H', template_data, 0x480 + 0x1A)[0]
    if (w, h) != (template_w, template_h):
        raise ValueError(f"Image dimensions {w}x{h} do not match template {template_w}x{template_h}")
        
    pal_data = template_data[0x70 : 0x70 + 1024]
    # Build reverse palette lookup: (r, g, b, a) -> index
    pal_map = {}
    for i in range(256):
        r = pal_data[i * 4]
        g = pal_data[i * 4 + 1]
        b = pal_data[i * 4 + 2]
        a = pal_data[i * 4 + 3]
        pal_map[(r, g, b, a)] = i
        
    # Helper to find closest color in palette if exact match doesn't exist
    def get_closest_palette_index(r, g, b, a):
        if (r, g, b, a) in pal_map:
            return pal_map[(r, g, b, a)]
        # Nearest neighbor euclidean distance in RGBA space
        best_idx = 0
        best_dist = float('inf')
        for i in range(256):
            pr = pal_data[i * 4]
            pg = pal_data[i * 4 + 1]
            pb = pal_data[i * 4 + 2]
            pa = pal_data[i * 4 + 3]
            dist = (r - pr)**2 + (g - pg)**2 + (b - pb)**2 + (a - pa)**2
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        return best_idx

    linear_bytes = bytearray(w * h)
    pix = img.load()
    for y in range(h):
        for x in range(w):
            rgba = pix[x, y]
            linear_bytes[y * w + x] = get_closest_palette_index(*rgba)
            
    # Reswizzle
    swizzled = swizzle_8bpp(linear_bytes, w, h)
    
    # Overwrite pixel payload in template
    template_data[0x4D0 : 0x4D0 + len(swizzled)] = swizzled
    
    os.makedirs(os.path.dirname(os.path.abspath(out_gim_path)), exist_ok=True)
    with open(out_gim_path, 'wb') as f:
        f.write(template_data)
        
    return len(template_data)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python tools/gim.py decode <in.gim> <out.png>")
        print("  python tools/gim.py encode <in.png> <template.gim> <out.gim>")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == 'decode':
        decode_gim(sys.argv[2], sys.argv[3])
        print(f"Decoded {sys.argv[2]} -> {sys.argv[3]}")
    elif cmd == 'encode':
        encode_gim_from_template(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Encoded {sys.argv[2]} -> {sys.argv[4]}")
