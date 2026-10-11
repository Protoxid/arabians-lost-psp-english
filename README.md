# *Arabians Lost: The Engagement on Desert* (PSP) — English Fan Translation

[![Platform: PSP](https://img.shields.io/badge/Platform-PSP-003791.svg)](https://en.wikipedia.org/wiki/PlayStation_Portable)
[![Status: Public Beta](https://img.shields.io/badge/Status-Public%20Beta%20v1.0-brightgreen.svg)]()
[![Scenario Coverage: 100%](https://img.shields.io/badge/Scenario-100%25%20Translated-blue.svg)]()
[![License: Non-Commercial Fan Project](https://img.shields.io/badge/License-Non--Commercial%20Fan%20Project-lightgrey.svg)]()

An English fan translation patch for **Arabians Lost: The Engagement on Desert** (*アラビアンズ・ロスト ～The Engagement on Desert～*), the acclaimed Arabian fantasy crime-romance otome visual novel developed by **QuinRose** and released for the PlayStation Portable (**ULJM-06104**).

---

## 📖 Overview

In the lawless desert kingdom of **Gilkhatar**, crime is commerce, and the strongest syndicate rules. Princess **Aileen Olazabal** wants nothing to do with her cutthroat royal heritage—she desires only a normal, peaceful life with an ordinary husband.

Her parents agree to let her break off her arranged marriage on one condition: within **25 days**, she must raise **10,000,000 Gold** on her own through heists, casino wagers, negotiations, and alliances with the most dangerous men in the kingdom:
* **Curtis Nile** — The polite, sociopathic Guildmaster of Assassins.
* **Roberto Cromwell** — The flamboyant casino tycoon and high-stakes gambler.
* **Shark Brandon** — The calculating, laconic president of the Merchants' Guild.
* **Stuart Sink** — The haughty, mysophobic crime family heir.
* **Tyrone Bale** — Stuart's fierce, hot-blooded cousin and enforcer.
* **Lyle Sluman** — Aileen's sarcastic, long-suffering royal tutor.
* **Meisen Hildegarde & Michael Faust** — A wandering eccentric magician and his deadpan contract demon.

---

## 🎮 Translation Status

* **Scenario Dialogue & Narration:** **100% Complete** (all 35,713 scenario records translated).
* **Character Nameplates:** **100% Localized** (all 26 character scroll nameplate textures recreated in English).
* **System UI & Buttons:** **100% Localized** (Save, Load, Options, Recall, Title menus, and confirmation prompts).
* **Typography & Engine Formatting:** Formatted with whole-word wrapping ($\le 18$ characters/line, $\le 4$ lines/box, CP932 ASCII encoding). Zero cut or sliced words.

---

## 💾 Prerequisites

To apply this patch, you must provide your own legally dumped copy of the Japanese PSP game:

| Property | Value |
| :--- | :--- |
| **Game Title** | *Arabians Lost: The Engagement on Desert* |
| **Product ID** | `ULJM-06104` (v1.02) |
| **Region** | Japan (NTSC-J) |
| **Original ISO Size** | `1,158,021,120 bytes` |
| **Original ISO SHA-256** | `5eddbb1bb87bc88f4efa380826276cd605fe65dac0c8beee73b64d7e91be110e` |

---

## 🛠️ How to Apply the Patch

The patch is distributed in standard **xdelta3** format: [`release/ArabiansLost_English_v1.0.xdelta`](release/ArabiansLost_English_v1.0.xdelta).

### Method 1: Online Web Patcher (Easiest — No Install Required)
1. Open [MarcRobledo Rom Patcher JS](https://marcrobledo.com/RomPatcher.js/) or [Romhacking.net Patcher](https://www.romhacking.net/patch/) in any modern web browser.
2. Under **ROM file**, select your untouched Japanese `original.iso`.
3. Under **Patch file**, select [`release/ArabiansLost_English_v1.0.xdelta`](release/ArabiansLost_English_v1.0.xdelta).
4. Click **Apply Patch** and save your patched file as `ArabiansLost_English.iso`.

### Method 2: Delta Patcher (Desktop GUI)
1. Download and open [Delta Patcher](https://www.romhacking.net/utilities/704/).
2. Set **Original file** to your untouched Japanese ISO.
3. Set **XDelta patch** to `ArabiansLost_English_v1.0.xdelta`.
4. Click **Apply patch**.

### Method 3: Command-Line (xdelta3)
```bash
xdelta3 -d -s original.iso release/ArabiansLost_English_v1.0.xdelta ArabiansLost_English.iso
```

### Method 4: Built-in Python Installer
If you have Python installed with `pyxdelta`:
```bash
python tools/apply_patch.py path/to/original.iso release/ArabiansLost_English_v1.0.xdelta build/ArabiansLost_English.iso
```

---

## 🔐 Cryptographic Checksums

Verify your patched ISO matches the official build using SHA-256:

```text
# Original Japanese ISO (ULJM-06104 v1.02):
5eddbb1bb87bc88f4efa380826276cd605fe65dac0c8beee73b64d7e91be110e *original.iso

# Patched English ISO:
82939a0d0cbf91964eb0cf13c3e1c5c67b9bbab24db2a35a93bde8005d03f270 *ArabiansLost_English.iso

# Distributable xdelta3 Patch:
19c90e91c13a3c8be45551bf9c31c07e3fb6a2a08ad01f5dca9e9703ec6656f1 *ArabiansLost_English_v1.0.xdelta
```

---

## 💡 Gameplay & Naming Screen Guide

### Heroine Name Entry Screen
Early in the prologue, the game opens the name entry screen (`[inputname]`):
* **Default Canon Name:** The canonical name is **Aileen Olazabal**. To use the canon name, simply press **START** (or select **終了** / *Done*) to proceed immediately.
* **Custom English Names:** To type a custom English name, look at the right-hand column and select the 4th option (**`英字`** / *Alphabet*). The grid will switch to the standard Latin Alphabet (`A–Z`, `a–z`, space, numbers), allowing you to enter any name up to 7 characters.

### Recommended PPSSPP Settings
* **Backend:** Vulkan or Direct3D 11 / OpenGL.
* **Rendering Resolution:** 2× PSP (960×544) or higher for crisp typography.
* **Texture Filtering:** Linear / Auto.
* **Language Setting:** Set PPSSPP's system language to English so firmware save-data notifications display in English.

---

## 🧪 Public Testing & Feedback

This is a public community testing release. While all 35,713 scenario records have passed automated linters with 0 errors, feedback on typos, awkward phrasing, or formatting glitches is warmly welcomed!

### How to Report an Issue:
1. Check the [Issues](../../issues) tab to see if the issue has already been reported.
2. If not, open a new issue with:
   * **Route & Scene:** Character route and approximate day or context.
   * **Screenshot:** A screenshot of the text box or menu.
   * **Observed vs Expected:** What the text currently says and what you suggest.

---

## 🏗️ Building from Source

To build the English ISO from source using the repository assets:

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place your untouched Japanese ISO in `input/original.iso`.
3. Extract source assets:
   ```bash
   python tools/extract.py
   ```
4. Build the English ISO:
   ```bash
   python tools/build.py
   ```
5. Generate the distribution patch:
   ```bash
   python tools/make_patch.py
   ```

---

## 📜 Disclaimer & Credits

* This is a non-commercial, fan-made translation project created for educational and preservation purposes.
* All original game content, scenario scripts, artwork, and music are copyright © **QuinRose** / **Prototype**.
* Please support the creators by purchasing official merchandise and releases.
