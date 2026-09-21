# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe for the self-contained Windows distribution."""
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, get_module_file_attribute

ROOT = Path(SPECPATH)
datas = [(str(ROOT / "main.py"), ".")]
binaries, hiddenimports = [], []

for package in (
    "streamlit", "playwright", "langchain", "langchain_community",
    "langchain_core", "langchain_experimental", "langchain_openai",
    "langchain_chroma", "langgraph", "chromadb", "faiss",
    "mypy_extensions",
):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

# Streamlit's frontend must be present at the exact path expected by the
# frozen launcher.  collect_all() is kept for the rest of the package, but
# this explicit entry prevents the frontend tree from being lost/relocated.
streamlit_package_dir = Path(get_module_file_attribute("streamlit")).parent
streamlit_static_dir = streamlit_package_dir / "static"
streamlit_index = streamlit_static_dir / "index.html"
if not streamlit_index.is_file():
    raise SystemExit(f"Streamlit UI assets were not found: {streamlit_index}")

datas.append((str(streamlit_static_dir), "streamlit/static"))

browser_dir = ROOT / "playwright-browsers"
if not browser_dir.is_dir():
    raise SystemExit("Missing playwright-browsers; run playwright install chromium first.")
datas.append((str(browser_dir), "playwright-browsers"))

a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    noarchive=False,
)
pyz = PYZ(a.pure)

# IMPORTANT: keep a console for the portable build.  A windowless EXE hides
# the real import/DLL exception when Streamlit fails before opening port 8501,
# making CI report only "connection refused".  A console does not change how
# Streamlit serves the app and makes failures diagnosable.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="JeongSoyoonAI",
    console=True,
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="JeongSoyoonAI",
)
