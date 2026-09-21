"""Portable launcher that runs the bundled Streamlit app."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from streamlit.web import cli as stcli


def _configure_frozen_streamlit_assets(bundle_dir: Path) -> None:
    """Make Streamlit's bundled frontend available from a PyInstaller build.

    Streamlit's health endpoint can work even when the frontend bundle is
    missing or the server module has already imported a reference to the
    original static-directory helper.  Patch the helper before Streamlit's
    server is started and validate the actual frontend entry point.
    """
    if not getattr(sys, "frozen", False):
        return

    static_dir = bundle_dir / "streamlit" / "static"
    index_file = static_dir / "index.html"
    if not index_file.is_file():
        raise RuntimeError(
            "Bundled Streamlit frontend is missing: "
            f"{index_file}"
        )

    from streamlit import file_util

    def _bundled_static_dir() -> str:
        return str(static_dir)

    # Streamlit uses file_util.get_static_dir() for its frontend root.
    file_util.get_static_dir = _bundled_static_dir

    # Some Streamlit versions import the helper into the Starlette static
    # routes module. Patch that alias too when it exists. This is deliberately
    # version-tolerant so the launcher works across the pinned Streamlit build.
    for module_name in (
        "streamlit.web.server.starlette.starlette_static_routes",
        "streamlit.web.server.starlette.starlette_routes",
        "streamlit.web.server.server",
    ):
        try:
            module = __import__(module_name, fromlist=["*"])
            if hasattr(module, "get_static_dir"):
                module.get_static_dir = _bundled_static_dir
            if hasattr(module, "STATIC_DIR"):
                module.STATIC_DIR = str(static_dir)
        except Exception:
            # Not every Streamlit version exposes these names.
            pass


def main() -> None:
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    app_file = bundle_dir / "main.py"
    browser_dir = bundle_dir / "playwright-browsers"
    if not app_file.is_file():
        raise RuntimeError(f"Bundled application file was not found: {app_file}")
    if browser_dir.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(browser_dir))
    _configure_frozen_streamlit_assets(bundle_dir)
    sys.argv = [
        "streamlit", "run", str(app_file),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
