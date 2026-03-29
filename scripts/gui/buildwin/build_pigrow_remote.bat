@echo off
setlocal

REM Build Pigrow Remote for Windows using PyInstaller.
REM This script is intended to be run from anywhere inside the repo.

set "REPO_ROOT=%~dp0\..\..\.."
for %%I in ("%REPO_ROOT%") do set "REPO_ROOT=%%~fI"

cd /d "%REPO_ROOT%"

set "BUILDWIN_DIR=scripts\gui\buildwin"
set "DIST_DIR=%BUILDWIN_DIR%\dist"
set "WORK_DIR=%BUILDWIN_DIR%\build"
set "SPEC_DIR=%BUILDWIN_DIR%"
set "GUI_DIR=%REPO_ROOT%\scripts\gui"
set "UI_IMAGES_DIR=%GUI_DIR%\ui_images"
set "GRAPH_MODULES_DIR=%GUI_DIR%\graph_modules"
set "SENSOR_MODULES_DIR=%GUI_DIR%\sensor_modules"
set "TIMELAPSE_MODULES_DIR=%GUI_DIR%\timelapse_modules"
set "GRAPH_PRESETS_DIR=%GUI_DIR%\graph_presets"
set "DATAWALL_PRESETS_DIR=%GUI_DIR%\datawall_presets"

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
if not exist "%WORK_DIR%" mkdir "%WORK_DIR%"

py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onedir ^
  --name PigrowRemote ^
  --icon "%UI_IMAGES_DIR%\icon.ico" ^
  --paths "%GUI_DIR%" ^
  --distpath "%DIST_DIR%" ^
  --workpath "%WORK_DIR%" ^
  --specpath "%SPEC_DIR%" ^
  --hidden-import panels.link_pnl ^
  --hidden-import panels.blank_pnl ^
  --hidden-import panels.start_pnl ^
  --hidden-import panels.system_pnl ^
  --hidden-import panels.cron_pnl ^
  --hidden-import panels.camera_pnl ^
  --hidden-import panels.timelapse_pnl ^
  --hidden-import panels.localfiles_pnl ^
  --hidden-import panels.sensors_pnl ^
  --hidden-import panels.power_pnl ^
  --hidden-import panels.watering_pnl ^
  --hidden-import panels.graphs_pnl ^
  --hidden-import panels.datawall_pnl ^
  --hidden-import panels.display_pnl ^
  --hidden-import panels.userlog_pnl ^
  --hidden-import panels.fswebcam_set_pnl ^
  --hidden-import panels.motion_set_pnl ^
  --hidden-import panels.picam_set_pnl ^
  --hidden-import panels.rpicap_set_pnl ^
  --hidden-import panels.libcam_set_pnl ^
  --collect-submodules graph_modules ^
  --collect-submodules datawall_modules ^
  --collect-submodules timelapse_modules ^
  --add-data "%UI_IMAGES_DIR%;ui_images" ^
  --add-data "%GRAPH_MODULES_DIR%;graph_modules" ^
  --add-data "%SENSOR_MODULES_DIR%;sensor_modules" ^
  --add-data "%TIMELAPSE_MODULES_DIR%;timelapse_modules" ^
  --add-data "%GRAPH_PRESETS_DIR%;graph_presets" ^
  --add-data "%DATAWALL_PRESETS_DIR%;datawall_presets" ^
  "%GUI_DIR%\pigrow_remote.py"

if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b 1
)

echo.
echo Build complete.

echo Dist output: %DIST_DIR%

echo Build work files: %WORK_DIR%

echo Spec file: %SPEC_DIR%\PigrowRemote.spec

endlocal
