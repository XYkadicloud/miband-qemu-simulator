@echo off
setlocal enabledelayedexpansion

rem Set paths
set QEMU_DIR=C:\Users\HP\WorkBuddy AI\2026-11-02-17-39-04\Miband-qemu-simulator\models\band9\core
set FIRMWARE_DIR=C:\Users\HP\WorkBuddy AI\2026-11-02-17-39-04\Miband-qemu-simulator\firmware\band9
set CONFIG_DIR=C:\Users\HP\WorkBuddy AI\2026-11-02-17-39-04\Miband-qemu-simulator\models\band9\config

rem Change to project directory
cd /d "C:\Users\HP\WorkBuddy AI\2026-11-02-17-39-04\Miband-qemu-simulator"

rem Start QEMU with display
"%QEMU_DIR%\qemu-system-arm.exe" ^
  -M bes1503,hardware-config=%CONFIG_DIR%\hardware.json,resource-image=%FIRMWARE_DIR%\vela_resource.bin,nor-fs-image=%CONFIG_DIR%\factory\nor-seed.bin,gpu-scanout-bridge=off,display-rotation=90 ^
  -kernel %FIRMWARE_DIR%\vela_ap.bin ^
  -display sdl ^
  -name "Mi Band 9 Simulator"

endlocal
