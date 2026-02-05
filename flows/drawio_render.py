# flows/drawio_render.py
"""
Render draw.io XML diagrams to PNG using draw.io CLI.
"""
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DrawioRenderResult:
    ok: bool
    png_path: Optional[Path] = None
    drawio_path: Optional[Path] = None
    cmd: Optional[list] = None
    error: Optional[str] = None


def _find_drawio_cli() -> Optional[str]:
    """
    Find the draw.io CLI executable.
    Returns path to executable or None if not found.
    """
    # Try common locations
    candidates = [
        # macOS
        "/Applications/draw.io.app/Contents/MacOS/draw.io",
        "/Applications/drawio.app/Contents/MacOS/drawio",
        os.path.expanduser("~/Applications/draw.io.app/Contents/MacOS/draw.io"),
        # Linux
        "/usr/bin/drawio",
        "/usr/local/bin/drawio",
        "/snap/bin/drawio",
        # Windows (via PATH)
        "drawio",
        "draw.io",
    ]

    # First check if it's in PATH
    for name in ["drawio", "draw.io"]:
        path = shutil.which(name)
        if path:
            return path

    # Then check specific locations
    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None


def render_drawio_png(drawio_xml: str, out_dir: Path, name: str) -> DrawioRenderResult:
    """
    Render draw.io XML to PNG using draw.io CLI.
    Returns DrawioRenderResult with real error messages.

    Requirements:
    - draw.io desktop app must be installed
    - macOS: /Applications/draw.io.app
    - Linux: drawio package (apt install drawio or snap install drawio)
    - Windows: draw.io from https://www.drawio.com/

    The CLI command used:
      drawio --export --format png --output <output.png> <input.drawio>
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    drawio_path = out_dir / f"{name}.drawio"
    png_path = out_dir / f"{name}.png"

    # Write the XML to a .drawio file
    drawio_path.write_text(drawio_xml, encoding="utf-8")

    # Find draw.io CLI
    drawio_cli = _find_drawio_cli()

    if not drawio_cli:
        return DrawioRenderResult(
            ok=False,
            png_path=None,
            drawio_path=drawio_path,
            cmd=None,
            error=(
                "draw.io CLI not found.\n\n"
                "Please install draw.io desktop app:\n"
                "  - macOS: Download from https://www.drawio.com/ or brew install --cask drawio\n"
                "  - Linux: sudo snap install drawio or sudo apt install drawio\n"
                "  - Windows: Download from https://www.drawio.com/\n\n"
                "After installation, restart your terminal and Django server.\n"
            ),
        )

    # Build command
    # --export: export mode
    # --format: output format (png, pdf, svg, etc.)
    # --output: output file path
    # --transparent: transparent background (optional)
    # --scale: scale factor (optional, default 1)
    # --border: border padding (optional)
    cmd = [
        drawio_cli,
        "--export",
        "--format", "png",
        "--output", str(png_path),
        "--scale", "2",  # Higher quality
        "--border", "10",
        str(drawio_path),
    ]

    try:
        # Run draw.io export
        # Note: draw.io CLI may need a display on Linux; use xvfb-run if headless
        env = os.environ.copy()

        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            timeout=60,  # 60 second timeout
        )

        if proc.returncode != 0:
            return DrawioRenderResult(
                ok=False,
                png_path=None,
                drawio_path=drawio_path,
                cmd=cmd,
                error=(
                    "draw.io export failed.\n"
                    f"Return code: {proc.returncode}\n\n"
                    "STDOUT:\n"
                    f"{(proc.stdout or '').strip()}\n\n"
                    "STDERR:\n"
                    f"{(proc.stderr or '').strip()}\n"
                ),
            )

        # Check if PNG was created
        if not png_path.exists():
            return DrawioRenderResult(
                ok=False,
                png_path=None,
                drawio_path=drawio_path,
                cmd=cmd,
                error="draw.io ran but PNG file was not created.",
            )

        if png_path.stat().st_size == 0:
            return DrawioRenderResult(
                ok=False,
                png_path=None,
                drawio_path=drawio_path,
                cmd=cmd,
                error="draw.io ran but PNG file is empty.",
            )

        return DrawioRenderResult(
            ok=True,
            png_path=png_path,
            drawio_path=drawio_path,
            cmd=cmd,
            error=None,
        )

    except subprocess.TimeoutExpired:
        return DrawioRenderResult(
            ok=False,
            png_path=None,
            drawio_path=drawio_path,
            cmd=cmd,
            error="draw.io export timed out after 60 seconds.",
        )
    except Exception as e:
        return DrawioRenderResult(
            ok=False,
            png_path=None,
            drawio_path=drawio_path,
            cmd=cmd,
            error=f"Unexpected error: {type(e).__name__}: {str(e)}",
        )
