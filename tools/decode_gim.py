import struct
from PIL import Image

def decode_gim_indexed8(data):
    # Palette is at 0x30
    # Image is at 0x480
    pal_chunk_hdr = data[0x30:0x40]
    pal_data_offset = 0x30 + 16 + struct.unpack_from('<I', data, 0x30 + 16)[0] # Usually at 0x30 + 0x50 = 0x80
    # Let's inspect where the 1024 bytes of palette are
    # And where the pixel bytes are
    print(f"Data length: {len(data)}")
    
    # In Sony GIM specification:
    # Chunk 0x05:
    # 0x00: chunk_type (0x0005)
    # 0x02: chunk_id
    # 0x04: chunk_size (0x450 = 1104 bytes)
    # 0x08: parent_size
    # 0x0C: sibling_size
    # 0x10: header_size (usually 0x50 = 80 bytes)
    # 0x14: reference
    # 0x16: format (0 = RGBA5650, 1 = RGBA5551, 2 = RGBA4444, 3 = RGBA8888)
    # 0x18: order
    # 0x1A: width (256)
    # 0x1C: height (1)
    # Pixel / Palette data starts at 0x30 + header_size
    
    # Let's check header_size at 0x30 + 0x10
    hdr_size = struct.unpack_from('<H', data, 0x40)[0]
    pal_data_start = 0x30 + hdr_size
    pal_bytes = data[pal_data_start : pal_data_start + 1024]
    print(f"Palette start: 0x{pal_data_start:X}, len: {len(pal_bytes)}")
    
    # Image chunk at 0x480:
    img_hdr_size = struct.unpack_from('<H', data, 0x490)[0]
    img_data_start = 0x480 + img_hdr_size
    w, h = struct.unpack_from('<HH', data, 0x480 + 0x1A)
    print(f"Image header size: 0x{img_hdr_size:X}, w={w}, h={h}, data start: 0x{img_data_start:X}")
    
    # PSP texture stride (pitch) is usually aligned to 16 bytes:
    stride = (w + 15) & ~15
    print(f"Stride: {stride}")
    
    img = Image.new('RGBA', (w, h))
    pixels = img.load()
    
    for y in range(h):
        for x in range(w):
            idx = data[img_data_start + y * stride + x]
            # Palette entry
            r = pal_bytes[idx * 4]
            g = pal_bytes[idx * 4 + 1]
            b = pal_bytes[idx * 4 + 2]
            a = pal_bytes[idx * 4 + 3]
            pixels[x, y] = (r, g, b, a)
            
    img.save('qa/screenshots/decoded_title_0.png')
    print("Saved qa/screenshots/decoded_title_0.png!")

with open('extracted/data_cpk/sysmedia/sysimage/title/title_0.gim', 'rb') as f:
    decode_gim_indexed8(f.read())
