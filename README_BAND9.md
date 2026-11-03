# Mi Band 9 (n66) 模拟器

## 快速启动

### 方法 1：使用 MSYS2 UCRT64 终端（推荐）

1. 打开 **MSYS2 UCRT64** 终端（开始菜单 → MSYS2 → UCRT64）

2. 运行：
```bash
cd "/c/Users/HP/WorkBuddy AI/2026-11-02-17-39-04/Miband-qemu-simulator"
./models/band9/core/qemu-system-arm.exe \
  -M bes1503,hardware-config=models/band9/config/hardware.json \
  -kernel firmware/band9/vela_ap.bin \
  -display sdl
```

### 方法 2：双击批处理文件

双击运行 `run_band9.bat`（如果 MSYS2 已添加到 PATH）

## 文件结构
```
Miband-qemu-simulator/
├── models/band9/
│   ├── config/
│   │   ├── hardware.json      # 硬件配置 (192x490 屏幕)
│   │   └── factory/
│   │       └── nor-seed.bin   # 出厂参数
│   ├── core/
│   │   └── qemu-system-arm.exe  # QEMU 二进制 (53 MB)
│   └── tools/
│       └── run_n66.py         # Python 启动脚本
├── firmware/band9/
│   ├── vela_ap.bin            # 主固件 (6.5 MB)
│   └── vela_resource.bin      # 资源镜像 (88 MB)
├── run_band9.bat              # Windows 批处理启动脚本
└── run_qemu.bat               # 备用启动脚本
```

## 故障排除

如果 QEMU 无法启动，错误代码 `0xC0000139` 表示 DLL 版本不匹配。

解决方案：
1. 确保 MSYS2 是最新版本：在 MSYS2 终端运行 `pacman -Syu`
2. 或者从 [Weilnetz QEMU](https://qemu.weilnetz.de/w64/) 下载预编译版本

## 仓库信息

- GitHub: https://github.com/XYkadicloud/miband-qemu-simulator
- CI 构建: 自动编译 QEMU 并生成 artifact

