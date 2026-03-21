from __future__ import annotations

from src.quantizer import quantize_note_events
from src.renderer import render_ascii


def alignment_payload() -> dict:
    return {
        "notes": [
            {"id": 0, "pitch_name": "F4", "pitch_midi": 65, "start_sec": 0.0, "hand": "RH", "chord_id": 0},
            {"id": 1, "pitch_name": "G#2", "pitch_midi": 44, "start_sec": 0.0, "hand": "LH", "chord_id": 0},
            {"id": 2, "pitch_name": "D#3", "pitch_midi": 51, "start_sec": 0.0, "hand": "LH", "chord_id": 0},
            {"id": 3, "pitch_name": "F#3", "pitch_midi": 54, "start_sec": 0.0, "hand": "LH", "chord_id": 0},
            {"id": 4, "pitch_name": "F4", "pitch_midi": 65, "start_sec": 0.2, "hand": "RH", "chord_id": 1},
            {"id": 5, "pitch_name": "C#3", "pitch_midi": 49, "start_sec": 0.25, "hand": "LH", "chord_id": 2},
            {"id": 6, "pitch_name": "D#4", "pitch_midi": 63, "start_sec": 0.3, "hand": "RH", "chord_id": 3},
            {"id": 7, "pitch_name": "G#2", "pitch_midi": 44, "start_sec": 0.45, "hand": "LH", "chord_id": 4},
            {"id": 8, "pitch_name": "C3", "pitch_midi": 48, "start_sec": 0.45, "hand": "LH", "chord_id": 4},
        ]
    }


def test_render_ascii_keeps_rh_and_lh_content_lengths_equal() -> None:
    score = quantize_note_events(alignment_payload(), time_step_sec=0.05)

    output = render_ascii(score, system_width=10)
    rh_line, lh_line = output.splitlines()

    rh_body = rh_line[len("RH:|") : -1]
    lh_body = lh_line[len("LH:|") : -1]
    assert len(rh_body) == len(lh_body)
    assert rh_line == "RH:|f--------f--d#-----|"
    assert lh_line == "LH:|g#d#f#----c#----g#c|"


def test_render_ascii_sorts_same_hand_chords_low_to_high() -> None:
    payload = {
        "notes": [
            {"id": 0, "pitch_name": "G4", "pitch_midi": 67, "start_sec": 0.0, "hand": "RH", "chord_id": 0},
            {"id": 1, "pitch_name": "C4", "pitch_midi": 60, "start_sec": 0.0, "hand": "RH", "chord_id": 0},
            {"id": 2, "pitch_name": "F#4", "pitch_midi": 66, "start_sec": 0.0, "hand": "RH", "chord_id": 0},
        ]
    }

    score = quantize_note_events(payload, time_step_sec=0.05)
    output = render_ascii(score, system_width=10)

    assert output == "RH:|cf#g|\nLH:|----|"


def test_render_ascii_wraps_after_50_columns() -> None:
    payload = {
        "notes": [
            {"id": 0, "pitch_name": "C4", "pitch_midi": 60, "start_sec": 0.0, "hand": "RH", "chord_id": 0},
            {"id": 1, "pitch_name": "D4", "pitch_midi": 62, "start_sec": 2.5, "hand": "RH", "chord_id": 1},
        ]
    }

    score = quantize_note_events(payload, time_step_sec=0.05)
    output = render_ascii(score, system_width=50)

    blocks = output.split("\n\n")
    assert len(blocks) == 2
    assert blocks[0].startswith("RH:|c")
    assert blocks[1].startswith("RH:|d")


def test_render_ascii_handles_empty_score() -> None:
    score = quantize_note_events({"notes": []}, time_step_sec=0.05)
    assert render_ascii(score, system_width=50) == "RH:||\nLH:||"
