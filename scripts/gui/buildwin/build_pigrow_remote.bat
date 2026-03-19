@echo off
setlocal

REM Build Pigrow Remote for Windows using PyInstaller.
REM This script is intended to be run from anywhere inside the repo.

cd /d %~dp0\..\..\..

set "BUILDWIN_DIR=scripts\gui\buildwin"
set "DIST_DIR=%BUILDWIN_DIR%\dist"
set "WORK_DIR=%BUILDWIN_DIR%\build"
set "SPEC_DIR=%BUILDWIN_DIR%"

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
if not exist "%WORK_DIR%" mkdir "%WORK_DIR%"

py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onedir ^
  --name PigrowRemote ^
  --icon scripts\gui\ui_images\icon.ico ^
  --paths scripts\gui ^
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
  --add-data "scripts\gui\ui_images;ui_images" ^
  --add-data "scripts\gui\graph_modules;graph_modules" ^
  --add-data "scripts\gui\sensor_modules;sensor_modules" ^
  --add-data "scripts\gui\timelapse_modules;timelapse_modules" ^
  --add-data "scripts\gui\graph_presets;graph_presets" ^
  --add-data "scripts\gui\datawall_presets;datawall_presets" ^
  scripts\gui\pigrow_remote.py

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
