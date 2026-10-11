import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from PIL import Image, ImageDraw, ImageFont
from tools.gim import decode_gim, encode_gim_from_template

NAME_MAP = {
    'nam_almeida': 'Almeida',
    'nam_aric': 'Aric',
    'nam_bartender': 'Bartender',
    'nam_buka': 'Henchman',
    'nam_cejka': 'Cejka',
    'nam_curtis': 'Curtis',
    'nam_dealer': 'Dealer',
    'nam_eugine': 'Eugine',
    'nam_hatena': '???',
    'nam_idit': 'Idit',
    'nam_joshua': 'Joshua',
    'nam_king': 'King',
    'nam_lille': 'Lyle',
    'nam_man': 'Man',
    'nam_maze': 'Maze',
    'nam_meissen': 'Meisen',
    'nam_michael': 'Michael',
    'nam_queen': 'Queen',
    'nam_roberto': 'Roberto',
    'nam_roley': 'Roley',
    'nam_shark': 'Shark',
    'nam_stuart': 'Stuart',
    'nam_totem': 'Totam',
    'nam_tyrone': 'Tyrone',
    'nam_woman': 'Woman',
    'nam_yuu': 'Yuuma',
}

font_path = r'C:\Windows\Fonts\georgiab.ttf'
font = ImageFont.truetype(font_path, 12)
font_small = ImageFont.truetype(font_path, 11)

out_gim_dir = 'translations/graphics/image'
os.makedirs(out_gim_dir, exist_ok=True)
os.makedirs('scratch/nameplates_localized_png', exist_ok=True)

for gim_id, text in NAME_MAP.items():
    orig_gim = f'extracted/data_cpk/image/{gim_id}.gim'
    if not os.path.exists(orig_gim):
        print(f"Warning: {orig_gim} not found!")
        continue
        
    temp_orig_png = f'scratch/nameplates_orig/{gim_id}.png'
    if not os.path.exists(temp_orig_png):
        decode_gim(orig_gim, temp_orig_png)
        
    im = Image.open(temp_orig_png).convert('RGBA')
    
    # 1. Erase original Japanese text cleanly by sampling left plaque background
    # The wooden plaque background is between y=3..18 and x=15..88
    for y in range(3, 19):
        colors = [im.getpixel((x, y)) for x in range(15, 25)]
        avg_r = sum(c[0] for c in colors) // len(colors)
        avg_g = sum(c[1] for c in colors) // len(colors)
        avg_b = sum(c[2] for c in colors) // len(colors)
        avg_a = sum(c[3] for c in colors) // len(colors)
        for x in range(16, 88):
            im.putpixel((x, y), (avg_r, avg_g, avg_b, avg_a))
            
    # 2. Draw English name
    draw = ImageDraw.Draw(im)
    use_font = font_small if len(text) >= 8 else font
    bbox = use_font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    cx = 52
    cy = 11
    tx = cx - tw // 2
    ty = cy - th // 2 - 1
    
    # Subtle drop shadow
    draw.text((tx + 1, ty + 1), text, font=use_font, fill=(20, 10, 10, 220))
    # Elegant cream lettering
    draw.text((tx, ty), text, font=use_font, fill=(255, 248, 235, 255))
    
    out_png = f'scratch/nameplates_localized_png/{gim_id}.png'
    im.save(out_png)
    
    out_gim = os.path.join(out_gim_dir, f'{gim_id}.gim')
    encode_gim_from_template(out_png, orig_gim, out_gim)
    print(f"Localized {gim_id}.gim: '{text}' -> {out_gim}")

print(f"\nSuccessfully localized all {len(NAME_MAP)} character nameplates!")
