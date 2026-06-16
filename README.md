# MinilabMk2_MacroMapper

Ableton Live 11/12 MIDI Remote Script that **automatically maps the MiniLab Mk2's encoders to rack macros on the selected track** — no blue hand focus needed, no manual MIDI mapping, ever.

---

## Requirements

- Arturia MiniLab Mk2
- Ableton Live 11 or 12
- Arturia MIDI Control Center (to flash the included preset)

---

## MIDI Control Center Setup (Required)

The MiniLab Mk2 must be flashed with the included preset before the script will work. The factory default encoder settings are **not** compatible.

1. Download and install [Arturia MIDI Control Center](https://www.arturia.com/support/downloads&manuals) if you don't have it.
2. Connect your MiniLab Mk2 via USB.
3. Open MIDI Control Center.
4. Click **Import** and select the `Macros.minilabmk2` file included in this repo.
5. Click **Store to Device** to flash the preset to the hardware.
6. Close MIDI Control Center.

The preset configures the encoders as follows:
- All encoders set to **Relative #3** mode (required for the script's delta tracking)
- Top row encoders (1–8): CC 112, 74, 71, 76, 77, 93, 73, 75 on MIDI channel 2
- Bottom row encoders (9–16): CC 114, 18, 19, 16, 17, 91, 79, 72 on MIDI channel 2
- Encoder 1 push: CC 113 on MIDI channel 2
- Encoder 9 push: CC 115 on MIDI channel 2

> **Note:** Do not use the Arturia "Ableton" factory preset — it uses different CC numbers and encoder modes that are incompatible with this script.

---

## Installation

1. **Find your User Remote Scripts folder:**
   - **Mac:** `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows:** `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\`

   > If the folder doesn't exist, create it. This location survives Live updates.

2. Copy the entire `MinilabMk2_MacroMapper` folder here.

3. Restart Ableton Live.

4. `Preferences → Link / Tempo / MIDI → Control Surface` → select **MinilabMk2_MacroMapper**
   Set Input and Output to **Arturia MiniLab mkII**.

---

## Encoder layout

| Row | CCs (MIDI ch 2) | Maps to |
|---|---|---|
| Top encoders 1–8 | CC 112, 74, 71, 76, 77, 93, 73, 75 | **Instrument Rack** macros 1–8 on selected track |
| Bottom encoders 9–16 | CC 114, 18, 19, 16, 17, 91, 79, 72 | **Audio Effect Rack** macros 1–8 on selected track |
| Encoder 1 **push** | CC 113 ch2 | Toggle Instrument Rack on/off |
| Encoder 9 **push** | CC 115 ch2 | Toggle Audio Effect Rack on/off |

Switching tracks instantly remaps both rows — completely hands-off.

---

## How rack detection works

The script scans `selected_track.devices` and finds:
- First device with `class_name == "InstrumentGroupDevice"` → top row
- First device with `class_name == "AudioEffectGroupDevice"` → bottom row

**Recommended track layout:**

```
[MIDI Track]
  └── Instrument Rack   ← top encoders 1-8 map here
  └── Audio Effect Rack ← bottom encoders 9-16 map here
```

If one rack type is missing, that encoder row silently does nothing (no errors).

---

## Running alongside Launchpad 95

Add MinilabMk2_MacroMapper as a **second** Control Surface slot — Ableton supports multiple scripts simultaneously with no conflict:

```
Control Surface 1: Launchpad95              → Launchpad X
Control Surface 2: MinilabMk2_MacroMapper   → MiniLab mkII
```

Workflow:
- **Launchpad X** → switch tracks, fire clips, Instrument/Sequencer mode
- **MiniLab top row** → tweak synth/drum preset macros (Instrument Rack)
- **MiniLab bottom row** → tweak insert effect macros (FX Rack)
- **MiniLab keys** → play melodic parts

---

## Troubleshooting

**Encoders don't respond at all:**
- Make sure you have flashed `Macros.minilabmk2` via MIDI Control Center (see setup above)
- Check `Preferences → Link / Tempo / MIDI`: script selected, Input set to MiniLab mkII, Remote toggle ON
- Check `Help → Show Log File` for Python errors

**Encoders jump wildly or spin without stopping:**
- The preset must be flashed to the device — do not use the factory Ableton preset
- Verify in MIDI Control Center that encoders are set to **Relative #3** mode

**Top or bottom row does nothing:**
- That rack type isn't on the selected track. Add an Instrument Rack or Audio Effect Rack to the device chain.
- The script finds the **first** rack of each type — place the Instrument Rack before any effects in the chain.
- Re-select the track after adding a rack to trigger a remap.

**Macros move but it's the wrong ones (e.g. Macro 9 instead of Macro 1):**
- This happens if the rack has 16 macros and the script picks up the wrong bank. The script targets the first 8 parameters in the rack's parameter list. Make sure your rack has macros starting from position 1, not 9.

**I have 16 macros on a rack — can I access macros 9–16?**
- Currently each row covers macros 1–8. A future version could add bank switching via a pad press.

---

## Customising CC numbers

If you modify the MIDI Control Center preset, update the constants at the top of `__init__.py` to match:

```python
TOP_ENCODER_CC    = [112, 74, 71, 76, 77, 93, 73, 75]
BOTTOM_ENCODER_CC = [114, 18, 19, 16, 17, 91, 79, 72]
ENC1_PUSH_CC      = 113
ENC9_PUSH_CC      = 115
ENCODER_CHANNEL   = 1   # 0-indexed, so 1 = MIDI channel 2
```

Use a MIDI monitor (MIDI Monitor on Mac, MIDI-OX on Windows) to verify what your unit sends if you're unsure.
