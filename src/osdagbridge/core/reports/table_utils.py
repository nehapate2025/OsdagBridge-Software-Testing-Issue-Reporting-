"""
OsdagBridge Report Table Utilities
==================================

Reusable helper functions and generators for multi-page LaTeX longtables.
Provides standardized repeated headers, continuation captions, and continuation
footers per the OsdagBridge design report specification.
"""

import re
from typing import Optional


def make_repeated_header(
    header_rows: str,
    ncols: int,
    caption: str = "",
    label: str = "",
    continuation_text: str = "",
) -> str:
    """
    Construct a complete, standard LaTeX longtable header and footer block.

    Features:
    - First page: Caption + primary column headers (ended by \\endfirsthead)
    - Subsequent pages: Clean continuation message + repeated column headers (ended by \\endhead)
    - Intermediate page footer: "Continued on next page" (ended by \\endfoot)
    - Final page footer: Standard horizontal rule \\hline (ended by \\endlastfoot)

    Parameters
    ----------
    header_rows : str
        The LaTeX column header string, e.g.
        r"\\textbf{Col 1} & \\textbf{Col 2} \\\\[6pt]"
    ncols : int
        Exact number of columns in the table (used for \\multicolumn).
    caption : str, optional
        The caption text for the table (e.g. r"\\textbf{Girder Section Dimensions}").
    label : str, optional
        Optional LaTeX \\label identifier.
    continuation_text : str, optional
        Optional custom continuation message. Defaults to
        r"\\tablename\\ \\thetable{} -- Continued from previous page" when caption
        is present, or "Table continued from previous page" otherwise.

    Returns
    -------
    str
        The formatted LaTeX longtable header/footer definition block.
    """
    h_rows = header_rows.strip()
    # Normalize ending: ensure it ends with LaTeX line break if not already present
    if not (h_rows.endswith(r"\\") or re.search(r"\\\\\[[^\]]+\]$", h_rows)):
        h_rows += r" \\"

    if caption:
        lbl_part = f"\\label{{{label}}}" if label else ""
        caption_block = f"\\caption{{{caption}}}{lbl_part} \\\\\n"
        default_cont = r"\small\textit{\tablename\ \thetable{} -- Continued from previous page}"
    else:
        caption_block = ""
        default_cont = r"\small\textit{Table continued from previous page}"

    cont_msg = continuation_text if continuation_text else default_cont

    return (
        f"{caption_block}\\hline\n"
        f"{h_rows}\n"
        f"\\hline\n"
        f"\\endfirsthead\n\n"
        f"\\multicolumn{{{ncols}}}{{c}}{{{{{cont_msg}}}}} \\\\[4pt]\n"
        f"\\hline\n"
        f"{h_rows}\n"
        f"\\hline\n"
        f"\\endhead\n\n"
        f"\\hline\n"
        f"\\multicolumn{{{ncols}}}{{r}}{{\\footnotesize\\textit{{Continued on next page}}}} \\\\\n"
        f"\\endfoot\n\n"
        f"\\hline\n"
        f"\\endlastfoot"
    )
