@echo off
cd /d "C:\Users\HP\WorkBuddy AI\2026-11-02-17-39-04\Miband-qemu-simulator"
set PATH=C:\msys64\ucrt64\bin;%PATH%
start "" "models\band9\core\qemu-system-arm.exe" -M bes1503,hardware-config=models/band9/config/hardware.json,resource-image=firmware/band9/vela_resource.bin,nor-fs-image=models/band9/config/factory/nor-seed.bin,gpu-scanout-bridge=off,display-rotation=90 -kernel firmware/band9/vela_ap.bin -display sdl -name "Mi Band 9 Simulator"
echo Starting Mi Band 9 Simulator...
