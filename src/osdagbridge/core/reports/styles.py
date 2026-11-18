"""
OsdagBridge Report Styling Configuration
========================================

Centralized styling configurations and visual constants for OsdagBridge design reports.
Standardizes:
- Page geometry, margins, and paper sizes (with explicit headheight, headsep, footskip)
- Typography, font sizing, and line spacing
- Header and footer rules, text, and vertical spacing (no negative spacing hacks)
- Heading hierarchy (chapters, sections, subsections, TOC)
- Table formatting (padding, row height, borders, longtable skips)
- Brand colors (Osdag Green #91B014)
- Reusable chart colors and visual styling constants for future chart implementation
"""

from typing import List, Tuple

# =============================================================================
# 1. PAGE SETUP & GEOMETRY
# =============================================================================
DOCUMENT_CLASS: str = "report"
DOCUMENT_FONT_SIZE: str = "12pt"
PAGE_SIZE: str = "a4paper"

# Explicit margins ensuring balanced layout and adequate vertical clearance
MARGIN_TOP: str = "1.0in"
MARGIN_BOTTOM: str = "1.25in"     # 31.75 mm (~90 pt): reserves ample space for footer
MARGIN_LEFT: str = "1.0in"
MARGIN_RIGHT: str = "1.0in"
PAGE_MARGIN: str = "1.0in"        # Compatibility alias

# Header and footer vertical geometry parameters (resolves fancyhdr warnings & overlap)
HEAD_HEIGHT: str = "20pt"         # Sufficient vertical space for 2-line header
HEAD_SEP: str = "12pt"            # Separation between header rule and start of text body
FOOT_SKIP: str = "30pt"           # Distance from bottom of text area to footer text baseline


# =============================================================================
# 2. BRAND & REPORT COLORS
# =============================================================================
# Primary Osdag brand color
COLOR_OSDAG_GREEN: str = "#91B014"
COLOR_OSDAG_GREEN_HEX: str = "91B014"
COLOR_NAME_OSDAG_GREEN: str = "osdagGreen"

# Report element colors
COLOR_PRIMARY: str = "#91B014"
COLOR_SECONDARY: str = "#1F4E79"
COLOR_TEXT_MAIN: str = "#000000"
COLOR_TEXT_MUTED: str = "#555555"
COLOR_BORDER: str = "#D0D0D0"


# =============================================================================
# 3. CHART & VISUALIZATION PALETTE (for future chart implementations)
# =============================================================================
CHART_COLOR_PRIMARY: str = "#91B014"     # Osdag Green
CHART_COLOR_SECONDARY: str = "#1F4E79"   # Steel / Navy Blue
CHART_COLOR_ACCENT: str = "#D9534F"      # Crimson / Red
CHART_COLOR_SUCCESS: str = "#27AE60"     # Green (Safe / Pass)
CHART_COLOR_WARNING: str = "#F39C12"     # Amber (Warning / Limit)
CHART_COLOR_DANGER: str = "#C0392B"      # Dark Red (Failure)
CHART_COLOR_INFO: str = "#2980B9"        # Blue (Info / BM)
CHART_COLOR_GRID: str = "#E0E0E0"        # Grid lines

# Specific structural response curve colors
CHART_COLOR_BM: str = "#2980B9"          # Bending moment
CHART_COLOR_SF: str = "#E67E22"          # Shear force
CHART_COLOR_DEFL: str = "#27AE60"        # Deflection
CHART_COLOR_STRESS: str = "#8E44AD"      # Stress distribution

# Reusable chart color palette
CHART_PALETTE: List[str] = [
    "#91B014",  # Osdag Green
    "#1F4E79",  # Steel Navy
    "#2980B9",  # Sky Blue
    "#E67E22",  # Orange
    "#27AE60",  # Emerald
    "#8E44AD",  # Purple
    "#D9534F",  # Coral / Red
    "#16A085",  # Teal
]

# Chart visual styling constants
CHART_DPI: int = 300
CHART_FIGURE_WIDTH: float = 6.5
CHART_FIGURE_HEIGHT: float = 4.0
CHART_FIGSIZE_DEFAULT: Tuple[float, float] = (6.5, 4.0)
CHART_FIGSIZE_WIDE: Tuple[float, float] = (7.5, 3.5)
CHART_LINE_WIDTH: float = 1.5
CHART_GRID_ALPHA: float = 0.5
CHART_GRID_STYLE: str = "--"
CHART_FONT_FAMILY: str = "sans-serif"
CHART_TITLE_FONTSIZE: int = 12
CHART_LABEL_FONTSIZE: int = 10
CHART_TICK_FONTSIZE: int = 8
CHART_LEGEND_FONTSIZE: int = 9


# =============================================================================
# 4. FONT & TYPOGRAPHY SETTINGS
# =============================================================================
FONT_SIZE_BASE: str = "12pt"
LINE_SPACING: float = 1.15
LINE_STRETCH: float = 1.15

# Caption settings
CAPTION_LABEL_FONT: str = "bf"
CAPTION_JUSTIFICATION: str = "raggedright"
CAPTION_SINGLE_LINE_CHECK: str = "false"
CAPTION_FORMAT: str = "plain"


# =============================================================================
# 5. CHAPTER & SECTION HEADING FORMATTING (titlesec / titletoc)
# =============================================================================
CHAPTER_TITLE_FORMAT: str = (
    r"\titleformat{\chapter}[block]"
    r"{\normalfont\Large\bfseries\centering}{\thechapter}{1em}{}"
)
CHAPTER_TITLE_SPACING: str = r"\titlespacing*{\chapter}{0pt}{0pt}{10pt}"

SECTION_TITLE_FORMAT: str = (
    r"\titleformat{\section}[hang]"
    r"{\normalfont\large\bfseries}{\thesection}{1em}{}"
)
SECTION_TITLE_SPACING: str = (
    r"\titlespacing*{\section}{0pt}{12pt plus 4pt minus 2pt}{6pt plus 2pt minus 2pt}"
)

SUBSECTION_TITLE_FORMAT: str = (
    r"\titleformat{\subsection}[hang]"
    r"{\normalfont\normalsize\bfseries}{\thesubsection}{1em}{}"
)
SUBSECTION_TITLE_SPACING: str = (
    r"\titlespacing*{\subsection}{0pt}{10pt plus 3pt minus 2pt}{4pt plus 2pt minus 2pt}"
)

# Table of Contents depth and titles
TOC_DEPTH: int = 2
TOC_TITLE: str = r"\centering\Large\bfseries Table of Contents"

TOC_CHAPTER_FORMAT: str = r"""\titlecontents{chapter}[1.5em]
  {\normalfont\vspace{2pt}}
  {\contentslabel{1.5em}}
  {\hspace*{-1.5em}}
  {\hfill\contentspage}"""

TOC_SECTION_FORMAT: str = r"""\titlecontents{section}[3.8em]
  {\normalfont}
  {\contentslabel{2.3em}}
  {\hspace*{-2.3em}}
  {\hfill\contentspage}"""

TOC_SUBSECTION_FORMAT: str = r"""\titlecontents{subsection}[7.0em]
  {\normalfont}
  {\contentslabel{3.2em}}
  {\hspace*{-3.2em}}
  {\hfill\contentspage}"""


# =============================================================================
# 6. TABLE SPACING, PADDING & BORDER THICKNESS
# =============================================================================
# Column padding
TABLE_COL_SEP: str = "6pt"

# Row height stretch & extra height
TABLE_ARRAY_STRETCH: float = 1.12
TABLE_EXTRA_ROW_HEIGHT: str = "0.6pt"

# Table rules & border thickness
TABLE_BORDER_THICKNESS: str = "0.5pt"
TABLE_RULE_WIDTH: str = "0.5pt"

# Longtable pre- and post-spacing
LONGTABLE_PRE_SKIP: str = "0pt"
LONGTABLE_POST_SKIP: str = "6pt"
LONGTABLE_ALIGN_LEFT: str = r"\fill"
LONGTABLE_ALIGN_RIGHT: str = r"\fill"

# Page-break overflow prevention (guarantees space before beginning a table)
TABLE_NEEDSPACE: str = r"6\baselineskip"


# =============================================================================
# 7. HEADER & FOOTER CONFIGURATION & SPACING
# =============================================================================
# Fixed text content
FOOTER_LEFT_TEXT: str = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
FOOTER_PAGE_FORMAT: str = r"Page \thepage\ of \pageref{LastPage}"
FOOTER_SD_NOTE_TEXT: str = r"* Software default value"

# Rule thickness and vertical spacing
HEADER_RULE_HEIGHT: str = "1pt"
HEADER_RULE_VSPACE: str = "2pt"
FOOTER_RULE_HEIGHT: str = "1pt"
FOOTER_RULE_VSPACE_BOTTOM: str = "4pt"   # Clean separation between rule and footer text (no text overlap)
FOOTER_SD_VSPACE_MID: str = "2pt"        # Clean separation between SD footnote note and green rule

# Deprecated spacing constants preserved for backward compatibility
FOOTER_SD_VSPACE_TOP: str = "0pt"
FOOTER_NORMAL_VSPACE: str = "0pt"
FOOTER_FIRSTPAGE_VSPACE: str = "0pt"


# =============================================================================
# 8. REUSABLE LATEX GENERATION HELPERS
# =============================================================================
def get_geometry_setup_latex() -> str:
    """Return LaTeX geometry package configuration with explicit header/footer spaces."""
    return (
        f"\\usepackage[{PAGE_SIZE}, "
        f"top={MARGIN_TOP}, "
        f"bottom={MARGIN_BOTTOM}, "
        f"left={MARGIN_LEFT}, "
        f"right={MARGIN_RIGHT}, "
        f"headheight={HEAD_HEIGHT}, "
        f"headsep={HEAD_SEP}, "
        f"footskip={FOOT_SKIP}]{{geometry}}"
    )


def get_color_definitions_latex() -> str:
    """Return LaTeX color definition commands."""
    return f"\\definecolor{{{COLOR_NAME_OSDAG_GREEN}}}{{HTML}}{{{COLOR_OSDAG_GREEN_HEX}}}"


def get_caption_setup_latex() -> str:
    """Return LaTeX caption setup block."""
    return (
        f"\\captionsetup{{\n"
        f"    labelfont={CAPTION_LABEL_FONT},\n"
        f"    justification={CAPTION_JUSTIFICATION},\n"
        f"    singlelinecheck={CAPTION_SINGLE_LINE_CHECK},\n"
        f"    format={CAPTION_FORMAT}\n"
        f"}}"
    )


def get_table_styling_latex() -> str:
    """Return LaTeX table formatting and spacing commands."""
    return (
        f"% Table layout and spacing: consistent padding, row height, and longtable pre/post skips\n"
        f"\\setlength{{\\tabcolsep}}{{{TABLE_COL_SEP}}}\n"
        f"\\renewcommand{{\\arraystretch}}{{{TABLE_ARRAY_STRETCH}}}\n"
        f"\\setlength{{\\LTpre}}{{{LONGTABLE_PRE_SKIP}}}\n"
        f"\\setlength{{\\LTpost}}{{{LONGTABLE_POST_SKIP}}}\n"
        f"% Table rules (outline thickness) and small extra row height for clarity\n"
        f"\\setlength{{\\arrayrulewidth}}{{{TABLE_BORDER_THICKNESS}}}\n"
        f"\\setlength{{\\extrarowheight}}{{{TABLE_EXTRA_ROW_HEIGHT}}}\n\n"
        f"% Prevent tables from overflowing past the page bottom:\n"
        f"% if fewer than 6 baseline-skips remain, break to the next page first.\n"
        f"\\BeforeBeginEnvironment{{table}}{{\\needspace{{{TABLE_NEEDSPACE}}}}}\n"
        f"\\BeforeBeginEnvironment{{longtable}}{{\\needspace{{{TABLE_NEEDSPACE}}}}}"
    )


def get_header_footer_latex(
    project_name_tex: str,
    job_number_tex: str,
    report_date_tex: str,
    report_version_tex: str,
) -> str:
    """
    Generate LaTeX fancyhdr pagestyle definitions for main, plain, and firstpage.

    Preserves dynamic project metadata, ensures consistent footer positioning,
    and eliminates negative vertical spacing hacks that cause content overlap.
    """
    return f"""\\fancypagestyle{{main}}{{
  \\fancyhf{{}}
  \\fancyhead[L]{{{project_name_tex} $|$ {job_number_tex}}}
  \\fancyhead[R]{{{report_date_tex} $|$ {report_version_tex}}}
  \\fancyfoot[L]{{{FOOTER_LEFT_TEXT}}}
  \\fancyfoot[R]{{{FOOTER_PAGE_FORMAT}}}
  \\renewcommand{{\\headrule}}{{\\color{{{COLOR_NAME_OSDAG_GREEN}}}\\hrule width\\headwidth height {HEADER_RULE_HEIGHT} \\vspace{{{HEADER_RULE_VSPACE}}}}}
  \\renewcommand{{\\footrule}}{{%
    \\ifbool{{hasSDonPage}}{{%
      \\hbox to \\headwidth{{\\textcolor{{black}}{{\\footnotesize\\textit{{{FOOTER_SD_NOTE_TEXT}}}}}\\hfil}}%
      \\vspace{{{FOOTER_SD_VSPACE_MID}}}%
    }}{{}}%
    \\color{{{COLOR_NAME_OSDAG_GREEN}}}\\hrule width\\headwidth height {FOOTER_RULE_HEIGHT} \\vspace{{{FOOTER_RULE_VSPACE_BOTTOM}}}%
  }}
}}
\\fancypagestyle{{plain}}{{
  \\fancyhf{{}}
  \\fancyhead[L]{{{project_name_tex} $|$ {job_number_tex}}}
  \\fancyhead[R]{{{report_date_tex} $|$ {report_version_tex}}}
  \\fancyfoot[L]{{{FOOTER_LEFT_TEXT}}}
  \\fancyfoot[R]{{{FOOTER_PAGE_FORMAT}}}
  \\renewcommand{{\\headrule}}{{\\color{{{COLOR_NAME_OSDAG_GREEN}}}\\hrule width\\headwidth height {HEADER_RULE_HEIGHT} \\vspace{{{HEADER_RULE_VSPACE}}}}}
  \\renewcommand{{\\footrule}}{{%
    \\ifbool{{hasSDonPage}}{{%
      \\hbox to \\headwidth{{\\textcolor{{black}}{{\\footnotesize\\textit{{{FOOTER_SD_NOTE_TEXT}}}}}\\hfil}}%
      \\vspace{{{FOOTER_SD_VSPACE_MID}}}%
    }}{{}}%
    \\color{{{COLOR_NAME_OSDAG_GREEN}}}\\hrule width\\headwidth height {FOOTER_RULE_HEIGHT} \\vspace{{{FOOTER_RULE_VSPACE_BOTTOM}}}%
  }}
}}
\\fancypagestyle{{firstpage}}{{
  \\fancyhf{{}}
  \\renewcommand{{\\headrulewidth}}{{0pt}}
  \\fancyfoot[L]{{{FOOTER_LEFT_TEXT}}}
  \\fancyfoot[R]{{{FOOTER_PAGE_FORMAT}}}
  \\renewcommand{{\\footrule}}{{\\color{{{COLOR_NAME_OSDAG_GREEN}}}\\hrule width\\headwidth height {FOOTER_RULE_HEIGHT} \\vspace{{{FOOTER_RULE_VSPACE_BOTTOM}}}}}
}}"""
