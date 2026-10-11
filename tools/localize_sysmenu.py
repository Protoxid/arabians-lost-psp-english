import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from PIL import Image, ImageDraw, ImageFont
from tools.gim import encode_gim_from_template, decode_gim

BTN_TEXTS = {
    'sys_btn_0': 'Save',
    'sys_btn_1': 'Load',
    'sys_btn_2': 'Display',
    'sys_btn_3': 'Volume',
    'sys_btn_4': 'Sound',
    'sys_btn_5': 'Voice',
    'sys_btn_6': 'Mute',
    'sys_btn_7': 'Recall',
    'sys_btn_8': 'Reset',
    'sys_btn_9': 'Title',
}

BANNER_BTNS = {
    'sys_btn_back': 'Back',
    'sys_btn_use': 'Use',
}

font_path = r'C:\Windows\Fonts\georgia.ttf'
font_btn = ImageFont.truetype(font_path, 13)
font_banner = ImageFont.truetype(font_path, 12)

out_gim_dir = 'translations/graphics/sysmedia/sysimage/sysmenu'
os.makedirs(out_gim_dir, exist_ok=True)
os.makedirs('scratch/sysmenu_localized_png', exist_ok=True)

# 1. Process sys_btn_0 through 9
for btn_name, text in BTN_TEXTS.items():
    orig_png = f'qa/sysmenu_png/{btn_name}.png'
    template_gim = f'extracted/data_cpk/sysmedia/sysimage/sysmenu/{btn_name}.gim'
    
    im = Image.open(orig_png).convert('RGBA')
    draw = ImageDraw.Draw(im)
    
    # We clean the text region on both top flask (y=22..40) and bottom flask (y=92..110)
    # Sample background color in the liquid area of flask
    # Top flask liquid center: (43, 31)
    # Bottom flask liquid center: (43, 101)
    
    # Render text for top state
    bbox = font_btn.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    cx = 43
    tx = cx - tw // 2
    ty_top = 22 + (16 - th) // 2
    ty_bot = 92 + (16 - th) // 2
    
    # Clean text area slightly with a smooth darkened glass patch
    # Draw soft pill behind text to conceal Japanese kanji cleanly
    pad_x = 4
    pad_y = 2
    draw.rounded_rectangle([tx - pad_x, ty_top - pad_y, tx + tw + pad_x, ty_top + th + pad_y + 2], radius=3, fill=(35, 25, 20, 210))
    draw.rounded_rectangle([tx - pad_x, ty_bot - pad_y, tx + tw + pad_x, ty_bot + th + pad_y + 2], radius=3, fill=(30, 45, 40, 220))
    
    # Outline + text for top
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((tx + dx, ty_top + dy), text, font=font_btn, fill=(40, 20, 10, 255))
    draw.text((tx, ty_top), text, font=font_btn, fill=(255, 250, 235, 255))
    
    # Outline + text for bottom (highlighted state)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((tx + dx, ty_bot + dy), text, font=font_btn, fill=(20, 50, 40, 255))
    draw.text((tx, ty_bot), text, font=font_btn, fill=(240, 255, 250, 255))
    
    out_png = f'scratch/sysmenu_localized_png/{btn_name}.png'
    im.save(out_png)
    
    out_gim = os.path.join(out_gim_dir, f'{btn_name}.gim')
    encode_gim_from_template(out_png, template_gim, out_gim)
    print(f"Localized {btn_name}: '{text}' -> {out_gim}")

# 2. Process sys_btn_back and sys_btn_use
for btn_name, text in BANNER_BTNS.items():
    orig_png = f'qa/sysmenu_png/{btn_name}.png'
    template_gim = f'extracted/data_cpk/sysmedia/sysimage/sysmenu/{btn_name}.gim'
    
    im = Image.open(orig_png).convert('RGBA')
    draw = ImageDraw.Draw(im)
    
    # Banner area for text is x=40..88, y=6..24
    # Fill the parchment interior to erase Japanese text
    draw.rectangle([42, 6, 86, 24], fill=(238, 224, 150, 255))
    
    bbox = font_banner.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    cx = (42 + 86) // 2
    tx = cx - tw // 2
    ty = 6 + (18 - th) // 2
    
    # Dark brown outline with gold/cream fill
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((tx + dx, ty + dy), text, font=font_banner, fill=(65, 45, 20, 255))
    draw.text((tx, ty), text, font=font_banner, fill=(255, 245, 215, 255))
    
    out_png = f'scratch/sysmenu_localized_png/{btn_name}.png'
    im.save(out_png)
    
    out_gim = os.path.join(out_gim_dir, f'{btn_name}.gim')
    encode_gim_from_template(out_png, template_gim, out_gim)
    print(f"Localized {btn_name}: '{text}' -> {out_gim}")

print("\nSuccessfully localized all 12 system menu button textures!")
