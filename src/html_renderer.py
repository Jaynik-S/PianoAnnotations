"""HTML renderer for fixed-grid piano annotations."""

from __future__ import annotations

from html import escape

from .quantizer import QuantizedScore
from .renderer import ColumnCell, build_render_systems


OCTAVE_COLORS = {
    1: "#ea9999",
    2: "#ffe599",
    3: "#ffffff",
    4: "#6d9eeb",
    5: "#8e7cc3",
    6: "#c27ba0",
    7: "#000000",
}


def render_html(score: QuantizedScore, system_width: int = 50) -> str:
    """Render the quantized score into standalone HTML."""

    systems = build_render_systems(score, system_width=system_width)
    system_markup = "\n".join(_render_html_system(system) for system in systems)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Piano Annotation</title>
  <style>
    body {{
      margin: 24px;
      background: #ffffff;
      color: #111111;
      font-family: "Courier New", Courier, monospace;
    }}
    .score {{
      white-space: pre;
      font-size: 16px;
      line-height: 1.35;
    }}
    .system {{
      margin-bottom: 16px;
    }}
    .line-label {{
      font-weight: 700;
    }}
    .note {{
      padding: 0;
      border-radius: 0;
    }}
  </style>
</head>
<body>
  <div class="score">
{system_markup}
  </div>
</body>
</html>
"""


def _render_html_system(system) -> str:
    rh_line = _render_html_line("RH", system.rh_cells, system.cell_widths)
    lh_line = _render_html_line("LH", system.lh_cells, system.cell_widths)
    return f'    <div class="system">{rh_line}<br>{lh_line}</div>'


def _render_html_line(label: str, cells: tuple[ColumnCell, ...], widths: tuple[int, ...]) -> str:
    body = "".join(_render_html_cell(cell, width) for cell, width in zip(cells, widths))
    return f'<span class="line-label">{label}:|</span>{body}|'


def _render_html_cell(cell: ColumnCell, width: int) -> str:
    if not cell.notes:
        return escape("-" * width)

    is_chord = len(cell.notes) > 1
    rendered_notes = "".join(
        _render_html_note_fragment(note.pitch_label, note.octave, bold=is_chord)
        for note in cell.notes
    )
    filler = "-" * max(0, width - len(cell.token))
    return f"{rendered_notes}{escape(filler)}"


def _render_html_note_fragment(note_label: str, octave: int, bold: bool) -> str:
    background = OCTAVE_COLORS.get(octave, "#d9d9d9")
    foreground = "#ffffff" if background.lower() == "#000000" else "#111111"
    weight = "700" if bold else "400"
    return (
        f'<span class="note" style="background:{background};color:{foreground};'
        f'font-weight:{weight};">{escape(note_label)}</span>'
    )
