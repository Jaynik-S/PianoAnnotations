from __future__ import annotations

import json

from src.main import main


def test_main_json_render_accepts_spacing_reduction(tmp_path) -> None:
    payload = {
        "notes": [
            {"id": 0, "pitch_name": "C4", "pitch_midi": 60, "start_sec": 0.0, "hand": "RH", "chord_id": 0},
            {"id": 1, "pitch_name": "D4", "pitch_midi": 62, "start_sec": 0.15, "hand": "RH", "chord_id": 1},
        ]
    }
    json_path = tmp_path / "score.json"
    ascii_path = tmp_path / "score.txt"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(
        [
            str(json_path),
            "--ascii",
            str(ascii_path),
            "--spacing-reduction",
            "1",
        ]
    )

    assert exit_code == 0
    assert ascii_path.read_text(encoding="utf-8") == "RH:|cd|\nLH:|--| 0:00"
