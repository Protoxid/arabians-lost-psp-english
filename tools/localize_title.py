import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from PIL import Image, ImageDraw, ImageFont
from tools.gim import encode_gim_from_template

TITLES = {
    'title_0': 'New Game',
    'title_1': 'Continue',
    'title_2': 'CG Gallery',
    'title_3': 'Scene Recall',
    'title_4': 'Options',
    'title_5': 'Data Install',
    'title_6': 'Uninstall'
}

font_path = r'C:\Windows\Fonts\georgia.ttf'
font = ImageFont.truetype(font_path, 15)

os.makedirs('extracted/graphics/title_eng', exist_ok=True)
os.makedirs('build/title_eng_gim', exist_ok=True)

for name, eng_text in TITLES.items():
    orig_png = f'extracted/graphics/title/{name}.png'
    template_gim = f'extracted/data_cpk/sysmedia/sysimage/title/{name}.gim'
    
    im = Image.open(orig_png).convert('RGBA')
    draw = ImageDraw.Draw(im)
    
    # 1. Clear text area on banners
    # Top banner interior
    draw.rectangle([34, 9, 168, 24], fill=(146, 198, 181, 255))
    # Bottom banner interior
    draw.rectangle([34, 44, 168, 59], fill=(235, 222, 175, 255))
    
    # Get text dimensions
    bbox = font.getbbox(eng_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    cx = (34 + 168) // 2
    tx = cx - tw // 2
    
    # Center y for top banner (y=9..24, center=16.5)
    ty_top = 8 + (16 - th) // 2
    # Center y for bottom banner (y=44..59, center=51.5)
    ty_bot = 43 + (16 - th) // 2
    
    # Top state: white text with dark border (105, 80, 50)
    border_color_top = (75, 55, 30, 255)
    fill_color_top = (255, 255, 255, 255)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((tx + dx, ty_top + dy), eng_text, font=font, fill=border_color_top)
    draw.text((tx, ty_top), eng_text, font=font, fill=fill_color_top)
    
    # Bottom state: golden-brown text with subtle dark shadow
    border_color_bot = (95, 75, 45, 255)
    fill_color_bot = (110, 85, 45, 255)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((tx + dx, ty_bot + dy), eng_text, font=font, fill=border_color_bot)
    draw.text((tx, ty_bot), eng_text, font=font, fill=(245, 235, 205, 255)) # Warm cream fill with dark border
    
    out_png = f'extracted/graphics/title_eng/{name}.png'
    im.save(out_png)
    
    out_gim = f'build/title_eng_gim/{name}.gim'
    encode_gim_from_template(out_png, template_gim, out_gim)
    print(f"Generated {out_png} and {out_gim}")
