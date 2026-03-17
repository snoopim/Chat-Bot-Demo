# flows/reactflow_render.py
"""
Render a ReactFlow HTML diagram to PNG using Selenium (headless Chrome).

Mirrors the interface of drawio_render.py:
    render_reactflow_png(html_str, out_dir, name) -> ReactFlowRenderResult
"""
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ReactFlowRenderResult:
    ok: bool
    png_path: Optional[Path] = None
    html_path: Optional[Path] = None
    error: Optional[str] = None


def render_reactflow_png(
    html_content: str,
    out_dir: Path,
    name: str,
    wait_seconds: float = 3.0,
    window_width: int = 1400,
    window_height: int = 1000,
) -> ReactFlowRenderResult:
    """
    Write HTML to disk, open in headless Chrome via Selenium, screenshot to PNG.

    Selenium 4's built-in selenium-manager automatically downloads the
    correct chromedriver for the installed Chrome version — no need to
    manually install or match chromedriver.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = out_dir / f"{name}.html"
    png_path = out_dir / f"{name}.png"

    # Write HTML
    html_path.write_text(html_content, encoding="utf-8")

    # Check Selenium is available
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        return ReactFlowRenderResult(
            ok=False,
            html_path=html_path,
            error=(
                "selenium is not installed.\n"
                "Install it with: pip install selenium\n"
            ),
        )

    driver = None
    # Temporarily hide any stale chromedriver from PATH so Selenium's
    # built-in selenium-manager downloads the correct version.
    orig_path = os.environ.get("PATH", "")
    clean_path = os.pathsep.join(
        p for p in orig_path.split(os.pathsep)
        if not (os.path.isfile(os.path.join(p, "chromedriver")))
    )
    os.environ["PATH"] = clean_path
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--force-device-scale-factor=2")
        options.add_argument(f"--window-size={window_width},{window_height}")

        # Let Selenium 4 auto-manage chromedriver via selenium-manager.
        driver = webdriver.Chrome(options=options)

        # Navigate to the local HTML file
        file_url = f"file://{html_path.resolve()}"
        driver.get(file_url)

        # Wait for render signal
        for _ in range(int(wait_seconds * 2) + 10):
            try:
                rendered = driver.execute_script("return window.__REACTFLOW_RENDERED__ === true")
                if rendered:
                    break
            except Exception:
                pass
            time.sleep(0.5)

        time.sleep(0.5)

        # Resize window to fit the full SVG (with padding to avoid clipping)
        try:
            dimensions = driver.execute_script("""
                const svg = document.querySelector('svg');
                if (svg) {
                    return {
                        width: Math.ceil(parseFloat(svg.getAttribute('width')) || 800),
                        height: Math.ceil(parseFloat(svg.getAttribute('height')) || 600)
                    };
                }
                return { width: 800, height: 600 };
            """)
            # Add extra space so Chrome doesn't clip the bottom
            content_w = dimensions.get("width", 800) + 40
            content_h = dimensions.get("height", 600) + 100
            driver.set_window_size(content_w, content_h)
            time.sleep(0.3)
        except Exception:
            pass

        # Screenshot the SVG element directly for tight cropping
        try:
            svg_el = driver.find_element("tag name", "svg")
            svg_el.screenshot(str(png_path))
        except Exception:
            driver.save_screenshot(str(png_path))

        if not png_path.exists() or png_path.stat().st_size == 0:
            return ReactFlowRenderResult(
                ok=False,
                html_path=html_path,
                error="Screenshot was taken but PNG file is empty or missing.",
            )

        return ReactFlowRenderResult(
            ok=True,
            png_path=png_path,
            html_path=html_path,
        )

    except Exception as e:
        return ReactFlowRenderResult(
            ok=False,
            html_path=html_path,
            error=f"Selenium error: {type(e).__name__}: {str(e)}",
        )
    finally:
        os.environ["PATH"] = orig_path
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
