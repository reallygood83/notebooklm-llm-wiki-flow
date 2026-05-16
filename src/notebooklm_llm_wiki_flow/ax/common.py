"""AURA Administrative (AX) Common Utilities.

Provides OCF-compliant ZIP handling, structured logging, and XML utilities.
"""

from __future__ import annotations

import logging
import os
import sys
import time
import zipfile
from contextlib import contextmanager
from typing import Dict, Iterator, Optional, Union

MIMETYPE = "application/hwp+zip"
RootEntries = Dict[str, Union[bytes, str]]

def get_logger(scope: str) -> logging.Logger:
    """Standardized logger for AX tools."""
    logger = logging.getLogger(f"aura.{scope}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        fmt = logging.Formatter(f"[{scope}][%(levelname)s] %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger

@contextmanager
def step(logger: logging.Logger, name: str) -> Iterator[None]:
    """Execution step context with timing and error reporting."""
    logger.info(f"[{name}] Starting")
    t0 = time.perf_counter()
    try:
        yield
    except Exception as exc:
        dt = (time.perf_counter() - t0) * 1000
        logger.error(f"[{name}] Failed ({dt:.1f}ms): {exc.__class__.__name__}: {exc}")
        raise
    else:
        dt = (time.perf_counter() - t0) * 1000
        logger.info(f"[{name}] Completed ({dt:.1f}ms)")

def escape_xml_text(s: str) -> str:
    """Escape text for XML body content."""
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def escape_xml_attr(s: str) -> str:
    """Escape text for XML attributes."""
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

def write_hwpx_from_entries(entries: RootEntries, output_path: str) -> str:
    """Package memory entries into an OCF-compliant HWPX file."""
    def _to_bytes(v: Union[bytes, str]) -> bytes:
        return v if isinstance(v, bytes) else v.encode("utf-8")

    with zipfile.ZipFile(output_path, "w", allowZip64=False) as z:
        # 1) mimetype FIRST, STORED, no extra field
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        info.external_attr = 0o644 << 16
        z.writestr(info, _to_bytes(entries.get("mimetype", MIMETYPE)))

        # 2) Others - Deterministic order, DEFLATE
        for name in sorted(k for k in entries.keys() if k != "mimetype"):
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, _to_bytes(entries[name]))
    return output_path

def read_hwpx(src_path: str) -> Dict[str, bytes]:
    """Read HWPX into a path->bytes map."""
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"HWPX file not found: {src_path}")
    out: Dict[str, bytes] = {}
    with zipfile.ZipFile(src_path, "r") as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            with z.open(info, "r") as fp:
                out[info.filename] = fp.read()
    return out
