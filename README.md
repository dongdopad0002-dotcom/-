# 정소윤 AI

## Windows에서 바로 실행할 수 있는 EXE

`main.py`, Python 의존성, Playwright Chromium을 `JeongSoyoonAI.exe`에 함께
포함합니다. 실행할 Windows PC에는 Python이나 Playwright 설치가 필요 없습니다.

GitHub **Actions**의 **Build Windows portable EXE**가 완료되면
`JeongSoyoonAI-Windows` 아티팩트를 내려받아 압축을 푼 뒤,
`JeongSoyoonAI/JeongSoyoonAI.exe`를 실행하세요. EXE 옆의 파일들은 함께 둬야 합니다.

직접 빌드하려면 Windows PowerShell에서 다음을 실행합니다.

```powershell
./scripts/build_windows_portable.ps1
```

생성 폴더는 `dist/JeongSoyoonAI`이며, 실행 데이터는
`%LOCALAPPDATA%\JeongSoyoonAI`에 저장됩니다.
