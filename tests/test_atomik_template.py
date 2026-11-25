import sys
import time
import types
import unittest

import numpy as np


# Atomik's detector is pure numpy for these tests. Avoid importing PortAudio on
# development machines that do not have the Raspberry's audio stack installed.
sys.modules.setdefault(
    "modules.module_mic",
    types.SimpleNamespace(
        open_native_stream=None,
        make_resampling_callback=lambda callback: callback,
    ),
)

from modules.module_atomik import WakeWordSystem


class TemplateWakeWordTests(unittest.TestCase):
    def make_detector(self):
        detector = WakeWordSystem(
            "enzo", sample_rate=16000, threshold=0.20, mode="template"
        )
        feature = np.ones((60, 13), dtype=np.float32)
        detector.templates = [feature]
        detector.mfcc_extractor.extract_mfcc = lambda _audio: feature
        return detector

    @staticmethod
    def speech_like_window():
        sample_rate = 16000
        t = np.arange(sample_rate, dtype=np.float32) / sample_rate
        carrier = np.sin(2 * np.pi * 190 * t)
        envelope = np.zeros(sample_rate, dtype=np.float32)
        envelope[1600:6000] = 0.025
        envelope[7200:12800] = 0.040
        return carrier * envelope

    def test_checks_full_window_not_only_oldest_64ms(self):
        detector = self.make_detector()
        audio = self.speech_like_window()
        detector.buffer.extend(audio)

        detector.last_check_time = 0
        first, _ = detector._detect_template()
        detector.last_check_time = 0
        second, _ = detector._detect_template()

        self.assertFalse(first)
        self.assertTrue(second)

    def test_rejects_keyboard_like_impulse(self):
        detector = self.make_detector()
        audio = np.zeros(16000, dtype=np.float32)
        audio[8000] = 1.0
        detector.buffer.extend(audio)
        detector.last_check_time = 0

        detected, score = detector._detect_template()

        self.assertFalse(detected)
        self.assertEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
