@echo off
chcp 65001 >nul
title Skill Radar
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 "%~dp0server.py"
) else (
  python "%~dp0server.py"
)
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo 启动失败：请确认已安装 Python 3。
  pause
)
