"""
Strategic Capacity & Risk Assessment — PDF Report Generator
============================================================
Generates a professional two-column PDF report from operational metrics.

Layout:
    - Fixed sidebar (canvas layer): telemetry dashboard, KPIs, alerts
    - Main content frame (Platypus flow): analysis, tables, chart

Dependencies:
    pip install reportlab matplotlib numpy
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable


# ---------------------------------------------------------------------------
# Configuration & constants
# ---------------------------------------------------------------------------

PAGE_WIDTH, PAGE_HEIGHT = A4

HEADER_HEIGHT = 20 * mm
FOOTER_HEIGHT = 14 * mm
SIDEBAR_WIDTH = 55 * mm
SIDEBAR_GAP   = 6 * mm
MARGIN_LEFT   = 14 * mm
MARGIN_RIGHT  = 14 * mm

CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - SIDEBAR_WIDTH - SIDEBAR_GAP - MARGIN_RIGHT
CONTENT_X     = MARGIN_LEFT
CONTENT_Y     = FOOTER_HEIGHT + 2 * mm
CONTENT_HEIGHT = PAGE_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT - 4 * mm

SIDEBAR_X = PAGE_WIDTH - MARGIN_RIGHT - SIDEBAR_WIDTH
SIDEBAR_Y = FOOTER_HEIGHT + 2 * mm
SIDEBAR_HEIGHT = PAGE_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT - 4 * mm

ROW_HEIGHT   = 7.5 * mm
SECTION_HEIGHT = 7 * mm


class Palette:
    """Brand colour constants for the report."""

    NAVY        = colors.HexColor("#0A1628")
    NAVY_MID    = colors.HexColor("#1B3A6B")
    BLUE        = colors.HexColor("#2563EB")
    RED         = colors.HexColor("#DC2626")
    GOLD        = colors.HexColor("#D97706")
    GREEN       = colors.HexColor("#059669")
    BG_LIGHT    = colors.HexColor("#F8FAFC")
    BG_ALT      = colors.HexColor("#EFF4FB")
    BORDER      = colors.HexColor("#CBD5E1")
    TEXT        = colors.HexColor("#0F172A")
    TEXT_MUTED  = colors.HexColor("#64748B")
    WHITE       = colors.white

    # Inline hex strings used only in Matplotlib
    CHART_SAFE  = "#BFDBFE"
    CHART_RISK  = "#FECACA"
    CHART_CURVE = "#1B3A6B"
    CHART_MEAN  = "#2563EB"
    CHART_CAP   = "#DC2626"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class OperationalMetrics:
    """
    Typed container for all operational data driving the report.
    Accepts a raw dict from the calling application via ``from_dict``.
    """

    transport_mode:   str   = "Road (Standard)"
    sla:              float = 0.95
    avg_demand:       float = 0.0
    std_dev:          float = 0.0
    safety_stock:     float = 0.0
    resilience_score: float = 0.0
    dependency_ratio: float = 0.0
    co2_emissions:    float = 0.0
    loyalty_score:    float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OperationalMetrics":
        """Construct from a plain dictionary, ignoring unknown keys."""
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    @property
    def capacity_threshold(self) -> float:
        return self.avg_demand + self.safety_stock

    @property
    def resilience_color(self) -> colors.Color:
        return Palette.GREEN if self.resilience_score > 70 else Palette.RED


# ---------------------------------------------------------------------------
# Typography helpers
# ---------------------------------------------------------------------------

def make_style(name: str, **overrides: Any) -> ParagraphStyle:
    """
    Return a ``ParagraphStyle`` by merging a named preset with any overrides.
    Each call produces a uniquely named style to avoid ReportLab's style cache.
    """
    presets: dict[str, dict[str, Any]] = {
        "h1": dict(
            fontName="Helvetica-Bold", fontSize=14, textColor=Palette.NAVY,
            spaceAfter=2, leading=17,
        ),
        "subtitle": dict(
            fontName="Helvetica", fontSize=8.5, textColor=Palette.TEXT_MUTED,
            spaceAfter=6, leading=11,
        ),
        "body": dict(
            fontName="Helvetica", fontSize=9, textColor=Palette.TEXT,
            spaceAfter=4, leading=13, alignment=TA_JUSTIFY,
        ),
        "small": dict(
            fontName="Helvetica", fontSize=8, textColor=Palette.TEXT_MUTED,
            spaceAfter=3, leading=11, alignment=TA_JUSTIFY,
        ),
        "equation": dict(
            fontName="Helvetica-Oblique", fontSize=9, textColor=Palette.NAVY_MID,
            spaceAfter=4, spaceBefore=2, leading=13,
            leftIndent=4 * mm,
            backColor=colors.HexColor("#EFF6FF"),
            borderPad=4,
        ),
        "table_header": dict(
            fontName="Helvetica-Bold", fontSize=8, textColor=Palette.WHITE,
            leading=10,
        ),
        "table_cell": dict(
            fontName="Helvetica", fontSize=8.5, textColor=Palette.TEXT,
            leading=11,
        ),
        "table_cell_highlight": dict(
            fontName="Helvetica-Bold", fontSize=8.5, textColor=Palette.RED,
            leading=11,
        ),
        "action_title": dict(
            fontName="Helvetica-Bold", fontSize=9.5, textColor=Palette.NAVY,
            spaceAfter=2, leading=12,
        ),
        "action_body": dict(
            fontName="Helvetica", fontSize=8.5, textColor=Palette.TEXT,
            leading=12, alignment=TA_JUSTIFY,
        ),
        "number_label": dict(
            fontName="Helvetica-Bold", fontSize=12, textColor=Palette.WHITE,
            alignment=TA_CENTER, leading=15,
        ),
    }

    if name not in presets:
        raise ValueError(f"Unknown style preset: '{name}'")

    config = {**presets[name], **overrides}
    unique_name = f"{name}_{id(overrides)}"
    return ParagraphStyle(unique_name, **config)


# ---------------------------------------------------------------------------
# Canvas-layer drawing (header, footer, sidebar)
# ---------------------------------------------------------------------------

def draw_rounded_rect(
    canvas: Any,
    x: float,
    y: float,
    width: float,
    height: float,
    radius: float = 3,
    fill_color: colors.Color | None = None,
    stroke_color: colors.Color | None = None,
    line_width: float = 0.5,
) -> None:
    """Convenience wrapper for ReportLab's roundRect with optional fill/stroke."""
    if fill_color is not None:
        canvas.setFillColor(fill_color)
    if stroke_color is not None:
        canvas.setStrokeColor(stroke_color)
        canvas.setLineWidth(line_width)
    canvas.roundRect(
        x, y, width, height, radius,
        fill=1 if fill_color else 0,
        stroke=1 if stroke_color else 0,
    )


def draw_header(canvas: Any, page_number: int) -> None:
    """Render the full-width navy header bar with title and metadata."""
    canvas.setFillColor(Palette.NAVY)
    canvas.rect(0, PAGE_HEIGHT - HEADER_HEIGHT, PAGE_WIDTH, HEADER_HEIGHT, fill=1, stroke=0)

    # Blue accent stripe at the base of the header
    canvas.setFillColor(Palette.BLUE)
    canvas.rect(0, PAGE_HEIGHT - HEADER_HEIGHT - 1, PAGE_WIDTH, 1.5, fill=1, stroke=0)

    text_y = PAGE_HEIGHT - HEADER_HEIGHT + 7.5 * mm

    canvas.setFillColor(Palette.WHITE)
    canvas.setFont("Helvetica-Bold", 11.5)
    canvas.drawString(MARGIN_LEFT, text_y, "STRATEGIC CAPACITY & RISK ASSESSMENT")

    date_string = datetime.now().strftime("%d %B %Y").upper()
    canvas.setFillColor(colors.HexColor("#93B4D8"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(
        PAGE_WIDTH - MARGIN_RIGHT, text_y,
        f"{date_string}  ·  CONFIDENTIAL  ·  PAGE {page_number}",
    )


def draw_footer(canvas: Any) -> None:
    """Render the full-width navy footer bar with document metadata."""
    canvas.setFillColor(Palette.NAVY)
    canvas.rect(0, 0, PAGE_WIDTH, FOOTER_HEIGHT, fill=1, stroke=0)

    # Blue accent stripe at the top of the footer
    canvas.setFillColor(Palette.BLUE)
    canvas.rect(0, FOOTER_HEIGHT, PAGE_WIDTH, 1, fill=1, stroke=0)

    canvas.setFillColor(Palette.TEXT_MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(MARGIN_LEFT, 5 * mm, "BER-MUC E-COMMERCE CORRIDOR  ·  DIGITAL TWIN ANALYSIS")

    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, 5 * mm, "FOR INTERNAL USE ONLY")


def draw_sidebar(canvas: Any, metrics: OperationalMetrics) -> None:
    """
    Render the telemetry dashboard sidebar entirely on the canvas layer.
    This keeps it visually fixed regardless of content flow on each page.
    """
    # Sidebar container
    draw_rounded_rect(
        canvas, SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT,
        radius=4, fill_color=Palette.BG_LIGHT,
        stroke_color=Palette.BORDER, line_width=0.5,
    )

    # Dashboard header block
    header_height = 12 * mm
    header_y = SIDEBAR_Y + SIDEBAR_HEIGHT - header_height
    draw_rounded_rect(canvas, SIDEBAR_X, header_y, SIDEBAR_WIDTH, header_height,
                      radius=4, fill_color=Palette.NAVY_MID)
    # Square off the bottom corners of the header block
    canvas.setFillColor(Palette.NAVY_MID)
    canvas.rect(SIDEBAR_X, header_y, SIDEBAR_WIDTH, header_height / 2, fill=1, stroke=0)

    canvas.setFillColor(Palette.WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(SIDEBAR_X + 4 * mm, SIDEBAR_Y + SIDEBAR_HEIGHT - 6.5 * mm, "TELEMETRY DASHBOARD")

    canvas.setFillColor(colors.HexColor("#93B4D8"))
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(SIDEBAR_X + 4 * mm, SIDEBAR_Y + SIDEBAR_HEIGHT - 10 * mm, "Live operational metrics")

    # Cursor tracks the current vertical drawing position
    cursor_y = SIDEBAR_Y + SIDEBAR_HEIGHT - header_height - 1 * mm

    def draw_section_header(title: str) -> None:
        nonlocal cursor_y
        cursor_y -= SECTION_HEIGHT + 1 * mm
        canvas.setFillColor(Palette.NAVY)
        canvas.rect(SIDEBAR_X + 2 * mm, cursor_y, SIDEBAR_WIDTH - 4 * mm, SECTION_HEIGHT, fill=1, stroke=0)
        # Blue left-edge accent pip
        canvas.setFillColor(Palette.BLUE)
        canvas.rect(SIDEBAR_X + 2 * mm, cursor_y, 2, SECTION_HEIGHT, fill=1, stroke=0)
        canvas.setFillColor(Palette.WHITE)
        canvas.setFont("Helvetica-Bold", 6.5)
        canvas.drawString(SIDEBAR_X + 5.5 * mm, cursor_y + 2.5 * mm, title.upper())

    def draw_metric_row(label: str, value: str, value_color: colors.Color | None = None,
                        shaded: bool = False) -> None:
        nonlocal cursor_y
        cursor_y -= ROW_HEIGHT
        if shaded:
            canvas.setFillColor(Palette.BG_ALT)
            canvas.rect(SIDEBAR_X + 2 * mm, cursor_y, SIDEBAR_WIDTH - 4 * mm, ROW_HEIGHT, fill=1, stroke=0)

        canvas.setFillColor(Palette.TEXT_MUTED)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(SIDEBAR_X + 4 * mm, cursor_y + 2.5 * mm, label)

        canvas.setFillColor(value_color if value_color else Palette.NAVY)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawRightString(SIDEBAR_X + SIDEBAR_WIDTH - 3 * mm, cursor_y + 2.2 * mm, value)

    def draw_gauge_bar(value: float, maximum: float, bar_color: colors.Color) -> None:
        """Render a proportional fill bar below the preceding metric row."""
        nonlocal cursor_y
        cursor_y -= 5 * mm
        bar_width  = SIDEBAR_WIDTH - 8 * mm
        bar_height = 3.5 * mm
        bar_x      = SIDEBAR_X + 4 * mm

        # Track background
        canvas.setFillColor(Palette.BORDER)
        canvas.roundRect(bar_x, cursor_y, bar_width, bar_height, 1.5, fill=1, stroke=0)

        # Filled portion
        fill_width = bar_width * min(value / maximum, 1.0)
        if fill_width > 0:
            canvas.setFillColor(bar_color)
            canvas.roundRect(bar_x, cursor_y, fill_width, bar_height, 1.5, fill=1, stroke=0)

        canvas.setFillColor(Palette.TEXT_MUTED)
        canvas.setFont("Helvetica", 6)
        canvas.drawRightString(
            SIDEBAR_X + SIDEBAR_WIDTH - 3 * mm,
            cursor_y + 1 * mm,
            f"{value:.0f} / {maximum:.0f}",
        )

    # -- Configuration section
    draw_section_header("Configuration")
    draw_metric_row("Transport Mode", metrics.transport_mode, shaded=True)
    draw_metric_row("SLA Target", f"{metrics.sla:.1%}")

    # -- Operations section
    draw_section_header("Operations")
    draw_metric_row("Avg Demand", f"{metrics.avg_demand:.0f} units", shaded=True)
    draw_metric_row("Volatility (sd)", f"{metrics.std_dev:.0f} units")
    draw_metric_row("Safety Stock", f"{metrics.safety_stock:.0f} units", Palette.RED, shaded=True)

    # -- Risk profile section
    draw_section_header("Risk Profile")
    draw_metric_row("Resilience Score", f"{metrics.resilience_score:.1f}/100",
                    metrics.resilience_color, shaded=True)
    draw_gauge_bar(metrics.resilience_score, 100, metrics.resilience_color)
    draw_metric_row("Dependency Ratio", f"{metrics.dependency_ratio:.1f}%")

    # -- Environmental impact section
    draw_section_header("Environmental Impact")
    draw_metric_row("CO2 Emissions", f"{metrics.co2_emissions:,.0f} kg", shaded=True)
    draw_metric_row("Loyalty Score", f"{metrics.loyalty_score:.0f}/100")

    # -- Outsourcing alert box
    cursor_y -= 10 * mm
    alert_height = 10 * mm
    alert_x = SIDEBAR_X + 2 * mm
    alert_width = SIDEBAR_WIDTH - 4 * mm

    canvas.setFillColor(colors.HexColor("#FEF3C7"))
    canvas.roundRect(alert_x, cursor_y - alert_height, alert_width, alert_height, 2, fill=1, stroke=0)
    canvas.setStrokeColor(Palette.GOLD)
    canvas.setLineWidth(0.8)
    canvas.roundRect(alert_x, cursor_y - alert_height, alert_width, alert_height, 2, fill=0, stroke=1)

    canvas.setFillColor(Palette.GOLD)
    canvas.setFont("Helvetica-Bold", 6.5)
    canvas.drawString(SIDEBAR_X + 4 * mm, cursor_y - 1.5 * mm, "!  OUTSOURCING ACTIVE")

    canvas.setFillColor(colors.HexColor("#92400E"))
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(SIDEBAR_X + 4 * mm, cursor_y - 5.5 * mm, "26 units externally sourced")


# ---------------------------------------------------------------------------
# Matplotlib chart
# ---------------------------------------------------------------------------

def render_demand_chart(metrics: OperationalMetrics) -> str:
    """
    Render the normal demand distribution chart to a temporary PNG file.
    Returns the file path. Caller is responsible for deleting the file.
    """
    mu    = metrics.avg_demand
    sigma = metrics.std_dev
    cap   = metrics.capacity_threshold

    x_values  = np.linspace(mu - 4.5 * sigma, mu + 4.5 * sigma, 500)
    pdf_curve = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_values - mu) / sigma) ** 2)
    peak      = pdf_curve.max()

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#F8FAFC")

    # Shaded regions
    ax.fill_between(x_values, pdf_curve, where=(x_values <= cap),
                    color=Palette.CHART_SAFE, alpha=0.9, zorder=2)
    ax.fill_between(x_values, pdf_curve, where=(x_values >= cap),
                    color=Palette.CHART_RISK, alpha=0.9, zorder=2)

    # Distribution curve
    ax.plot(x_values, pdf_curve, color=Palette.CHART_CURVE, linewidth=2.2, zorder=3)

    # Reference lines
    ax.axvline(mu,  color=Palette.CHART_MEAN, linestyle=":",  linewidth=1.4, alpha=0.8, zorder=4)
    ax.axvline(cap, color=Palette.CHART_CAP,  linestyle="--", linewidth=1.8,            zorder=4)

    # Inline annotations
    annotation_style = dict(fontsize=8, ha="center", fontfamily="monospace")
    ax.annotate(f"mu = {mu:.0f}", xy=(mu, peak * 0.60),
                color=Palette.CHART_MEAN,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=Palette.CHART_SAFE, lw=0.8),
                **annotation_style)
    ax.annotate(f"Cap = {cap:.0f}", xy=(cap, peak * 0.25),
                color=Palette.CHART_CAP,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=Palette.CHART_RISK, lw=0.8),
                **annotation_style)

    # Legend
    legend_patches = [
        mpatches.Patch(color=Palette.CHART_SAFE, label="Within Capacity"),
        mpatches.Patch(color=Palette.CHART_RISK, label="Overflow Risk"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, framealpha=1,
              edgecolor="#E2E8F0", loc="upper left", facecolor="white")

    # Axes formatting
    ax.set_xlabel("Demand Volume (Units)", fontsize=9, color="#475569", labelpad=5)
    ax.set_ylabel("Probability Density",   fontsize=9, color="#475569", labelpad=5)
    ax.tick_params(colors="#94A3B8", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#E2E8F0")
    ax.spines["bottom"].set_color("#E2E8F0")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#E2E8F0", linewidth=0.5)
    ax.set_axisbelow(True)

    fig.tight_layout(pad=1.0)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp_file.name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return tmp_file.name


# ---------------------------------------------------------------------------
# Platypus flowables
# ---------------------------------------------------------------------------

class SectionHeader(Flowable):
    """A full-width navy banner with a blue left-edge accent, used as a section divider."""

    BANNER_HEIGHT = 7 * mm

    def __init__(self, title: str, width: float = CONTENT_WIDTH) -> None:
        super().__init__()
        self.title = title
        self.width = width
        self.height = self.BANNER_HEIGHT + 2 * mm

    def wrap(self, available_width: float, available_height: float) -> tuple[float, float]:
        return self.width, self.height

    def draw(self) -> None:
        canvas = self.canv
        banner_y = 2 * mm

        canvas.setFillColor(Palette.NAVY)
        canvas.roundRect(0, banner_y, self.width, self.BANNER_HEIGHT, 3, fill=1, stroke=0)

        # Blue left-edge accent pip
        canvas.setFillColor(Palette.BLUE)
        canvas.roundRect(0, banner_y, 4, self.BANNER_HEIGHT, 2, fill=1, stroke=0)
        canvas.rect(2, banner_y, 4, self.BANNER_HEIGHT, fill=1, stroke=0)

        canvas.setFillColor(Palette.WHITE)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawString(8, banner_y + self.BANNER_HEIGHT / 2 - 3, self.title.upper())


class KPICardRow(Flowable):
    """
    A horizontal row of metric cards, each with a coloured top-border accent,
    large value display, a label, and a sub-label.
    """

    CARD_HEIGHT  = 20 * mm
    CARD_GAP     = 3 * mm

    def __init__(
        self,
        cards: list[tuple[str, str, str, colors.Color]],
        width: float = CONTENT_WIDTH,
    ) -> None:
        """
        Parameters
        ----------
        cards:
            List of ``(label, value, sub_label, accent_color)`` tuples.
        width:
            Total available width for the row.
        """
        super().__init__()
        self.cards = cards
        self.width = width

    def wrap(self, available_width: float, available_height: float) -> tuple[float, float]:
        return self.width, self.CARD_HEIGHT

    def draw(self) -> None:
        canvas = self.canv
        num_cards  = len(self.cards)
        card_width = (self.width - (num_cards - 1) * self.CARD_GAP) / num_cards

        for index, (label, value, sub_label, accent_color) in enumerate(self.cards):
            card_x = index * (card_width + self.CARD_GAP)

            # Card background with border
            canvas.setFillColor(Palette.WHITE)
            canvas.setStrokeColor(Palette.BORDER)
            canvas.setLineWidth(0.5)
            canvas.roundRect(card_x, 0, card_width, self.CARD_HEIGHT, 3, fill=1, stroke=1)

            # Coloured top accent bar
            accent_height = 2.5
            canvas.setFillColor(accent_color)
            canvas.roundRect(card_x, self.CARD_HEIGHT - accent_height,
                             card_width, accent_height + 4, 3, fill=1, stroke=0)
            canvas.rect(card_x, self.CARD_HEIGHT - accent_height,
                        card_width, accent_height / 2, fill=1, stroke=0)

            text_x = card_x + 3 * mm

            # Small uppercase label
            canvas.setFillColor(Palette.TEXT_MUTED)
            canvas.setFont("Helvetica", 6)
            canvas.drawString(text_x, self.CARD_HEIGHT - 6.5 * mm, label.upper())

            # Large value
            canvas.setFillColor(Palette.NAVY)
            canvas.setFont("Helvetica-Bold", 14)
            canvas.drawString(text_x, self.CARD_HEIGHT - 13.5 * mm, value)

            # Sub-label at the bottom
            if sub_label:
                canvas.setFillColor(Palette.TEXT_MUTED)
                canvas.setFont("Helvetica", 6.5)
                canvas.drawString(text_x, 3 * mm, sub_label)


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------

BASE_TABLE_STYLE = TableStyle([
    ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("GRID",          (0, 0), (-1, -1), 0.3, Palette.BORDER),
])


def build_newsvendor_table() -> Table:
    """Construct the Newsvendor model variables breakdown table."""
    col_widths = [42 * mm, 28 * mm, CONTENT_WIDTH - 70 * mm]

    rows = [
        [
            Paragraph("Variable",    make_style("table_header")),
            Paragraph("Value",       make_style("table_header")),
            Paragraph("Description", make_style("table_header")),
        ],
        [
            Paragraph('C<sub rise="2" size="7">u</sub>  (Understocking)', make_style("table_cell")),
            Paragraph("USD 35.0", make_style("table_cell_highlight")),
            Paragraph("Unit margin lost per stockout",        make_style("table_cell")),
        ],
        [
            Paragraph('C<sub rise="2" size="7">o</sub>  (Overstocking)', make_style("table_cell")),
            Paragraph("USD 18.5", make_style("table_cell_highlight")),
            Paragraph("Per-unit holding cost per period",     make_style("table_cell")),
        ],
        [
            Paragraph("SL*  (Optimal)", make_style("table_cell")),
            Paragraph("65.4%", make_style("table_cell", textColor=Palette.GREEN,
                                          fontName="Helvetica-Bold")),
            Paragraph("Newsvendor critical ratio",            make_style("table_cell")),
        ],
    ]

    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        *BASE_TABLE_STYLE._cmds,
        ("BACKGROUND",    (0, 0), (-1, 0),  Palette.NAVY_MID),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [Palette.WHITE, Palette.BG_LIGHT]),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.5, Palette.BLUE),
        ("LINEBELOW",     (0, -1), (-1, -1), 0.5, Palette.BORDER),
    ]))
    return table


def build_action_table(actions: list[tuple[str, str, str]]) -> Table:
    """
    Construct the numbered strategic recommendations table.

    Parameters
    ----------
    actions:
        List of ``(number, title, body_text)`` tuples.
    """
    rows = []
    for number, title, body in actions:
        number_cell = Paragraph(f"<b>{number}</b>", make_style("number_label"))

        content_cell = Table(
            [[Paragraph(title, make_style("action_title"))],
             [Paragraph(body,  make_style("action_body"))]],
            colWidths=[CONTENT_WIDTH - 16 * mm],
        )
        content_cell.setStyle(TableStyle([
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))

        rows.append([number_cell, content_cell])

    # Alternate the number-cell background between two navy shades
    number_backgrounds = [
        ("BACKGROUND", (0, i), (0, i), Palette.NAVY if i % 2 == 0 else Palette.NAVY_MID)
        for i in range(len(rows))
    ]

    table = Table(rows, colWidths=[10 * mm, CONTENT_WIDTH - 10 * mm])
    table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.4, Palette.BORDER),
        ("BACKGROUND",    (1, 0), (1, -1),  Palette.WHITE),
        *number_backgrounds,
    ]))
    return table


# ---------------------------------------------------------------------------
# Content builder
# ---------------------------------------------------------------------------

def build_story(metrics: OperationalMetrics) -> list[Any]:
    """
    Assemble the ordered list of Platypus flowables that form the report body.
    The sidebar and chrome (header/footer) are handled separately on the canvas.
    """
    story: list[Any] = []

    # -- Title block
    story.append(Paragraph("BER-MUC E-COMMERCE CORRIDOR", make_style("h1")))
    story.append(Paragraph(
        "Quantitative Capacity &amp; Risk Analysis  ·  Digital Twin Report  ·  Road (Standard)",
        make_style("subtitle"),
    ))
    story.append(HRFlowable(width=CONTENT_WIDTH, thickness=0.5,
                            color=Palette.BORDER, spaceAfter=5 * mm))

    # -- KPI summary cards
    kpi_cards: list[tuple[str, str, str, colors.Color]] = [
        ("Utilization Rate",  "117.3%",                      "vs 150-unit capacity",    Palette.RED),
        ("Resilience Score",  f"{metrics.resilience_score:.0f}/100", "operational robustness",  metrics.resilience_color),
        ("Optimal SLA",       "65.4%",                       "Newsvendor model",         Palette.NAVY_MID),
        ("Safety Stock",      f"{metrics.safety_stock:.0f} u", "55.7% of avg demand",   Palette.GOLD),
    ]
    story.append(KPICardRow(kpi_cards))
    story.append(Spacer(1, 5 * mm))

    # -- Section 1: Quantitative analysis
    story.append(SectionHeader("Quantitative Analysis"))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f"The digital twin data for the BER-MUC lane reveals an operation characterized by high resilience "
        f"(<b>{metrics.resilience_score:.1f}/100</b>) but significant capacity imbalances and elevated "
        f"unit-level holding costs. Current utilization stands at <b>117.3%</b> relative to internal "
        f"warehouse capacity (150 units), necessitating the outsourcing of <b>26 units</b> to external providers.",
        make_style("body"),
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "The <b>Newsvendor model</b> identifies an optimal Service Level of <b>65.4%</b>, derived from "
        "the critical ratio of understocking cost to total mismatch cost:",
        make_style("body"),
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "SL* = C<sub rise=\"2\" size=\"7\">u</sub> / "
        "(C<sub rise=\"2\" size=\"7\">u</sub> + C<sub rise=\"2\" size=\"7\">o</sub>)"
        "  =  35.0 / (35.0 + 18.5)  approx  <b>0.654</b>",
        make_style("equation"),
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(build_newsvendor_table())
    story.append(Spacer(1, 5 * mm))

    # -- Section 2: Strategic recommendations
    story.append(SectionHeader("Strategic Recommendations"))
    story.append(Spacer(1, 3 * mm))
    story.append(build_action_table([
        (
            "1",
            "Inventory Policy Re-Calibration",
            "The current safety stock of 63 units (55.7% of average demand) is aggressive relative to "
            "the 65.4% Newsvendor optimum. At USD 18.5 per unit holding cost, the overstocking burden is "
            "substantial. Rationalizing buffers to the critical ratio target could bring total capacity "
            "used (currently 176 units) back within the 150-unit internal limit, eliminating costly "
            "outsourcing entirely.",
        ),
        (
            "2",
            "Capacity-as-a-Service (CaaS) Optimization",
            "The ACTIVE cooperation status underpins the high Resilience Score (84.6/100), yet the "
            "26-unit outsourcing requirement signals a structural capacity deficit. Converting ad-hoc "
            "outsourcing into a formal CaaS contract enables rigorous cost benchmarking: where the "
            "outsourcing unit cost is less than internal expansion cost plus holding risk premium, "
            "maintain a Lean Internal / Scalable External operating model.",
        ),
        (
            "3",
            "Intermodal Shift for Decarbonization & Margin Recovery",
            f"CO2 emissions of {metrics.co2_emissions:,.0f} kg are material for this E-Commerce lane "
            f"where customer loyalty ({metrics.loyalty_score:.0f}/100) is an ESG-sensitive asset. "
            "A shift from Road (Standard) to Rail-Road Intermodal would materially reduce the carbon "
            "footprint. Lead-time variability can be absorbed by the strong Resilience Score, while "
            "lower emissions support a Green Premium pricing strategy to improve the USD 35.0 margin.",
        ),
    ]))
    story.append(Spacer(1, 5 * mm))

    # -- Section 3: Capacity risk chart
    story.append(SectionHeader("Capacity Risk Distribution"))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f"Normal demand distribution (mean={metrics.avg_demand:.0f}, sd={metrics.std_dev:.0f}) "
        f"with safety threshold at {metrics.capacity_threshold:.0f} units. "
        "Blue zone = within-capacity probability mass. Red zone = overflow risk.",
        make_style("small"),
    ))
    story.append(Spacer(1, 3 * mm))

    chart_path: str | None = None
    try:
        chart_path = render_demand_chart(metrics)
        story.append(Image(chart_path, width=CONTENT_WIDTH, height=85 * mm))
    except Exception as exc:  # noqa: BLE001
        story.append(Paragraph(f"Chart unavailable: {exc}", make_style("small")))

    return story, chart_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pdf(metrics_dict: dict[str, Any], ai_summary: str = "") -> bytes:
    """
    Generate the strategic report PDF and return it as raw bytes.

    Parameters
    ----------
    metrics_dict:
        Raw operational data. All recognised keys are mapped to
        ``OperationalMetrics``; unknown keys are silently ignored.
    ai_summary:
        Optional text to prepend before the main analysis sections.
        Reserved for future LLM-generated narrative injection.

    Returns
    -------
    bytes
        The complete PDF file contents.
    """
    metrics = OperationalMetrics.from_dict(metrics_dict)

    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

    content_frame = Frame(
        CONTENT_X, CONTENT_Y, CONTENT_WIDTH, CONTENT_HEIGHT,
        leftPadding=0, rightPadding=0,
        topPadding=5 * mm, bottomPadding=2 * mm,
    )

    def on_page(canvas: Any, document: Any) -> None:
        draw_header(canvas, document.page)
        draw_footer(canvas)
        draw_sidebar(canvas, metrics)

    page_template = PageTemplate(id="main", frames=[content_frame], onPage=on_page)

    document = BaseDocTemplate(
        tmp_path, pagesize=A4,
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        topMargin=HEADER_HEIGHT, bottomMargin=FOOTER_HEIGHT,
    )
    document.addPageTemplates([page_template])

    story, chart_path = build_story(metrics)
    document.build(story)

    with open(tmp_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    # Clean up temporary files
    os.unlink(tmp_path)
    if chart_path and os.path.exists(chart_path):
        os.unlink(chart_path)

    return pdf_bytes


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_metrics = {
        "transport_mode":   "Road (Standard)",
        "sla":              0.95,
        "avg_demand":       113,
        "std_dev":          30,
        "safety_stock":     63,
        "resilience_score": 84.6,
        "dependency_ratio": 15.0,
        "co2_emissions":    2138.83,
        "loyalty_score":    81.7,
    }

    pdf_bytes = generate_pdf(sample_metrics)

    output_path = "/mnt/user-data/outputs/Strategic_Report_BER_MUC_final.pdf"
    with open(output_path, "wb") as output_file:
        output_file.write(pdf_bytes)

    print(f"Report written to: {output_path}  ({len(pdf_bytes):,} bytes)")


# Code by Claude ReportLab (Platypus) — a proper document layout engine
