from __future__ import annotations

import base64
import math
import struct

SAMPLE_RATE = 8000
DURATION_SEC = 0.4
FREQUENCY = 880


def _generate_wave() -> bytes:
    frames = []
    total_samples = int(SAMPLE_RATE * DURATION_SEC)
    for n in range(total_samples):
        sample = int(32767 * math.sin(2 * math.pi * FREQUENCY * n / SAMPLE_RATE))
        frames.append(struct.pack('<h', sample))
    return b''.join(frames)


def synthesize_beep_base64() -> str:
    payload = _generate_wave()
    header = b''.join([
        b'RIFF',
        struct.pack('<I', 36 + len(payload)),
        b'WAVEfmt ',
        struct.pack('<IHHIIHH', 16, 1, 1, SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16),
        b'data',
        struct.pack('<I', len(payload)),
    ])
    return base64.b64encode(header + payload).decode('ascii')
