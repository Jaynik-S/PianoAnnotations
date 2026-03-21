"""ASCII renderer built on top of the fixed-grid quantized score."""

from __future__ import annotations

from dataclasses import dataclass

from .quantizer import QuantizedScore, RenderNote


@dataclass(frozen=True)
class ColumnCell:
    """A single logical time cell for one hand."""

    token: str
    notes: tuple[RenderNote, ...]


@dataclass(frozen=True)
class RenderSystem:
    """A wrapped system containing RH and LH cells plus per-column widths."""

    start_column: int
    rh_cells: tuple[ColumnCell, ...]
    lh_cells: tuple[ColumnCell, ...]
    cell_widths: tuple[int, ...]


def build_hand_sequence(
    columns: dict[int, list[RenderNote]],
    total_columns: int,
) -> list[ColumnCell]:
    """Build the full logical column sequence for one hand."""

    sequence: list[ColumnCell] = []
    for column_index in range(total_columns):
        notes_in_column = tuple(columns.get(column_index, []))
        token = "".join(note.pitch_label for note in notes_in_column) if notes_in_column else "-"
        sequence.append(ColumnCell(token=token, notes=notes_in_column))
    return sequence


def build_render_systems(score: QuantizedScore, system_width: int) -> list[RenderSystem]:
    """Split the full score into wrapped systems with shared RH/LH column widths."""

    if system_width <= 0:
        raise ValueError("system_width must be greater than zero")

    total_columns = score.total_columns
    if total_columns == 0:
        return [RenderSystem(start_column=0, rh_cells=tuple(), lh_cells=tuple(), cell_widths=tuple())]

    rh_sequence = build_hand_sequence(score.rh_columns, total_columns)
    lh_sequence = build_hand_sequence(score.lh_columns, total_columns)

    systems: list[RenderSystem] = []
    for start in range(0, total_columns, system_width):
        rh_chunk = tuple(rh_sequence[start : start + system_width])
        lh_chunk = tuple(lh_sequence[start : start + system_width])
        widths = tuple(
            max(len(rh_cell.token), len(lh_cell.token), 1)
            for rh_cell, lh_cell in zip(rh_chunk, lh_chunk)
        )
        systems.append(
            RenderSystem(
                start_column=start,
                rh_cells=rh_chunk,
                lh_cells=lh_chunk,
                cell_widths=widths,
            )
        )
    return systems


def render_ascii(score: QuantizedScore, system_width: int = 50) -> str:
    """Render the quantized score into wrapped ASCII notation."""

    systems = build_render_systems(score, system_width=system_width)
    blocks: list[str] = []
    for system in systems:
        rh_line = _render_ascii_line("RH", system.rh_cells, system.cell_widths)
        lh_line = _render_ascii_line("LH", system.lh_cells, system.cell_widths)
        blocks.append(f"{rh_line}\n{lh_line}")
    return "\n\n".join(blocks)


def _render_ascii_line(
    label: str,
    cells: tuple[ColumnCell, ...],
    widths: tuple[int, ...],
) -> str:
    body = "".join(_render_ascii_cell(cell, width) for cell, width in zip(cells, widths))
    return f"{label}:|{body}|"


def _render_ascii_cell(cell: ColumnCell, width: int) -> str:
    if not cell.notes:
        return "-" * width
    return f"{cell.token}{'-' * (width - len(cell.token))}"
