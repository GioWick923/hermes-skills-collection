@echo off
REM Build + install un crate Rust (cdylib pyo3) como .pyd en el venv de Hermes.
REM Compila OFFLINE usando el registry cache local de cargo.
REM Uso: editar NOMBRE y rutas, luego ejecutar.
setlocal
set NOMBRE=fuzzy_norm_rs
set CRATE_DIR=C:\%NOMBRE%

call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
cd /d %CRATE_DIR%
set PATH=%USERPROFILE%\.local\bin;%PATH%

set HERMES_VENV=%LOCALAPPDATA%\hermes\hermes-agent\venv
set PYO3_PYTHON=%HERMES_VENV%\Scripts\python.exe
set PYTHON_SYS_EXECUTABLE=%PYO3_PYTHON%
set CARGO_NET_OFFLINE=true

cargo build --release
if errorlevel 1 (
  echo BUILD_FAILED
  exit /b 1
)

copy /Y target\release\%NOMBRE%.dll target\release\%NOMBRE%.pyd

for /f "delims=" %%i in ('%HERMES_VENV%\Scripts\python.exe -c "import site; print(site.getsitepackages()[0])"') do set SP=%%i
copy /Y target\release\%NOMBRE%.pyd "%SP%\%NOMBRE%.pyd"
echo BUILD_OK -^> %SP%\%NOMBRE%.pyd
endlocal
