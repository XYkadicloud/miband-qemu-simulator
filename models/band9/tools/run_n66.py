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
    machine = ('bes1503,hardware-config=config/hardware.json,'
               'resource-image=firmware/vela_resource.bin,'
               f'nor-fs-image=config/factory/nor-seed.bin,flash-state={out.as_posix()},')
    if args.rotation not in (0, 90, 180, 270):
        args.rotation = 90  # landscape by default for band9
    machine += f'gpu-scanout-bridge=off,display-rotation={args.rotation}'

    command = [
        str(args.qemu.resolve()),
        '-M', machine,
        '-name', 'Xiaomi Smart Band 9 (n66) - Offline',
        '-display', 'sdl,gl=off,show-cursor=on' if args.display == 'sdl' else 'none',
        '-kernel', 'firmware/vela_ap.bin',
        '-qmp', f'tcp:127.0.0.1:{port},server=on,wait=off',
        '-d', 'guest_errors',
        '-D', relative + '/mmio.log',
    ]

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
        'qemu_command': command,
    }

    with (out / 'qemu-stderr.log').open('w', encoding='utf8') as stderr:
        qemu = subprocess.Popen(
            command, cwd=ROOT, env=env,
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
    parser.add_argument('--qemu', type=Path, default=ROOT / 'core/qemu-system-arm.exe',
                        help='Path to QEMU binary')
    args = parser.parse_args()
    main(args)
