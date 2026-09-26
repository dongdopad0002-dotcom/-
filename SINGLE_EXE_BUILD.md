# Single-EXE Windows build

`windows_onefile.spec` is the single-file version of the existing PyInstaller
configuration.

It keeps the existing:
- Streamlit application and UI
- LangChain/LangGraph/LangChain tools
- Chroma / FAISS
- Playwright and bundled Chromium
- Streamlit static frontend patch
- local writable data directory
- fixed `127.0.0.1:8501` server settings
- console/log diagnostics
- existing `requirements.txt`

The important difference is that the spec does **not** call `COLLECT()`.
Everything needed at runtime is embedded in `dist\JeongSoyoonAI.exe`.

Build on Windows:

```bat
build_onefile.bat
```

The resulting file is:

```text
dist\JeongSoyoonAI.exe
```

Because Chromium and the Python runtime are embedded, the EXE can be large.
PyInstaller extracts its internal contents to a temporary directory when it
starts; that is normal for `--onefile`.

The app's writable runtime data still goes to:

```text
%LOCALAPPDATA%\JeongSoyoonAI
```

This is intentional and does not create a second executable/dependency
distribution.
