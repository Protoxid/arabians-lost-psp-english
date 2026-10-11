# Arabians Lost (PSP) — English Patch Installation Guide

## Requirements

1. A legal, unmodified backup image of **Arabians Lost: The Engagement on Desert (ULJM06104)** in ISO format.
2. The patch file `ArabiansLost_English_v1.0.xdelta`.
3. An xdelta3 patching tool or the included Python script.

---

## Method 1: Using the Included Python Script (Recommended)

Run the following command from the project root:

```bash
python tools/apply_patch.py <path_to_original.iso> release/ArabiansLost_English_v1.0.xdelta ArabiansLost_English.iso
```

The script will automatically:
1. Verify that your source ISO matches the required SHA-256 (`5eddbb1bb87bc88f4efa380826276cd605fe65dac0c8beee73b64d7e91be110e`).
2. Apply the patch in under one second.
3. Validate that the output image matches the verified English release hash.

---

## Method 2: Using the xdelta3 Command-Line Tool

If you prefer standard xdelta3:

```bash
xdelta3 -d -s original.iso ArabiansLost_English_v1.0.xdelta ArabiansLost_English.iso
```

---

## Playing on Emulator or Hardware

- **PPSSPP:** Load `ArabiansLost_English.iso` directly into PPSSPP. No custom plugins or texture replacements are required. All English text renders natively.
- **Real PSP Hardware:** Copy `ArabiansLost_English.iso` to the `ISO/` folder of your Memory Stick on a custom-firmware enabled PSP (PRO, ME, or ARK).

---

## ☕ Support Future Translations

If you find this translation helpful and want to support upcoming projects or patch updates:  
👉 **[Buy a coffee on Ko-fi](https://ko-fi.com/protoxide)**

