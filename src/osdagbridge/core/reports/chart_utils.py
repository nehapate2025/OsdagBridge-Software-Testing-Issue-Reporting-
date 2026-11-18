"""
OsdagBridge Report Chart Generation Utilities
=============================================

Reusable chart creation helpers for OsdagBridge PDF engineering reports.
Generates high-resolution Matplotlib figures (300 DPI) matching the report's
centralized visual style (defined in styles.py).

Provides:
- `create_ur_bar_chart`: Standardized bar charts for Utilization Ratios (UR = Demand / Capacity)
  with a red dashed horizontal reference line at UR = 1.0, value annotations above bars,
  and color differentiation for passing (UR <= 1.0) vs exceeding (UR > 1.0) checks.
- `create_unavailable_chart`: Informative graphic card for unavailable or unsupported checks
  (e.g., Rolled / Welded end diaphragms where design check is not implemented).
- Component-specific UR data extractors:
  - Steel Plate Girder: Moment, Shear, LTB, Deflection, Stress, Fatigue
  - Concrete Deck Slab: Flexure (sagging, hogging, overhang), Punching shear, One-way shear
  - Cross Bracing: Compression, Tension, Slenderness for diagonal and chord members
  - End Diaphragm: Cross-bracing results when configured as bracing; clear unavailable message
    for Rolled / Welded sections where moment/shear design is not implemented
- `generate_ch5_ur_charts`: High-level orchestrator that creates and returns file paths
  for all four Section 5.5 UR charts.
"""

import os
import zlib
import struct
import tempfile
import logging
from typing import List, Tuple, Dict, Optional, Any

from .styles import (
    CHART_COLOR_PRIMARY,
    CHART_COLOR_SECONDARY,
    CHART_COLOR_ACCENT,
    CHART_COLOR_SUCCESS,
    CHART_COLOR_WARNING,
    CHART_COLOR_DANGER,
    CHART_COLOR_INFO,
    CHART_COLOR_GRID,
    CHART_DPI,
    CHART_FIGURE_WIDTH,
    CHART_FIGURE_HEIGHT,
    CHART_LINE_WIDTH,
    CHART_FONT_FAMILY,
    CHART_TITLE_FONTSIZE,
    CHART_LABEL_FONTSIZE,
    CHART_TICK_FONTSIZE,
    CHART_LEGEND_FONTSIZE,
)

logger = logging.getLogger(__name__)

# Attempt to load matplotlib; enable headless Agg backend
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("Matplotlib is not installed. Chart generation will use fallback mode.")


def _create_fallback_png(path: str, width: int = 400, height: int = 240, color: Tuple[int, int, int] = (245, 245, 245)) -> str:
    """Generate a minimal valid PNG file if matplotlib is absent."""
    png = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data))
    png += struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + ihdr_crc
    raw_row = b'\x00' + bytes(color) * width
    compressed = zlib.compress(raw_row * height)
    idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed))
    png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc
    png += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND'))
    
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png)
    return path.replace('\\', '/')


# =============================================================================
# 1. REUSABLE CHART CREATION FUNCTIONS
# =============================================================================

def create_ur_bar_chart(
    categories: List[str],
    values: List[float],
    title: str,
    output_path: str,
    subtitle: Optional[str] = None,
    ur_limit: float = 1.0,
    figsize: Tuple[float, float] = (6.5, 3.2),
    dpi: int = CHART_DPI,
) -> str:
    """
    Generate a standardized engineering Utilization Ratio (UR) bar chart.

    Parameters
    ----------
    categories : List[str]
        Labels for each design check bar.
    values : List[float]
        Actual UR (Demand / Capacity) values.
    title : str
        Main descriptive chart title.
    output_path : str
        Target file path for saving the PNG image.
    subtitle : Optional[str]
        Secondary descriptor (e.g. governing girder or code limit note).
    ur_limit : float
        Reference capacity threshold (default 1.0).
    figsize : Tuple[float, float]
        Figure dimensions in inches (default 6.5 x 3.2 for A4 reports).
    dpi : int
        Resolution (default 300 DPI).

    Returns
    -------
    str : Normalized forward-slash path to the saved image.
    """
    if not HAS_MATPLOTLIB:
        return _create_fallback_png(output_path)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Color each bar: Osdag green if UR <= 1.0, Danger red if UR > 1.0
    bar_colors = [
        CHART_COLOR_DANGER if (v is not None and v > ur_limit) else CHART_COLOR_PRIMARY
        for v in values
    ]

    x_indices = list(range(len(categories)))
    bar_width = 0.52 if len(categories) <= 6 else 0.65
    bars = ax.bar(
        x_indices,
        values,
        color=bar_colors,
        width=bar_width,
        edgecolor="#333333",
        linewidth=0.75,
        zorder=3,
    )

    # Add numeric UR text annotation directly above each bar
    for bar, val in zip(bars, values):
        height = bar.get_height()
        val_str = f"{val:.2f}"
        # Visually emphasize exceeding values with bold dark red text
        txt_color = CHART_COLOR_DANGER if val > ur_limit else "#222222"
        ax.annotate(
            val_str,
            xy=(bar.get_x() + bar.get_width() / 2.0, height),
            xytext=(0, 3.5),  # 3.5 points vertical offset
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=CHART_TICK_FONTSIZE + 1,
            fontweight="bold",
            color=txt_color,
        )

    # Red dashed reference line at UR = 1.0
    limit_line = ax.axhline(
        ur_limit,
        color=CHART_COLOR_DANGER,
        linestyle="--",
        linewidth=1.4,
        zorder=4,
        label=f"Code Limit (UR = {ur_limit:.1f})",
    )

    # Y-axis scaling ensuring ample headroom for UR = 1.0 line and value labels
    max_val = max(values) if values else 1.0
    y_top = max(1.25, max_val * 1.22)
    ax.set_ylim(0.0, y_top)

    # Labels and typography
    ax.set_ylabel("Utilization Ratio (UR)", fontsize=CHART_LABEL_FONTSIZE, fontweight="bold", labelpad=8)
    
    full_title = title
    if subtitle:
        full_title += f"\n({subtitle})"
    ax.set_title(full_title, fontsize=CHART_TITLE_FONTSIZE, fontweight="bold", pad=10)

    # X-axis ticks and labels
    ax.set_xticks(x_indices)
    ax.set_xticklabels(categories, fontsize=CHART_TICK_FONTSIZE, fontweight="medium")

    # Rotate labels if more than 5 categories or if any label is long
    has_long_labels = any(len(c) > 12 or "\n" in c for c in categories)
    if len(categories) > 5 or has_long_labels:
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right")

    ax.tick_params(axis="y", labelsize=CHART_TICK_FONTSIZE)

    # Light background grid lines on Y-axis
    ax.grid(axis="y", linestyle="--", alpha=0.5, color=CHART_COLOR_GRID, zorder=1)
    ax.set_axisbelow(True)

    # Clear, descriptive legend identifying the reference limit and status
    has_exceeding = any(v > ur_limit for v in values)
    legend_elements = [limit_line]
    legend_elements.append(
        mpatches.Patch(facecolor=CHART_COLOR_PRIMARY, edgecolor="#333333", linewidth=0.75, label="Pass (UR $\\leq$ 1.0)")
    )
    if has_exceeding:
        legend_elements.append(
            mpatches.Patch(facecolor=CHART_COLOR_DANGER, edgecolor="#333333", linewidth=0.75, label="Exceeds Limit (UR > 1.0)")
        )

    ax.legend(
        handles=legend_elements,
        loc="upper right",
        fontsize=CHART_LEGEND_FONTSIZE,
        framealpha=0.90,
        edgecolor="#D0D0D0",
    )

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    return output_path.replace("\\", "/")


def create_unavailable_chart(
    title: str,
    message: str,
    output_path: str,
    detail: Optional[str] = None,
    figsize: Tuple[float, float] = (6.5, 2.4),
    dpi: int = CHART_DPI,
) -> str:
    """
    Generate an informative graphic card for unavailable or unimplemented design checks.

    Parameters
    ----------
    title : str
        Component title (e.g. 'End Diaphragm Utilization Ratio').
    message : str
        Primary status message (e.g. 'Utilization ratio unavailable — design check not implemented.').
    output_path : str
        Target file path for saving the PNG image.
    detail : Optional[str]
        Supplementary engineering context or reason.
    figsize : Tuple[float, float]
        Figure dimensions in inches.
    dpi : int
        Resolution.

    Returns
    -------
    str : Normalized forward-slash path to the saved image.
    """
    if not HAS_MATPLOTLIB:
        return _create_fallback_png(output_path, color=(248, 248, 248))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Draw a clean border box with subtle fill
    card = mpatches.FancyBboxPatch(
        (0.04, 0.08),
        0.92,
        0.84,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        facecolor="#FBFBFB",
        edgecolor="#C0C0C0",
        linewidth=1.2,
        linestyle="-",
        transform=ax.transAxes,
    )
    ax.add_patch(card)

    # Title
    ax.text(
        0.5,
        0.75,
        title,
        ha="center",
        va="center",
        fontsize=CHART_TITLE_FONTSIZE,
        fontweight="bold",
        color="#222222",
        transform=ax.transAxes,
    )

    # Primary Message
    ax.text(
        0.5,
        0.48,
        message,
        ha="center",
        va="center",
        fontsize=CHART_LABEL_FONTSIZE,
        fontweight="bold",
        color="#7F8C8D",
        transform=ax.transAxes,
    )

    # Detail / note
    if detail:
        ax.text(
            0.5,
            0.26,
            detail,
            ha="center",
            va="center",
            fontsize=CHART_TICK_FONTSIZE + 1,
            fontstyle="italic",
            color="#555555",
            transform=ax.transAxes,
        )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    return output_path.replace("\\", "/")


# =============================================================================
# 2. DATA EXTRACTION HELPERS FOR SECTION 5.5 CHARTS
# =============================================================================

def extract_girder_ur_data(bridge: Any) -> Tuple[bool, List[str], List[float], str]:
    """
    Extract actual Demand/Capacity Ratio (DCR) values for Steel Plate Girder checks.

    Checks:
    - Moment (Check ID 1, Strength – Flexure)
    - Shear (Check ID 2, Strength – Shear)
    - Lateral Torsional Buckling (Check ID 5, LTB)
    - Deflection (Check IDs 13, 14, Deflection Check)
    - Stress (Check ID 11, SLS Stress Limitation)
    - Fatigue (Check IDs 8, 9, Fatigue)

    Returns
    -------
    (has_data, categories, values, subtitle)
    """
    pg_dict = (bridge.output_dict.get("design_results", {}) or {}).get("per_girder", {}) or {}

    check_specs = [
        ("Moment", {1}),
        ("Shear", {2}),
        ("LTB", {5}),
        ("Deflection", {13, 14}),
        ("Stress", {11}),
        ("Fatigue", {8, 9}),
    ]

    categories: List[str] = []
    values: List[float] = []
    governing_girders: set = set()

    for label, cids in check_specs:
        best_dcr = None
        best_g = None

        # 1. Prefer per_girder["checks"]
        for g, gd in pg_dict.items():
            if str(g).startswith("EB"):
                continue
            for chk in (gd.get("checks") or []):
                if chk.get("check_id") in cids:
                    d = chk.get("dcr")
                    if d is not None:
                        try:
                            df = float(d)
                            if best_dcr is None or df > best_dcr:
                                best_dcr = df
                                best_g = g
                        except (TypeError, ValueError):
                            pass

        # 2. Fallback to per_lc for SLS checks (e.g. deflection)
        if best_dcr is None:
            for g, gd in pg_dict.items():
                if str(g).startswith("EB"):
                    continue
                for _lc, _ld in (gd.get("per_lc") or {}).items():
                    if str(_lc).lower().startswith("envelope"):
                        continue
                    for chk in (_ld.get("checks") or []):
                        if chk.get("id") in cids:
                            d = chk.get("dcr")
                            if d is not None:
                                try:
                                    df = float(d)
                                    if best_dcr is None or df > best_dcr:
                                        best_dcr = df
                                        best_g = g
                                except (TypeError, ValueError):
                                    pass

        if best_dcr is not None:
            lbl = f"{label} ({best_g})" if best_g else label
            categories.append(lbl)
            values.append(best_dcr)
            if best_g:
                governing_girders.add(str(best_g))

    if not values:
        return False, [], [], "Governing checks across girders"

    g_desc = f"Governing values across girders ({', '.join(sorted(governing_girders))})" if governing_girders else "Governing checks across all girders"
    return True, categories, values, g_desc


def extract_deck_ur_data(bridge: Any) -> Tuple[bool, List[str], List[float], str]:
    """
    Extract actual Demand/Capacity values and compute UR for Concrete Deck Slab.

    Checks:
    - Flexure (sagging): KEY_DD_M_ULS_SAG / KEY_DD_MU_BOT
    - Flexure (hogging): KEY_DD_M_ULS_HOG / KEY_DD_MU_TOP
    - Cantilever overhang: KEY_DD_M_ULS_OH / KEY_DD_MU_OH (if overhang present)
    - Punching shear: KEY_DD_PUNCH_VED / KEY_DD_VRD_C_MPA
    - One-way shear: KEY_DD_SHEAR_VED / KEY_DD_SHEAR_VRDC

    Returns
    -------
    (has_data, categories, values, subtitle)
    """
    from osdagbridge.core.utils.common import (
        KEY_DD_M_ULS_SAG,
        KEY_DD_MU_BOT,
        KEY_DD_M_ULS_HOG,
        KEY_DD_MU_TOP,
        KEY_DD_M_ULS_OH,
        KEY_DD_MU_OH,
        KEY_DD_HAS_OVERHANG,
        KEY_DD_PUNCH_VED,
        KEY_DD_VRD_C_MPA,
        KEY_DD_SHEAR_VED,
        KEY_DD_SHEAR_VRDC,
    )

    deck_rpt = bridge.output_dict.get("deck_report_values", {}) or {}
    if not deck_rpt:
        deck_rpt = bridge.output_dict.get("deck_design_results", {}) or {}

    if not deck_rpt:
        return False, [], [], "IRC 6 Basic ULS combination"

    def _get_val(k: str) -> Optional[float]:
        v = deck_rpt.get(k)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _calc_ur(dem_k: str, cap_k: str) -> Optional[float]:
        dem = _get_val(dem_k)
        cap = _get_val(cap_k)
        if dem is not None and cap is not None and cap > 0.0:
            return dem / cap
        return None

    categories: List[str] = []
    values: List[float] = []

    # 1. Flexure (sagging)
    ur_sag = _calc_ur(KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT)
    if ur_sag is not None:
        categories.append("Flexure\n(Sagging)")
        values.append(ur_sag)

    # 2. Flexure (hogging)
    ur_hog = _calc_ur(KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP)
    if ur_hog is not None:
        categories.append("Flexure\n(Hogging)")
        values.append(ur_hog)

    # 3. Cantilever overhang
    if bool(deck_rpt.get(KEY_DD_HAS_OVERHANG)):
        ur_oh = _calc_ur(KEY_DD_M_ULS_OH, KEY_DD_MU_OH)
        if ur_oh is not None:
            categories.append("Cantilever\nOverhang")
            values.append(ur_oh)

    # 4. Punching shear
    ur_punch = _calc_ur(KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA)
    if ur_punch is not None:
        categories.append("Punching\nShear")
        values.append(ur_punch)

    # 5. One-way shear
    ur_shear = _calc_ur(KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC)
    if ur_shear is not None:
        categories.append("One-Way\nShear")
        values.append(ur_shear)

    if not values:
        return False, [], [], "IRC 6 Basic ULS combination"

    return True, categories, values, "IRC 6 Basic ULS combination (Demand / Capacity)"


def extract_cb_ur_data(bridge: Any) -> Tuple[bool, List[str], List[float], str]:
    """
    Extract actual Utilization Ratios for Cross Bracing members.

    Checks:
    - Compression (efficiency)
    - Tension (efficiency)
    - Slenderness (KL/r / limit)

    Returns
    -------
    (has_data, categories, values, subtitle)
    """
    try:
        pairs = bridge.get_cb_pairs()
    except Exception:
        pairs = []

    if not pairs:
        return False, [], [], "Design per IS 800:2007"

    raw_items: List[Tuple[str, float]] = []

    for pair in pairs:
        for member in ("diagonal", "chord"):
            # Compression
            comp_eff = bridge.get_cb_efficiency(pair, member, "compression")
            try:
                cf = float(comp_eff)
                raw_items.append((f"{pair} {member[:4].capitalize()}\nComp", cf))
            except (TypeError, ValueError):
                pass

            # Tension
            tens_eff = bridge.get_cb_efficiency(pair, member, "tension")
            try:
                tf = float(tens_eff)
                raw_items.append((f"{pair} {member[:4].capitalize()}\nTens", tf))
            except (TypeError, ValueError):
                pass

            # Slenderness
            slend_str = bridge.get_cb_slenderness(pair, member)
            try:
                sf = float(slend_str)
                lim = 400.0 if member == "chord" else 250.0
                raw_items.append((f"{pair} {member[:4].capitalize()}\nSlend", sf / lim))
            except (TypeError, ValueError):
                pass

    if not raw_items:
        return False, [], [], "Design per IS 800:2007"

    # If 8 or fewer member checks, display individual members
    if len(raw_items) <= 8:
        categories = [item[0] for item in raw_items]
        values = [item[1] for item in raw_items]
        return True, categories, values, "Individual member checks across panels (IS 800)"

    # If more than 8 checks across multiple panels, plot governing checks by category
    gov_by_type: Dict[str, Tuple[float, str]] = {}
    for label, val in raw_items:
        check_type = "Comp" if "Comp" in label else ("Tens" if "Tens" in label else "Slend")
        mem_type = "Diag" if "Diag" in label else "Chord"
        k = f"{mem_type} {check_type}"
        if k not in gov_by_type or val > gov_by_type[k][0]:
            gov_by_type[k] = (val, label.replace("\n", " "))

    categories = list(gov_by_type.keys())
    values = [gov_by_type[k][0] for k in categories]
    return True, categories, values, "Governing checks across bracing panels (IS 800)"


def extract_ed_ur_data(bridge: Any) -> Tuple[bool, List[str], List[float], str, str, Optional[str]]:
    """
    Extract actual Utilization Ratios for End Diaphragms or identify unsupported cases.

    Returns
    -------
    (has_data, categories, values, title, message, detail)
    """
    from osdagbridge.core.utils.common import KEY_MP_ED_TYPE

    ed_type = ""
    for _k, _v in bridge.input_dict.items():
        if str(_k).startswith(KEY_MP_ED_TYPE) and _v:
            ed_type = str(_v)
            break

    is_cb = "brac" in ed_type.strip().lower()

    title = "End Diaphragm Utilization Ratio"

    if not is_cb:
        # Rolled or Welded beam section — design check is not implemented
        return (
            False,
            [],
            [],
            title,
            "Utilization ratio unavailable — design check not implemented.",
            "Rolled / Welded section end-diaphragm moment and shear design is not implemented yet in OsdagBridge.",
        )

    # Cross Bracing configured: inspect end_diaphragm_design_results
    ed_designs = bridge.output_dict.get("end_diaphragm_design_results") or {}
    if not ed_designs:
        return (
            False,
            [],
            [],
            title,
            "Utilization ratio unavailable — end diaphragm design results not available.",
            "Cross-bracing end diaphragm was selected, but detailed member design outputs were not found.",
        )

    categories: List[str] = []
    values: List[float] = []

    for pair, pdata in ed_designs.items():
        if not isinstance(pdata, dict):
            continue
        for member in ("diagonal", "chord"):
            mdata = pdata.get(member) or {}
            for ft in ("compression", "tension"):
                fdata = mdata.get(ft) or {}
                eff = fdata.get("efficiency")
                if eff is not None:
                    try:
                        f_eff = float(eff)
                        categories.append(f"{pair} {member[:4].capitalize()}\n{ft[:4].capitalize()}")
                        values.append(f_eff)
                    except (TypeError, ValueError):
                        pass

    if not values:
        return (
            False,
            [],
            [],
            title,
            "Utilization ratio unavailable — end diaphragm design results not available.",
            "Cross-bracing end diaphragm results did not contain valid efficiency values.",
        )

    return (
        True,
        categories,
        values,
        title,
        "Cross-bracing end diaphragm member checks",
        None,
    )


# =============================================================================
# 3. HIGH-LEVEL ORCHESTRATOR
# =============================================================================

def generate_ch5_ur_charts(bridge: Any, output_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Generate all four Section 5.5 Utilization Ratio charts and return their file paths.

    Charts created:
    1. 'ur_girder': Steel Plate Girder UR
    2. 'ur_deck': Concrete Deck Slab UR
    3. 'ur_cross_bracing': Cross Bracing UR
    4. 'ur_end_diaphragm': End Diaphragm UR (or unavailable message graphic)

    Parameters
    ----------
    bridge : ReportDataBridge
        Bridge data bridge providing inputs, outputs, and design check results.
    output_dir : Optional[str]
        Directory where chart PNG images should be saved. If None, a temporary directory is created.

    Returns
    -------
    Dict[str, str] : Mapping from chart identifier to image file path.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="osdag_ch5_charts_")

    os.makedirs(output_dir, exist_ok=True)
    fig_paths: Dict[str, str] = {}

    # -------------------------------------------------------------------------
    # Chart 5.5.1: Steel Plate Girder Utilization Ratio
    # -------------------------------------------------------------------------
    p1 = os.path.join(output_dir, "ur_steel_plate_girder.png")
    has_g, g_cats, g_vals, g_sub = extract_girder_ur_data(bridge)
    if has_g:
        create_ur_bar_chart(
            categories=g_cats,
            values=g_vals,
            title="Steel Plate Girder — Utilization Ratio",
            subtitle=g_sub,
            output_path=p1,
        )
    else:
        create_unavailable_chart(
            title="Steel Plate Girder Utilization Ratio",
            message="Utilization ratio unavailable — design results not found.",
            detail="Girder design check results were not found in the output dictionary.",
            output_path=p1,
        )
    fig_paths["ur_girder"] = p1.replace("\\", "/")

    # -------------------------------------------------------------------------
    # Chart 5.5.2: Concrete Deck Slab Utilization Ratio
    # -------------------------------------------------------------------------
    p2 = os.path.join(output_dir, "ur_concrete_deck_slab.png")
    has_d, d_cats, d_vals, d_sub = extract_deck_ur_data(bridge)
    if has_d:
        create_ur_bar_chart(
            categories=d_cats,
            values=d_vals,
            title="Concrete Deck Slab — Utilization Ratio",
            subtitle=d_sub,
            output_path=p2,
        )
    else:
        create_unavailable_chart(
            title="Concrete Deck Slab Utilization Ratio",
            message="Utilization ratio unavailable — deck design not run.",
            detail="Concrete deck slab design check results were not found in the output dictionary.",
            output_path=p2,
        )
    fig_paths["ur_deck"] = p2.replace("\\", "/")

    # -------------------------------------------------------------------------
    # Chart 5.5.3: Cross Bracing Utilization Ratio
    # -------------------------------------------------------------------------
    p3 = os.path.join(output_dir, "ur_cross_bracing.png")
    has_cb, cb_cats, cb_vals, cb_sub = extract_cb_ur_data(bridge)
    if has_cb:
        create_ur_bar_chart(
            categories=cb_cats,
            values=cb_vals,
            title="Cross Bracing — Utilization Ratio",
            subtitle=cb_sub,
            output_path=p3,
        )
    else:
        create_unavailable_chart(
            title="Cross Bracing Utilization Ratio",
            message="Utilization ratio unavailable — cross bracing results not found.",
            detail="Cross-bracing member forces and design results were not found.",
            output_path=p3,
        )
    fig_paths["ur_cross_bracing"] = p3.replace("\\", "/")

    # -------------------------------------------------------------------------
    # Chart 5.5.4: End Diaphragm Utilization Ratio
    # -------------------------------------------------------------------------
    p4 = os.path.join(output_dir, "ur_end_diaphragm.png")
    has_ed, ed_cats, ed_vals, ed_title, ed_msg, ed_detail = extract_ed_ur_data(bridge)
    if has_ed:
        create_ur_bar_chart(
            categories=ed_cats,
            values=ed_vals,
            title=ed_title,
            subtitle=ed_msg,
            output_path=p4,
        )
    else:
        create_unavailable_chart(
            title=ed_title,
            message=ed_msg,
            detail=ed_detail,
            output_path=p4,
        )
    fig_paths["ur_end_diaphragm"] = p4.replace("\\", "/")

    return fig_paths


# =============================================================================
# 4. CHAPTER 7 MATERIAL QUANTITY CHARTS
# =============================================================================

def extract_structural_steel_data(inputs: dict) -> Tuple[List[str], List[Optional[float]], List[str]]:
    """
    Extract structural steel tonnage for Girders, Cross Bracing, and End Diaphragms.

    Returns
    -------
    (categories, values, display_strings)
    """
    categories = ["Steel Girders", "Cross Bracing", "End Diaphragms"]
    values: List[Optional[float]] = []
    display_strings: List[str] = []

    # 1. Steel Girders — MT
    g_raw = inputs.get("steel_girders_wt_total")
    try:
        if g_raw is not None and str(g_raw).strip() not in ("", "N.A.", "None"):
            g_val = float(g_raw)
            values.append(g_val)
            display_strings.append(f"{g_val:.2f} MT")
        else:
            values.append(None)
            display_strings.append("N.A.")
    except (TypeError, ValueError):
        values.append(None)
        display_strings.append("N.A.")

    # 2. Cross Bracing — MT
    # Combine top, bottom, and diagonal chords only when all are valid
    top_raw = inputs.get("bracing_top_wt_total")
    bot_raw = inputs.get("bracing_bot_wt_total")
    diag_raw = inputs.get("bracing_diag_wt_total")

    def _is_valid_wt(w: Any) -> bool:
        if w is None:
            return False
        s = str(w).strip()
        if not s or s in ("N.A.", "None"):
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    if _is_valid_wt(top_raw) and _is_valid_wt(bot_raw) and _is_valid_wt(diag_raw):
        try:
            cb_tot = float(top_raw) + float(bot_raw) + float(diag_raw)
            values.append(cb_tot)
            display_strings.append(f"{cb_tot:.2f} MT")
        except Exception:
            values.append(None)
            display_strings.append("N.A.")
    elif _is_valid_wt(inputs.get("steel_bracing_wt_total")):
        try:
            cb_single = float(inputs["steel_bracing_wt_total"])
            values.append(cb_single)
            display_strings.append(f"{cb_single:.2f} MT")
        except Exception:
            values.append(None)
            display_strings.append("N.A.")
    else:
        values.append(None)
        display_strings.append("N.A.")

    # 3. End Diaphragms — MT
    ed_raw = inputs.get("end_diaphragm_wt_total")
    if _is_valid_wt(ed_raw):
        try:
            ed_val = float(ed_raw)
            values.append(ed_val)
            display_strings.append(f"{ed_val:.2f} MT")
        except Exception:
            values.append(None)
            display_strings.append("Quantity unavailable")
    else:
        values.append(None)
        display_strings.append("Quantity unavailable")

    return categories, values, display_strings


def extract_concrete_rebar_data(inputs: dict) -> Tuple[Optional[float], str, Optional[float], str]:
    """
    Extract concrete deck volume (m³) and reinforcement steel weight (MT).

    Returns
    -------
    (conc_vol, conc_str, rebar_wt, rebar_str)
    """
    # 1. Concrete deck volume — m³
    c_raw = inputs.get("concrete_deck_vol_total")
    conc_vol: Optional[float] = None
    conc_str = "N.A."
    if c_raw is not None and str(c_raw).strip() not in ("", "N.A.", "None"):
        try:
            conc_vol = float(c_raw)
            conc_str = f"{conc_vol:.2f} m³"
        except (TypeError, ValueError):
            pass

    # 2. Reinforcement steel weight — MT
    r_raw = inputs.get("rebar_deck_wt_total")
    rebar_wt: Optional[float] = None
    rebar_str = "N.A."
    if r_raw is not None and str(r_raw).strip() not in ("", "N.A.", "None"):
        try:
            rebar_wt = float(r_raw)
            rebar_str = f"{rebar_wt:.2f} MT"
        except (TypeError, ValueError):
            pass

    return conc_vol, conc_str, rebar_wt, rebar_str


def create_structural_steel_chart(
    categories: List[str],
    values: List[Optional[float]],
    display_strings: List[str],
    output_path: str,
    figsize: Tuple[float, float] = (6.5, 3.2),
    dpi: int = CHART_DPI,
) -> str:
    """
    Generate Chart 7.1 — Structural Steel Quantity Distribution.

    Displays Steel Girders, Cross Bracing, and End Diaphragms with units in MT.
    """
    if not HAS_MATPLOTLIB:
        return _create_fallback_png(output_path)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    bar_colors = [
        CHART_COLOR_PRIMARY,    # Steel Girders (Osdag Green)
        CHART_COLOR_SECONDARY,  # Cross Bracing (Steel Navy)
        CHART_COLOR_INFO if values[2] is not None else "#BDC3C7",  # End Diaphragms
    ]

    x_indices = list(range(len(categories)))
    plot_values = [v if v is not None else 0.0 for v in values]

    bars = ax.bar(
        x_indices,
        plot_values,
        color=bar_colors,
        width=0.48,
        edgecolor="#333333",
        linewidth=0.75,
        zorder=3,
    )

    # Determine maximum height for proper headroom
    max_val = max([v for v in values if v is not None], default=10.0)
    y_top = max(10.0, max_val * 1.25)
    ax.set_ylim(0.0, y_top)

    # Value annotations above each bar
    for bar, val, d_str in zip(bars, values, display_strings):
        if val is not None and val > 0:
            height = bar.get_height()
            ax.annotate(
                d_str,
                xy=(bar.get_x() + bar.get_width() / 2.0, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=CHART_TICK_FONTSIZE + 1,
                fontweight="bold",
                color="#222222",
            )
        else:
            # Unavailable / N.A. indication clearly shown without a fabricated bar
            ax.annotate(
                d_str,
                xy=(bar.get_x() + bar.get_width() / 2.0, y_top * 0.08),
                xytext=(0, 0),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=CHART_TICK_FONTSIZE,
                fontstyle="italic",
                fontweight="bold",
                color="#7F8C8D",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#F5F5F5", edgecolor="#CCCCCC", alpha=0.9),
            )

    ax.set_ylabel("Weight (MT)", fontsize=CHART_LABEL_FONTSIZE, fontweight="bold", labelpad=8)
    ax.set_title("Structural Steel Quantity Distribution", fontsize=CHART_TITLE_FONTSIZE, fontweight="bold", pad=12)

    ax.set_xticks(x_indices)
    ax.set_xticklabels(categories, fontsize=CHART_TICK_FONTSIZE + 1, fontweight="bold")
    ax.tick_params(axis="y", labelsize=CHART_TICK_FONTSIZE)

    ax.grid(axis="y", linestyle="--", alpha=0.5, color=CHART_COLOR_GRID, zorder=1)
    ax.set_axisbelow(True)

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    return output_path.replace("\\", "/")


def create_concrete_rebar_chart(
    conc_vol: Optional[float],
    conc_str: str,
    rebar_wt: Optional[float],
    rebar_str: str,
    output_path: str,
    figsize: Tuple[float, float] = (6.5, 3.2),
    dpi: int = CHART_DPI,
) -> str:
    """
    Generate Chart 7.2 — Concrete and Reinforcement Material Quantities.

    Two-panel figure with distinct scales and explicit units (m³ vs MT).
    """
    if not HAS_MATPLOTLIB:
        return _create_fallback_png(output_path)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, dpi=dpi)

    # -------------------------------------------------------------------------
    # Panel 1 (Left): Concrete Deck Volume (m³)
    # -------------------------------------------------------------------------
    c_val = conc_vol if conc_vol is not None else 0.0
    c_top = max(10.0, c_val * 1.25)
    ax1.set_ylim(0.0, c_top)

    bar1 = ax1.bar(["Concrete Deck"], [c_val], color=CHART_COLOR_SECONDARY, width=0.45, edgecolor="#333333", linewidth=0.75, zorder=3)
    if conc_vol is not None and conc_vol > 0:
        ax1.annotate(
            conc_str,
            xy=(bar1[0].get_x() + bar1[0].get_width() / 2.0, c_val),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=CHART_TICK_FONTSIZE + 1,
            fontweight="bold",
            color="#222222",
        )
    else:
        ax1.annotate(
            conc_str,
            xy=(bar1[0].get_x() + bar1[0].get_width() / 2.0, c_top * 0.15),
            ha="center",
            va="bottom",
            fontsize=CHART_TICK_FONTSIZE,
            fontstyle="italic",
            fontweight="bold",
            color="#7F8C8D",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#F5F5F5", edgecolor="#CCCCCC", alpha=0.9),
        )

    ax1.set_ylabel("Volume (m³)", fontsize=CHART_LABEL_FONTSIZE, fontweight="bold", labelpad=6)
    ax1.set_title("Concrete Deck Volume", fontsize=CHART_LABEL_FONTSIZE + 1, fontweight="bold", pad=8)
    ax1.tick_params(axis="x", labelsize=CHART_TICK_FONTSIZE, labelrotation=0)
    ax1.tick_params(axis="y", labelsize=CHART_TICK_FONTSIZE)
    ax1.grid(axis="y", linestyle="--", alpha=0.5, color=CHART_COLOR_GRID, zorder=1)
    ax1.set_axisbelow(True)

    # -------------------------------------------------------------------------
    # Panel 2 (Right): Reinforcement Steel Weight (MT)
    # -------------------------------------------------------------------------
    r_val = rebar_wt if rebar_wt is not None else 0.0
    r_top = max(5.0, r_val * 1.25)
    ax2.set_ylim(0.0, r_top)

    bar2 = ax2.bar(["Deck Rebar"], [r_val], color=CHART_COLOR_PRIMARY, width=0.45, edgecolor="#333333", linewidth=0.75, zorder=3)
    if rebar_wt is not None and rebar_wt > 0:
        ax2.annotate(
            rebar_str,
            xy=(bar2[0].get_x() + bar2[0].get_width() / 2.0, r_val),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=CHART_TICK_FONTSIZE + 1,
            fontweight="bold",
            color="#222222",
        )
    else:
        ax2.annotate(
            rebar_str,
            xy=(bar2[0].get_x() + bar2[0].get_width() / 2.0, r_top * 0.15),
            ha="center",
            va="bottom",
            fontsize=CHART_TICK_FONTSIZE,
            fontstyle="italic",
            fontweight="bold",
            color="#7F8C8D",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#F5F5F5", edgecolor="#CCCCCC", alpha=0.9),
        )

    ax2.set_ylabel("Weight (MT)", fontsize=CHART_LABEL_FONTSIZE, fontweight="bold", labelpad=6)
    ax2.set_title("Reinforcement Steel Weight", fontsize=CHART_LABEL_FONTSIZE + 1, fontweight="bold", pad=8)
    ax2.tick_params(axis="x", labelsize=CHART_TICK_FONTSIZE, labelrotation=0)
    ax2.tick_params(axis="y", labelsize=CHART_TICK_FONTSIZE)
    ax2.grid(axis="y", linestyle="--", alpha=0.5, color=CHART_COLOR_GRID, zorder=1)
    ax2.set_axisbelow(True)

    fig.suptitle("Concrete and Reinforcement Material Quantities", fontsize=CHART_TITLE_FONTSIZE, fontweight="bold", y=1.03)

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    return output_path.replace("\\", "/")


def generate_ch7_material_charts(inputs: dict, output_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Generate both Chapter 7 material quantity charts and return their file paths.

    Charts created:
    1. 'mat_steel': Structural Steel Quantity Distribution (MT)
    2. 'mat_concrete_rebar': Concrete and Reinforcement Material Quantities (m³ and MT)

    Parameters
    ----------
    inputs : dict
        Inputs dictionary containing calculated quantities from calculate_material_quantities().
    output_dir : Optional[str]
        Directory where chart PNG images should be saved.

    Returns
    -------
    Dict[str, str] : Mapping from chart identifier to image file path.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="osdag_ch7_charts_")

    os.makedirs(output_dir, exist_ok=True)
    fig_paths: Dict[str, str] = {}

    # Chart 7.1: Structural Steel Quantity Distribution
    p1 = os.path.join(output_dir, "structural_steel_quantities.png")
    cats, vals, d_strs = extract_structural_steel_data(inputs)
    create_structural_steel_chart(cats, vals, d_strs, p1)
    fig_paths["mat_steel"] = p1.replace("\\", "/")

    # Chart 7.2: Concrete and Reinforcement Material Quantities
    p2 = os.path.join(output_dir, "concrete_rebar_quantities.png")
    c_vol, c_str, r_wt, r_str = extract_concrete_rebar_data(inputs)
    create_concrete_rebar_chart(c_vol, c_str, r_wt, r_str, p2)
    fig_paths["mat_concrete_rebar"] = p2.replace("\\", "/")

    return fig_paths

