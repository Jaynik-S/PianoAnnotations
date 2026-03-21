"""CLI entrypoint for the MIDI to note-event JSON pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .chord_grouping import build_chord_groups
from .exporter import build_export_dict, export_to_json
from .hand_inference import infer_hands
from .midi_parser import MidiParserError, normalize_notes, parse_midi_file
from .note_schema import ParseResult, PipelineConfig


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path | None = None,
    config: PipelineConfig | None = None,
) -> dict:
    """Run the full pipeline and optionally export the result to disk."""

    effective_config = config or PipelineConfig()
    extracted_notes, metadata = parse_midi_file(input_path)
    notes = normalize_notes(extracted_notes)
    groups = build_chord_groups(notes, effective_config.group_tolerance_sec)
    infer_hands(notes, groups, effective_config.hand_split_midi)

    result = ParseResult(metadata=metadata, notes=notes, groups=groups)
    payload = build_export_dict(result, effective_config)
    if output_path is not None:
        export_to_json(payload, output_path, pretty=effective_config.pretty_json)
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description="Parse a MIDI file into normalized note-event JSON."
    )
    parser.add_argument("input", help="Path to the input .mid or .midi file")
    parser.add_argument("--output", required=True, help="Path to the output JSON file")
    parser.add_argument(
        "--group-tolerance",
        type=float,
        default=0.03,
        help="Maximum onset difference in seconds for grouping notes into a chord",
    )
    parser.add_argument(
        "--hand-split-midi",
        type=int,
        default=60,
        help="Register split threshold used by the RH/LH heuristic",
    )
    parser.add_argument(
        "--pretty",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Pretty-print the exported JSON",
    )
    parser.add_argument(
        "--include-metadata",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include top-level metadata in the exported JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute the CLI and return a process exit code."""

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    config = PipelineConfig(
        group_tolerance_sec=args.group_tolerance,
        hand_split_midi=args.hand_split_midi,
        pretty_json=args.pretty,
        include_metadata=args.include_metadata,
    )

    try:
        payload = run_pipeline(args.input, args.output, config=config)
    except (MidiParserError, ValueError) as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")
    except OSError as exc:
        parser.exit(status=1, message=f"Error writing output: {exc}\n")

    note_count = len(payload["notes"])
    group_count = len(payload["groups"])
    print(f"Exported {note_count} notes across {group_count} groups to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
