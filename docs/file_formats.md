# Arabians Lost: The Engagement on Desert (PSP) — File Format Specifications

## 1. ISO Image Layout

- **Disc ID:** `ULJM06104` (UMD Release 1.02, System Version 6.60)
- **Filesystem:** Standard ISO-9660 with Sony PSP structure:
  - `PSP_GAME/PARAM.SFO`: System metadata.
  - `PSP_GAME/SYSDIR/EBOOT.BIN`: Encrypted MIPS executable (~2.2 MB).
  - `PSP_GAME/USRDIR/data.cpk`: Main game archive (scripts, graphics, fonts).
  - `PSP_GAME/USRDIR/voice.cpk`: Voice audio clips (CRI CPK container).
  - `PSP_GAME/USRDIR/bgm.cpk`: Background music (CRI CPK container).
  - `PSP_GAME/USRDIR/sound.cpk`: Sound effects (CRI CPK container).
  - `PSP_GAME/USRDIR/movie.cpk`: Video cutscenes (CRI CPK container).
  - `PSP_GAME/USRDIR/libfont.prx`: Sony PSP font driver module.
  - `PSP_GAME/INSDIR/*.DNS`: Encrypted Sony PGD containers for Memory Stick Data Install.

---

## 2. CRI Middleware CPK Archive (`data.cpk`)

- **Signature:** `CPK\x20` at offset `0x0000`.
- **Table System:** CRI Universal Table Format (`@UTF`).
- **Header Table (`CpkHeader`):**
  - Offset: `0x0010`.
  - Specifies:
    - `TocOffset`: `0x00000800` (Offset to TOC table).
    - `TocSize`: `0x0003BCD8` (Size of TOC table).
    - `ContentOffset`: `0x00050000` (Base payload offset).
    - `Align`: `2048` (0x800 sector alignment).
    - `Files`: `5636` files.
- **Table of Contents (`CpkTocInfo`):**
  - Location: `0x00000810` (inside TOC chunk at 0x800).
  - Rows: `5636`.
  - Key columns per entry:
    - `ID`: File index (`uint32`).
    - `DirName`: Virtual directory path (`string`).
    - `FileName`: File name (`string`).
    - `FileSize`: Stored byte size in archive (`uint32`).
    - `ExtractSize`: Decompressed uncompressed size (`uint32`).
    - `FileOffset`: Stored offset relative to `TocOffset` (`0x800`) (`uint64`).
- **Compression Mode:**
  - If `FileSize < ExtractSize` and signature is `CRILAYLA`, data is compressed with CRI Layla.
  - If `FileSize == ExtractSize`, data is stored uncompressed.
  - The game engine natively handles both uncompressed and compressed files.

---

## 3. CRILAYLA Compression Algorithm

- **Signature:** `CRILAYLA` (8 bytes) at start of compressed chunk.
- **Header Structure (16 bytes):**
  - Bytes 0–7: `b'CRILAYLA'`
  - Bytes 8–11: `decomp_size` (32-bit unsigned little-endian: uncompressed payload size minus 256 bytes).
  - Bytes 12–15: `comp_size` (32-bit unsigned little-endian: compressed payload size).
- **Payload Layout:**
  - Bytes 16 to `16 + comp_size`: Backwards LZSS bitstream.
  - Bytes `16 + comp_size` to `16 + comp_size + 256`: Trailer (first 256 bytes of uncompressed file).
- **Decompression Logic:**
  - Initialize destination buffer of size `256 + decomp_size`.
  - Copy 256-byte trailer to `dst[0:256]`.
  - Process bitstream in reverse from `src[comp_size - 1]` to write destination from `dst[decomp_size + 255]` down to `dst[256]`.
  - Exit condition: `dbuf_pos < 256`.

---

## 4. Scenario Script Format (`.ks`)

QuinRose visual novel scripts are structured text files derived from the KAG (Kirikiri Adventure Game) specification, encoded in **CP932 (Shift-JIS)** with CRLF line endings.

- **Total Scenario Files:** 1,815 files (`extracted/data_cpk/scenario/*.ks`).
- **Total Lines:** 232,450 lines.
- **Comments:** Lines starting with `;` (e.g. `; ac_ev1.ks`).
- **Script Commands:** Enclosed in brackets `[tag arg1="val" arg2="val"]`.

### Primary Tags:
1. `[message window="win" face="ai_xxx.png"] ... [/message]`:
   - Defines dialogue and narrative text.
   - Text inside block is displayed in the dialogue window.
   - Tab indentation `\t` prefixes Japanese spoken text.
   - Quotation marks `「 ... 」` denote spoken character dialogue.
   - Window types:
     - `kya`: Secondary character speaking to Aileen.
     - `her`: Aileen speaking directly.
     - `tog`: Narration / omniscient narrative description.
     - `mon`: Internal monologue / thoughts.
   - `face="..."`: Face sprite thumbnail displayed alongside dialogue box.
2. `[br]`: Line break within dialogue box.
3. `[clearmessage]`: Clears text from dialogue window.
4. `[select item1="..." item2="..."]`: Choice and branching decisions.
5. `[next file="xxx.ks"]`: Script chaining and jump to next scenario file.
6. `[if_route_next ...]` / `[route chara="..."]`: Route evaluation conditions.
7. `[chara1]`, `[chara2]`, `[chara3]`, `[chara4]`: Character sprite stage positioning.
8. `[bgimage file="..."]`: Background scene changes.
9. `[bgm file="..."]` / `[se1 file="..."]` / `[se2 file="..."]`: Audio playback.
10. `[cg file="..."]`: Event CG display.

---

## 5. Font Resources (`.pgf`)

- **Format:** Sony PlayStation Portable PGF (`PGF0`).
- **Font Files (12 files in archive root):**
  - Gothic: `gothic9.pgf`, `gothic13.pgf`, `gothic15.pgf`
  - Maru: `maru9.pgf`, `maru13.pgf`, `maru15.pgf`
  - Mincho: `mincho9.pgf`, `mincho13.pgf`, `mincho15.pgf`
  - Pop: `pop9.pgf`, `pop13.pgf`, `pop15.pgf`
- Standard ASCII characters (32–126), fullwidth alphanumerics, and standard punctuation are natively supported.
