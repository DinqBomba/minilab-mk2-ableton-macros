"""
MinilabMk2_MacroMapper
======================
Ableton Live 11/12 MIDI Remote Script for the Arturia MiniLab Mk2.

Automatically maps encoders to rack macros on the SELECTED track:

  Top row    encoders 1-8   (CC 14-21, ch 1)  → Instrument Rack macros 1-8
  Bottom row encoders 9-16  (CC 22-29, ch 1)  → Audio Effect Rack macros 1-8

Both mappings update instantly whenever you select a different track.
No blue hand focus required — just select the track and twist.

Push controls:
  Encoder 1 push  (CC 112, ch 1)  → toggle Instrument Rack on/off
  Encoder 9 push  (CC 113, ch 1)  → toggle Audio Effect Rack on/off

Rack detection uses device.class_name:
  "InstrumentGroupDevice"  → Instrument Rack
  "AudioEffectGroupDevice" → Audio Effect Rack (first one found on the chain)

Author: generated for beatmaking workflow extension
Requires: MiniLab Mk2 in Ableton/DAW mode (Shift + Pad 8)
Tested:   Ableton Live 11 / 12  (Python 3)
"""

from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE
import Live

# Hardware constants  (MiniLab Mk2 in Ableton mode, all ch 1 = index 0)
ENCODER_CHANNEL    = 1

TOP_ENCODER_CC     = [112, 74, 71, 76, 77, 93, 73, 75]   # encoders 1-8
BOTTOM_ENCODER_CC  = [114, 18, 19, 16, 17, 91, 79, 72]   # encoders 9-16

ENC1_PUSH_CC       = 113   # encoder 1 push → toggle instrument rack on/off
ENC9_PUSH_CC       = 115   # encoder 9 push → toggle fx rack on/off

# Device class names as reported by the Live Object Model
INSTRUMENT_RACK_CLASS  = "InstrumentGroupDevice"
AUDIO_FX_RACK_CLASS    = "AudioEffectGroupDevice"

# How many macros each row of encoders controls (racks have up to 16, we use 8)
MACROS_PER_ROW = 8


def create_instance(c_instance):
    return MinilabMk2MacroMapper(c_instance)


class MinilabMk2MacroMapper(ControlSurface):

    def __init__(self, c_instance):
        super().__init__(c_instance)
        self.log_message("MinilabMk2_MacroMapper: loading …")

        with self.component_guard():
            self._build_encoders()
            self._install_track_listener()

        self.show_message("MiniLab Mk2 Macro Mapper ready")
        self.log_message("MinilabMk2_MacroMapper: loaded OK")

    def _debug_midi(self, value):
        self.log_message("RAW MIDI VALUE: {}".format(value))

    # Initialisation helpers

    def _build_encoders(self):
        # Use ButtonElement instead of EncoderElement to get raw CC values
        self._top_encs = [
            ButtonElement(False, MIDI_CC_TYPE, ENCODER_CHANNEL, cc)
            for cc in TOP_ENCODER_CC
        ]
        self._bot_encs = [
            ButtonElement(False, MIDI_CC_TYPE, ENCODER_CHANNEL, cc)
            for cc in BOTTOM_ENCODER_CC
        ]

        self._enc1_push = ButtonElement(True, MIDI_CC_TYPE, ENCODER_CHANNEL, ENC1_PUSH_CC)
        self._enc9_push = ButtonElement(True, MIDI_CC_TYPE, ENCODER_CHANNEL, ENC9_PUSH_CC)

        for i, enc in enumerate(self._top_encs):
            enc.add_value_listener(lambda v, idx=i: self._top_moved(v, idx))
        for i, enc in enumerate(self._bot_encs):
            enc.add_value_listener(lambda v, idx=i: self._bot_moved(v, idx))

        self._enc1_push.add_value_listener(self._enc1_pushed)
        self._enc9_push.add_value_listener(self._enc9_pushed)

        self._prev_values = {}
        self._top_params = []
        self._bot_params = []

    def _install_track_listener(self):
        """Watch for track selection changes."""
        view = self.song().view
        view.add_selected_track_listener(self._on_track_selected)
        self._on_track_selected()   # map immediately for whatever track is selected

    # Track / device scanning

    def _on_track_selected(self):
        """Re-scan the selected track and update both encoder rows."""
        track = self.song().view.selected_track
        if track is None:
            self._top_params = []
            self._bot_params = []
            self.show_message("No track selected")
            return

        instrument_rack = self._find_rack(track, INSTRUMENT_RACK_CLASS)
        fx_rack         = self._find_rack(track, AUDIO_FX_RACK_CLASS)

        self._top_params = self._macro_params(instrument_rack, MACROS_PER_ROW)
        self._bot_params = self._macro_params(fx_rack,         MACROS_PER_ROW)

        self._report_mapping(track, instrument_rack, fx_rack)

    def _find_rack(self, track, class_name):
        """
        Return the first device on `track` whose class_name matches.
        Returns None if not found.
        """
        for device in track.devices:
            if device.class_name == class_name:
                return device
        return None

    def _macro_params(self, rack, count):
        if rack is None:
            return []
        # parameters[0] is always on/off, macros start at index 1
        # First 8 macros are indices 1-8, second bank is 9-16
        macros = [p for p in rack.parameters[1:count+1]]
        return macros

    def _report_mapping(self, track, inst_rack, fx_rack):
        """Log and display a status message for the current mapping."""
        inst_name = inst_rack.name if inst_rack else "—"
        fx_name   = fx_rack.name   if fx_rack   else "—"

        # DEBUG: log all macro names in order
        if inst_rack:
            for i, p in enumerate(self._top_params):
                self.log_message("top_param[{}] = {}".format(i, p.name))

        msg = "↑ {} | ↓ {}".format(inst_name, fx_name)
        self.show_message(msg)
        self.log_message(
            "MinilabMk2_MacroMapper: track '{}' | inst rack '{}' ({} macros) | "
            "fx rack '{}' ({} macros)".format(
                track.name,
                inst_name, len(self._top_params),
                fx_name,   len(self._bot_params),
            )
        )

    # Encoder movement  →  parameter change

    def _top_moved(self, value, idx):
        self.log_message("_top_moved: idx={} value={} params_len={}".format(idx, value, len(self._top_params)))
        self._apply(self._top_params, idx, value)

    def _bot_moved(self, value, idx):
        self._apply(self._bot_params, idx, value)

    def _apply(self, params, idx, value):
        if idx >= len(params):
            return
        param = params[idx]
        if param is None or not param.is_enabled:
            return

        key = id(param)
        
        # Ignore the resting baseline value the hardware sends between pulses
        if value == 16:
            self._prev_values[key] = value
            return

        if key not in self._prev_values:
            self._prev_values[key] = value
            return

        prev = self._prev_values[key]
        self._prev_values[key] = value

        delta = value - prev
        if delta > 64:
            delta -= 128
        elif delta < -64:
            delta += 128

        if delta == 0:
            return

        step = (param.max - param.min) / 64.0
        new_value = param.value + (delta * step)
        param.value = max(param.min, min(param.max, new_value))
        self.log_message("_apply: param={} delta={} new_value={}".format(param.name, delta, param.value))

    # Encoder pushes  →  rack on/off toggle

    def _enc1_pushed(self, value):
        """Toggle the Instrument Rack on/off."""
        if value == 0:
            return
        self._toggle_rack(INSTRUMENT_RACK_CLASS, "Instrument Rack")

    def _enc9_pushed(self, value):
        """Toggle the Audio Effect Rack on/off."""
        if value == 0:
            return
        self._toggle_rack(AUDIO_FX_RACK_CLASS, "FX Rack")

    def _toggle_rack(self, class_name, label):
        track = self.song().view.selected_track
        if track is None:
            return
        rack = self._find_rack(track, class_name)
        if rack is None:
            self.show_message("No {} on this track".format(label))
            return
        # parameters[0] is always the device on/off
        on_off = rack.parameters[0]
        on_off.value = 0.0 if on_off.value > 0.5 else 1.0
        state = "ON" if on_off.value > 0.5 else "OFF"
        self.show_message("{}: {}  ({})".format(label, rack.name, state))

    # Cleanup

    def disconnect(self):
        try:
            self.song().view.remove_selected_track_listener(self._on_track_selected)
        except Exception:
            pass
        super().disconnect()
        self.log_message("MinilabMk2_MacroMapper: disconnected")
