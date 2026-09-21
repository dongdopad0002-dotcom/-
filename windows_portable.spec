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
):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

# Streamlit serves its UI from this directory.  Keep it explicit as well as
# collect_all: without these HTML/JS assets the health endpoint can be ready
# while the browser receives only a 404/"Not Found" response at `/`.
streamlit_static_dir = Path(get_module_file_attribute("streamlit")).parent / "static"
streamlit_index = streamlit_static_dir / "index.html"
if not streamlit_index.is_file():
    raise SystemExit(f"Streamlit UI assets were not found: {streamlit_index}")

# Do not depend on collect_all() to preserve the frontend tree.  Streamlit's
# root page is served from static/index.html and its JS/CSS live below the
# same directory.
datas.append((str(streamlit_static_dir), "streamlit/static"))

browser_dir = ROOT / "playwright-browsers"
if not browser_dir.is_dir():
    raise SystemExit("Missing playwright-browsers; run playwright install chromium first.")
datas.append((str(browser_dir), "playwright-browsers"))

a = Analysis([str(ROOT / "app.py")], pathex=[str(ROOT)], binaries=binaries,
             datas=datas, hiddenimports=hiddenimports, noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
          name="JeongSoyoonAI", console=False, exclude_binaries=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
               name="JeongSoyoonAI")
