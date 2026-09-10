@echo off
chcp 65001 >nul
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 "%~dp0server.py" --refresh-only
) else (
  python "%~dp0server.py" --refresh-only
)
