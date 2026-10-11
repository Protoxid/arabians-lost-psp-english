#!/usr/bin/env python3
"""
Localize all system banners, autosave notices, and confirmation dialogs in:
sysmedia/sysimage/common/
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

sys.path.insert(0, os.path.abspath('.'))
from tools.gim import decode_gim, encode_gim_from_template

FONT_SERIF_BOLD = r'C:\Windows\Fonts\georgiab.ttf'

GOLD_BANNERS = {
    'bnr_load': ['System data loaded.'],
    'bnr_save1': ['Saving system data.', 'Do not remove the Memory Stick™.'],
    'bnr_save2': ['System data saved.'],
    'bnr_start': [
        'This game supports autosave.',
        'Do not remove the Memory Stick™',
        'while access lamp is blinking.'
    ],
    'bnr_font': ['Loading font...', 'Please wait a moment.'],
    'bnr_capt': ['Capturing screenshot.', 'Do not remove the Memory Stick™.'],
}

PURPLE_DIALOGS = {
    'dlog_qsave': ['Quick Save?'],
    'dlog_qload': ['Quick Load?'],
    'dlog_title': ['Return to Title Screen?'],
    'dlog_reset': ['Reset settings to default?'],
    'dlog_ndat': ['System data was not found.', 'Create new system data?'],
    'dlog_emem': ['Exit Memory Recall?'],
}

def make_blank_gold():
    orig_path = 'extracted/data_cpk/sysmedia/sysimage/common/bnr_load.gim'
    png_path = 'scratch/common_png/bnr_load.png'
    decode_gim(orig_path, png_path)
    im = cv2.imread(png_path)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    mask = np.zeros(gray.shape, dtype=np.uint8)
    text_region = (gray < 110)
    region_mask = np.zeros_like(gray, dtype=bool)
    region_mask[25:75, 40:325] = True
    mask[text_region & region_mask] = 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.dilate(mask, kernel, iterations=2)
    inpainted = cv2.inpaint(im, mask, 3, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)).convert('RGBA')

def make_blank_purple():
    orig_path = 'extracted/data_cpk/sysmedia/sysimage/common/dlog_qsave.gim'
    png_path = 'scratch/common_png/dlog_qsave.png'
    decode_gim(orig_path, png_path)
    im = cv2.imread(png_path)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    mask = np.zeros(gray.shape, dtype=np.uint8)
    text_region = (gray < 110)
    region_mask = np.zeros_like(gray, dtype=bool)
    region_mask[20:75, 40:325] = True
    mask[text_region & region_mask] = 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.dilate(mask, kernel, iterations=2)
    inpainted = cv2.inpaint(im, mask, 3, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)).convert('RGBA')

def render_banner_text(bg_image: Image.Image, lines: list, text_color=(58, 32, 18, 255), shadow_color=(240, 220, 170, 180)):
    im = bg_image.copy()
    draw = ImageDraw.Draw(im)
    w, h = im.size
    
    if len(lines) == 1:
        font = ImageFont.truetype(FONT_SERIF_BOLD, 16)
        line_spacing = 0
    elif len(lines) == 2:
        font = ImageFont.truetype(FONT_SERIF_BOLD, 14)
        line_spacing = 4
    else:
        font = ImageFont.truetype(FONT_SERIF_BOLD, 12)
        line_spacing = 3

    # Calculate total block height
    line_bboxes = [font.getbbox(l) for l in lines]
    line_heights = [b[3] - b[1] for b in line_bboxes]
    line_widths = [b[2] - b[0] for b in line_bboxes]
    total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)
    
    start_y = (h - total_text_h) // 2 - 2
    cur_y = start_y
    for i, line in enumerate(lines):
        lw = line_widths[i]
        lh = line_heights[i]
        lx = (w - lw) // 2
        # Drop shadow / glow
        draw.text((lx + 1, cur_y + 1), line, font=font, fill=shadow_color)
        # Main text
        draw.text((lx, cur_y), line, font=font, fill=text_color)
        cur_y += lh + line_spacing

    return im

def render_buttons():
    # dlog_btny: 50x36, top is <Yes>, bottom is Yes
    # dlog_btnn: 50x36, top is <No>, bottom is No
    btn_defs = {
        'dlog_btny': ('<Yes>', 'Yes'),
        'dlog_btnn': ('<No>', 'No'),
    }
    font = ImageFont.truetype(FONT_SERIF_BOLD, 13)
    results = {}
    for bname, (top_text, bot_text) in btn_defs.items():
        im = Image.new('RGBA', (50, 36), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        
        # Top text (selected): y center = 9
        bbox_top = font.getbbox(top_text)
        tw_t, th_t = bbox_top[2] - bbox_top[0], bbox_top[3] - bbox_top[1]
        tx_t = (50 - tw_t) // 2
        ty_t = 9 - th_t // 2 - 1
        draw.text((tx_t + 1, ty_t + 1), top_text, font=font, fill=(240, 220, 170, 180))
        draw.text((tx_t, ty_t), top_text, font=font, fill=(58, 32, 18, 255))
        
        # Bottom text (unselected): y center = 27
        bbox_bot = font.getbbox(bot_text)
        tw_b, th_b = bbox_bot[2] - bbox_bot[0], bbox_bot[3] - bbox_bot[1]
        tx_b = (50 - tw_b) // 2
        ty_b = 27 - th_b // 2 - 1
        draw.text((tx_b + 1, ty_b + 1), bot_text, font=font, fill=(240, 220, 170, 180))
        draw.text((tx_b, ty_b), bot_text, font=font, fill=(90, 60, 45, 230))
        
        results[bname] = im
    return results

def main():
    os.makedirs('translations/graphics/sysmedia/sysimage/common', exist_ok=True)
    os.makedirs('scratch/localized_common_png', exist_ok=True)
    
    blank_gold = make_blank_gold()
    blank_purple = make_blank_purple()
    
    # 1. Gold banners
    for name, lines in GOLD_BANNERS.items():
        png_out = f'scratch/localized_common_png/{name}.png'
        gim_out = f'translations/graphics/sysmedia/sysimage/common/{name}.gim'
        tmpl_gim = f'extracted/data_cpk/sysmedia/sysimage/common/{name}.gim'
        
        im = render_banner_text(blank_gold, lines, text_color=(58, 32, 18, 255), shadow_color=(240, 220, 170, 180))
        im.save(png_out)
        encode_gim_from_template(png_out, tmpl_gim, gim_out)
        print(f"Encoded gold banner: {name}.gim")

    # 2. Purple dialogs
    for name, lines in PURPLE_DIALOGS.items():
        png_out = f'scratch/localized_common_png/{name}.png'
        gim_out = f'translations/graphics/sysmedia/sysimage/common/{name}.gim'
        tmpl_gim = f'extracted/data_cpk/sysmedia/sysimage/common/{name}.gim'
        
        im = render_banner_text(blank_purple, lines, text_color=(58, 32, 18, 255), shadow_color=(240, 220, 200, 180))
        im.save(png_out)
        encode_gim_from_template(png_out, tmpl_gim, gim_out)
        print(f"Encoded purple dialog: {name}.gim")

    # 3. Buttons
    btn_imgs = render_buttons()
    for name, im in btn_imgs.items():
        png_out = f'scratch/localized_common_png/{name}.png'
        gim_out = f'translations/graphics/sysmedia/sysimage/common/{name}.gim'
        tmpl_gim = f'extracted/data_cpk/sysmedia/sysimage/common/{name}.gim'
        
        im.save(png_out)
        encode_gim_from_template(png_out, tmpl_gim, gim_out)
        print(f"Encoded dialog button: {name}.gim")

    print("\nAll 14 common dialog & banner graphics localized successfully!")

if __name__ == '__main__':
    main()
