"""Offline launcher for Xiaomi Mi Band 9 (n66) using bes1503 overlay."""
import argparse
import datetime
import json
import os
from pathlib import Path
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def main(args):
    launch_start = time.monotonic()
    out = ROOT / 'artifacts/offline-sessions' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    out.mkdir(parents=True)
    relative = out.relative_to(ROOT).as_posix()

    with socket.socket() as reserved:
        reserved.bind(('127.0.0.1', 0))
        port = reserved.getsockname()[1]

    # n66 uses the bes1503 machine (same SoC family as band10pro)
    # Display is landscape (192x490 → window shows 490x192 rotated)
    repo_root = ROOT.parents[0]
    machine = ('bes1503,hardware-config=../models/band9/config/hardware.json,'
               'resource-image=../firmware/band9/vela_resource.bin,'
               f'nor-fs-image=../models/band9/config/factory/nor-seed.bin,flash-state={out.as_posix()},')
    if args.rotation not in (0, 90, 180, 270):
        args.rotation = 90  # landscape by default for band9
    machine += f'gpu-scanout-bridge=off,display-rotation={args.rotation}'

    # Build QEMU command arguments
    display_arg = 'sdl,gl=off,show-cursor=on' if args.display == 'sdl' else 'none'
    qemu_args = [
        '-M', machine,
        '-name', 'Xiaomi Smart Band 9 (n66) - Offline',
        '-display', display_arg,
        '-kernel', '../firmware/band9/vela_ap.bin',
        '-qmp', f'tcp:127.0.0.1:{port},server=on,wait=off',
        '-d', 'guest_errors',
        '-D', relative + '/mmio.log',
    ]

    # Use MSYS2 ucrt64 launcher to run QEMU (QEMU requires MSYS2 runtime)
    msys2_launcher = 'C:/msys64/ucrt64.exe'
    if not os.path.exists(msys2_launcher):
        msys2_launcher = '/c/msys64/ucrt64.exe'
    if not os.path.exists(msys2_launcher):
        raise RuntimeError('MSYS2 not found at C:/msys64')

    # Build the command for MSYS2
    cmd_str = f"cd '{str(ROOT)}' && ./models/band9/core/qemu-system-arm.exe "
    cmd_str += ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in qemu_args])

    env = os.environ.copy()
    system = Path(os.environ['SystemRoot'])
    env['PATH'] = os.pathsep.join((
        str(ROOT.parents[1] / 'runtime/bin'),
        str(system / 'System32'),
        str(system),
    ))

    receipt = {
        'started_at': datetime.datetime.now().astimezone().isoformat(),
        'model': 'band9',
        'board': 'n66',
        'firmware': '3.1.32',
        'display': [192, 490],
        'rotation': args.rotation,
        'qemu_command': [msys2_launcher, '-c', cmd_str],
    }

    with (out / 'qemu-stderr.log').open('w', encoding='utf8') as stderr:
        qemu = subprocess.Popen(
            [msys2_launcher, '-c', cmd_str], cwd=str(ROOT), env=env,
            stderr=stderr, stdout=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        receipt['qemu_pid'] = qemu.pid
        (out / 'launch.json').write_text(json.dumps(receipt, indent=2), encoding='utf8')

        try:
            deadline = time.monotonic() + 15
            qmp = None
            while qmp is None:
                if qemu.poll() is not None:
                    raise RuntimeError('QEMU failed to start; see artifacts/offline-sessions/*/')
                try:
                    from qmp_client import Qmp
                    qmp = Qmp(port)
                except OSError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.1)

            receipt['timings'] = {'qmp_ready_seconds': round(time.monotonic() - launch_start, 3)}
            started = time.monotonic()

            while qemu.poll() is None:
                if (out / 'stop.request').exists() or (args.seconds and time.monotonic() - started >= args.seconds):
                    qmp.call('quit')
                    break
                time.sleep(0.02)

            qemu.wait(timeout=10)
            receipt['exit_code'] = qemu.returncode
            if qemu.returncode:
                raise RuntimeError(f'QEMU exited with code {qemu.returncode}')
        finally:
            if qemu.poll() is None:
                try:
                    if qmp:
                        qmp.call('quit')
                    qemu.wait(timeout=10)
                except Exception:
                    qemu.terminate()
                    qemu.wait(timeout=10)
            if qmp:
                qmp.close()

    receipt.update(ended_at=datetime.datetime.now().astimezone().isoformat())
    (out / 'launch.json').write_text(json.dumps(receipt, indent=2), encoding='utf8')
    print(f'Session: {out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--display', choices=('sdl', 'none'), default='sdl')
    parser.add_argument('--seconds', type=float, default=0, help='Auto-exit after N seconds')
    parser.add_argument('--rotation', type=int, choices=(0, 90, 180, 270), default=90,
                        help='Display rotation (default 90° landscape)')
    parser.add_argument('--qemu', type=Path,
                        default=ROOT.parents[0] / 'models/band9/core/qemu-w64/qemu-system-arm.exe',
                        help='Path to QEMU binary')
    args = parser.parse_args()
    main(args)
