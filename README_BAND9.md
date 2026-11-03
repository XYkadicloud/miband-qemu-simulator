# Mi Band 9 (n66) Simulator

## 快速启动

### 方法 1：使用 MSYS2（推荐）
```bash
# 确保已安装 MSYS2 (https://www.msys2.org/)
# 打开 MSYS2 UCRT64 终端，运行：
cd "C:\Users\HP\WorkBuddy AI\2026-11-02-17-39-04\Miband-qemu-simulator"
./models/band9/core/qemu-system-arm.exe \
  -M bes1503,hardware-config=models/band9/config/hardware.json \
  -kernel firmware/band9/vela_ap.bin \
  -display sdl
```

### 方法 2：使用批处理文件
双击运行 `run_band9.bat`（会自动设置 PATH）

## 文件结构
```
models/band9/
├── config/
│   ├── hardware.json      # 硬件配置 (192x490 display, FT5260 touch)
│   └── factory/
│       └── nor-seed.bin   # 出厂参数
├── core/
│   └── qemu-system-arm.exe  # QEMU 二进制 (53 MB)
└── tools/
    └── run_n66.py         # Python 启动脚本

firmware/band9/
├── vela_ap.bin            # 主固件 (6.5 MB)
└── vela_resource.bin      # 资源镜像 (88 MB)
```

## 运行命令
```bash
# 带窗口显示
./models/band9/core/qemu-system-arm.exe \
  -M bes1503,hardware-config=models/band9/config/hardware.json \
  -kernel firmware/band9/vela_ap.bin \
  -display sdl

# 无头模式（用于测试）
./models/band9/core/qemu-system-arm.exe \
  -M bes1503,hardware-config=models/band9/config/hardware.json \
  -kernel firmware/band9/vela_ap.bin \
  -display none
```
