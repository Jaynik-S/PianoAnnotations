# Piano MIDI to Note-Event JSON MVP

This project parses a local piano-oriented MIDI file into a normalized JSON structure containing note events, onset groups, and simple right-hand versus left-hand labels.

It is intentionally small and modular:
- `src/midi_parser.py` loads MIDI data with `pretty_midi` and extracts note-level timing.
- `src/chord_grouping.py` groups near-simultaneous onsets into deterministic chord groups.
- `src/hand_inference.py` applies a replaceable RH/LH heuristic.
- `src/exporter.py` builds and writes the final JSON payload.
- `src/quantizer.py` maps stage-one JSON onto a fixed time grid for aligned rendering.
- `src/renderer.py` renders aligned ASCII output from the fixed grid.
- `src/html_renderer.py` renders the same layout as monospaced HTML with octave colors.
- `src/main.py` exposes both the MIDI-to-JSON CLI and the JSON-to-annotation CLI.

## Requirements

- Python 3.9+
- Dependencies from `requirements.txt`

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python -m src.main inputs/Mariage.MID --output outputs/mariage.json
```

Optional flags:

```bash
python -m src.main inputs/Mariage.MID \
  --output outputs/mariage.json \
  --group-tolerance 0.03 \
  --hand-split-midi 60 \
  --pretty \
  --include-metadata
```

To disable pretty formatting or metadata:

```bash
python -m src.main inputs/Mariage.MID --output outputs/mariage.json --no-pretty --no-include-metadata
```

## Render JSON to ASCII and HTML

The second stage consumes the stage-one JSON and renders it on a shared fixed time grid. Both hands use the same quantized columns, and each logical column is padded to the widest token across RH and LH before serialization. This keeps the output visually aligned even when one hand has a long chord label and the other has a single note or a dash.

The renderer also applies a small layout compaction pass inside each wrapped system: fully empty leading or interior runs lose exactly one dash in total while RH and LH still share the same column widths. Each LH line ends with the elapsed time covered by that wrapped block, formatted as `m:ss`.

```bash
python -m src.main outputs/mariage.json --ascii outputs/mariage.txt --html outputs/mariage.html
```

Optional renderer flags:

```bash
python -m src.main outputs/mariage.json \
  --ascii outputs/mariage.txt \
  --html outputs/mariage.html \
  --time-step 0.05 \
  --system-width 50
```

ASCII output uses wrapped systems like:

```text
RH:|f-------f--d#----|
LH:|g#d#f#---c#---g#c| 0:00
```

## JSON shape

```json
{
  "metadata": {
    "source_file": "example.mid",
    "source_path": "/absolute/path/example.mid",
    "note_count": 2,
    "group_count": 1,
    "group_tolerance_sec": 0.03,
    "hand_split_midi": 60,
    "tempo_estimate_bpm": 120.0,
    "initial_tempo_bpm": 120.0,
    "duration_sec": 0.6,
    "instrument_count": 1,
    "is_likely_piano_only": true
  },
  "notes": [
    {
      "id": 0,
      "pitch_midi": 56,
      "pitch_name": "G#3",
      "start_sec": 0.5,
      "end_sec": 0.9,
      "duration_sec": 0.4,
      "velocity": 84,
      "hand": "LH",
      "chord_id": 0,
      "track_index": 0,
      "instrument_index": 0,
      "instrument_name": "Acoustic Grand Piano",
      "onset_rank": 0,
      "metadata": {
        "is_drum": false
      }
    }
  ],
  "groups": [
    {
      "chord_id": 0,
      "start_sec": 0.5,
      "end_sec": 0.9,
      "duration_sec": 0.4,
      "note_ids": [0, 1],
      "pitches_midi": [56, 63],
      "pitches": ["G#3", "D#4"],
      "hand": null,
      "size": 2
    }
  ]
}
```

## Hand heuristic

The MVP hand inference is intentionally simple and isolated from parsing so it can be replaced later.

Current behavior:
- Groups whose notes are all below the split threshold default to `LH`.
- Groups whose notes are all at or above the split threshold default to `RH`.
- Mixed-register simultaneous groups are split low-to-high, with the middle note in an odd-sized group assigned by its side of the split.
- Neighbor smoothing reduces isolated flips near middle C when surrounding groups clearly favor the other hand.
- Entire passages that sit fully above or below the split threshold can resolve to a single hand.

Known limitations:
- It does not perform voice separation.
- Cross-hand passages can be mislabeled.
- Sustained overlaps are not used during hand inference.
- Non-piano MIDI is processed generically, so hand labels are only rough register guesses.
- `pretty_midi` exposes instruments rather than true track ids, so `track_index` and `instrument_index` use the same source ordering.

## Test

```bash
pytest
```
