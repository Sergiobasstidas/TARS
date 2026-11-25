#!/usr/bin/env python3
"""Interactively train Atomik wake-word templates one round at a time."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np


def _record_fixed_window(trainer, duration: float) -> Optional[np.ndarray]:
    """Record a fixed window and keep the one-second region with most voice energy."""
    from modules.module_mic import open_native_stream, make_resampling_callback

    for remaining in range(3, 0, -1):
        print(f"   {remaining}...")
        time.sleep(1)

    print("   GRABANDO: di ENZO ahora", flush=True)
    recording: list[float] = []

    def callback(audio_chunk, frames, time_info, status):
        recording.extend(audio_chunk)

    with open_native_stream(
        callback=make_resampling_callback(callback),
        blocksize=512,
    ):
        time.sleep(duration)

    audio = np.asarray(recording, dtype=np.float32)
    if len(audio) < trainer.sample_rate:
        return None

    # Locate the loudest short region, then retain one second around it. This
    # avoids relying on a fixed VAD threshold when the USB module has a high
    # electronic noise floor.
    frame_size = 512
    energies = np.asarray([
        np.sqrt(np.mean(audio[i:i + frame_size] ** 2))
        for i in range(0, len(audio) - frame_size + 1, frame_size)
    ])
    if not len(energies):
        return None

    peak_frame = int(np.argmax(energies))
    peak_sample = peak_frame * frame_size + frame_size // 2
    start = max(0, peak_sample - trainer.sample_rate // 2)
    end = min(len(audio), start + trainer.sample_rate)
    start = max(0, end - trainer.sample_rate)
    sample = audio[start:end]

    baseline = float(np.median(energies))
    peak = float(np.max(energies))
    print(
        f"   Nivel base={baseline:.4f}, voz={peak:.4f}, "
        f"relación={peak / max(baseline, 1e-8):.2f}x"
    )
    if peak < baseline * 1.08:
        return None
    return sample


def _add_template_sample(trainer, audio: np.ndarray) -> bool:
    added = 0
    # Skip synthetic-noise variants: on this microphone their noise can be as
    # loud as the captured voice. Time, pitch and level variants remain useful.
    for variant in trainer.augment_audio(audio)[:7]:
        mfcc = trainer.mfcc_extractor.extract_mfcc(variant)
        if mfcc is not None:
            trainer.templates.append(mfcc)
            added += 1
    print(f"   Se agregaron {added} plantillas.")
    return added > 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wake_word")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--energy-threshold", type=float, default=0.02)
    parser.add_argument(
        "--fixed-window",
        type=float,
        default=0.0,
        help="Record this many seconds and isolate the strongest one-second region.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()

    src_dir = args.project_root.resolve() / "src"
    os.chdir(src_dir)
    sys.path.insert(0, str(src_dir))

    from modules.module_atomik import WakeWordSystem

    trainer = WakeWordSystem(args.wake_word, mode="template")
    trainer.vad.energy_threshold = args.energy_threshold
    trainer.delete_templates()
    trainer.templates = []

    for index in range(1, args.samples + 1):
        while True:
            input(f"\nMuestra {index}/{args.samples}: presiona ENTER para iniciar...")
            if args.fixed_window:
                audio = _record_fixed_window(trainer, args.fixed_window)
                valid = audio is not None and _add_template_sample(trainer, audio)
            else:
                valid = trainer._record_template()
            if valid:
                print(f"Muestra {index}/{args.samples}: válida.")
                break
            print("Muestra inválida; se repetirá esta misma ronda.")

    trainer._save_templates()
    print(f"Entrenamiento terminado: {len(trainer.templates)} plantillas.")


if __name__ == "__main__":
    main()
