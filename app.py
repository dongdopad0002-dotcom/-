"""Portable launcher for the bundled Streamlit application.

This launcher is deliberately defensive because a PyInstaller EXE can fail
before Streamlit opens its port (for example because a bundled import/DLL is
missing).  The previous launcher hid that exception with a windowless EXE,
which made the GitHub smoke test look like a simple connection-refused error.
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _bundle_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def _log_file() -> Path:
    # Always use a writable location.  The GitHub runner also keeps the
    # repository writable, so the local log is useful during the smoke test.
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("TEMP", Path.home()))
    else:
        base = Path(__file__).resolve().parent
    base.mkdir(parents=True, exist_ok=True)
    return base / "JeongSoyoonAI_portable_startup.log"


def _log(message: str) -> None:
    line = f"[{__import__('datetime').datetime.now().isoformat()}] {message}\n"
    try:
        with _log_file().open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    try:
        print(line, flush=True)
    except Exception:
        pass


def _configure_frozen_streamlit_assets(bundle_dir: Path) -> None:
    if not getattr(sys, "frozen", False):
        return

    static_dir = bundle_dir / "streamlit" / "static"
    index_file = static_dir / "index.html"
    if not index_file.is_file():
        raise RuntimeError(f"Bundled Streamlit frontend is missing: {index_file}")

    from streamlit import file_util

    def _bundled_static_dir() -> str:
        return str(static_dir)

    file_util.get_static_dir = _bundled_static_dir

    # Streamlit has changed the module holding the static-route helper across
    # releases. Patch every known alias before the server is started.
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
        except Exception as exc:
            _log(f"Static-route patch skipped for {module_name}: {exc}")


def main() -> None:
    bundle_dir = _bundle_dir()
    app_file = bundle_dir / "main.py"
    browser_dir = bundle_dir / "playwright-browsers"

    _log(f"Launcher starting; frozen={getattr(sys, 'frozen', False)}")
    _log(f"bundle_dir={bundle_dir}")
    _log(f"app_file={app_file} exists={app_file.is_file()}")

    if not app_file.is_file():
        raise RuntimeError(f"Bundled application file was not found: {app_file}")

    if browser_dir.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_dir)
        _log(f"PLAYWRIGHT_BROWSERS_PATH={browser_dir}")

    _configure_frozen_streamlit_assets(bundle_dir)

    # Explicitly select the loopback interface and a fixed port used by the
    # GitHub smoke test.  Disable the file watcher because it is unnecessary
    # in a frozen executable and can cause PyInstaller/runtime path issues.
    # PyInstaller can make Streamlit believe it is running in development mode.
    # In development mode Streamlit refuses explicit server.port settings.
    # Force production mode before invoking the CLI.
    os.environ["STREAMLIT_GLOBAL_DEVELOPMENTMODE"] = "false"

    sys.argv = [
        "streamlit",
        "run",
        "--global.developmentMode=false",
        str(app_file),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
    ]
    _log(f"Launching Streamlit: {sys.argv!r}")

    from streamlit.web import cli as stcli
    return_code = stcli.main()
    _log(f"Streamlit exited with code {return_code!r}")
    if isinstance(return_code, int):
        raise SystemExit(return_code)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        _log(f"FATAL: {type(exc).__name__}: {exc}")
        _log(traceback.format_exc())
        # Keep the console enabled in the CI build so the same traceback is
        # also visible directly in the GitHub Actions log.
        raise
