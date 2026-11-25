"""Exercise production capture methods without importing/starting hardware."""
import ast
from collections import deque
from pathlib import Path
import threading
import time
import types
import unittest
from unittest.mock import Mock, patch

import numpy as np


def methods(path, class_name, names, namespace):
    tree = ast.parse(Path(path).read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    selected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), path, 'exec'), namespace)
    return types.SimpleNamespace(**{name: namespace[name] for name in names})


ROOT = Path(__file__).resolve().parents[1]


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.tts_patch = patch.dict('sys.modules', {
            'modules.module_tts': types.SimpleNamespace(
                needs_mic_flush=lambda: False, clear_mic_flush=lambda: None)
        })
        self.tts_patch.start()
        self.addCleanup(self.tts_patch.stop)
        self.trace = Mock()
        self.ns = dict(np=np, time=time, queue_message=Mock(), voice_trace=self.trace,
                       is_tts_playing=lambda: False)
        self.code = methods(str(ROOT / 'src/modules/module_stt.py'), 'STTManager',
                            ['_record_audio_chunks', '_smart_turn_infer',
                             '_is_silence_detected_smart_turn'], self.ns)
        self.vad = Mock()
        self.vad.empty.return_value = True
        self.vad.is_speech_detected.return_value = False
        self.manager = types.SimpleNamespace(
            sherpa_vad=self.vad, smart_turn_session=None, smart_turn_extractor=None,
            smart_turn_audio_buffer=deque(maxlen=80), _smart_turn_future=None,
            _smart_turn_last_buf_len=0, MAX_SILENT_FRAMES=15, DEBUG=False,
            _get_progress_bar=lambda: (lambda *a: None, lambda: None),
        )

    def test_loud_click_is_not_speech_when_neural_vad_rejects_it(self):
        click = np.zeros((1600, 1), dtype=np.int16)
        click[200] = 30000
        _, detected, silence = self.code._is_silence_detected_smart_turn(
            self.manager, click, False, 0)
        self.assertFalse(detected)
        self.assertFalse(self.manager._frame_is_speech)
        self.assertEqual(silence, 1)

    def test_preserves_pause_after_quiet_speech(self):
        self.vad.is_speech_detected.side_effect = [True, False]
        quiet = np.ones((1600, 1), dtype=np.int16) * 30
        self.code._is_silence_detected_smart_turn(self.manager, quiet, False, 0)
        self.code._is_silence_detected_smart_turn(self.manager, quiet * 0, True, 0)
        audio = np.concatenate(self.manager.smart_turn_audio_buffer)
        self.assertEqual(len(audio), 3200)
        self.assertTrue(np.all(audio[1600:] == 0))

    def test_inference_pads_before_speech(self):
        captured = []
        def extract(audio, **kwargs):
            captured.append(audio)
            return types.SimpleNamespace(input_features=np.zeros((1, 80, 800)))
        self.manager.smart_turn_extractor = extract
        self.manager.smart_turn_session = Mock()
        self.manager.smart_turn_session.run.return_value = [np.array([[0.8]])]
        self.code._smart_turn_infer(self.manager, np.ones(1600))
        self.assertEqual(len(captured[0]), 128000)
        self.assertTrue(np.all(captured[0][:-1600] == 0))
        self.assertTrue(np.all(captured[0][-1600:] == 1))

    def setup_recorder(self, overflow=False):
        mic = Mock()
        mic.read.return_value = (np.zeros((1600, 1), dtype=np.int16), overflow)
        stream = Mock()
        stream.__enter__ = Mock(return_value=mic)
        stream.__exit__ = Mock(return_value=False)
        self.ns['ResamplingInputStream'] = lambda **kw: stream
        m = self.manager
        m.MAX_RECORDING_FRAMES = 250
        m.PRE_SPEECH_TIMEOUT_FRAMES = 80
        m.RECORDING_CHUNK_SECONDS = 0.1
        m.RECORDING_CHUNK_FRAMES = 1600
        m.MODEL_RATE = 16000
        m._chunks_to_float32 = lambda chunks: np.concatenate(chunks).flatten() / 32768.0
        m.vadmethod = 'smart-turn'
        m.shutdown_event = threading.Event()
        m.is_paused = m.is_cancelled = lambda: False
        m._is_silence_detected_silero = m._is_silence_detected_sherpa_onnx = Mock()
        m._is_silence_detected_rms = Mock()
        m._is_silence_detected_smart_turn = lambda *args: self.code._is_silence_detected_smart_turn(m, *args)
        return mic

    def test_missing_vad_never_opens_microphone(self):
        mic = self.setup_recorder()
        self.manager.sherpa_vad = None
        self.assertEqual(self.code._record_audio_chunks(self.manager), (None, 0))
        mic.read.assert_not_called()

    def test_read_timeout_discards_audio(self):
        mic = self.setup_recorder(overflow=True)
        self.assertEqual(self.code._record_audio_chunks(self.manager), (None, 0))
        self.assertEqual(mic.read.call_count, 1)
        self.trace.finish.assert_called_with('recording_aborted', reason='audio_read_timeout')

    def test_silence_ends_without_transcription(self):
        mic = self.setup_recorder()
        self.assertEqual(self.code._record_audio_chunks(self.manager), (None, 0))
        self.assertEqual(mic.read.call_count, 80)

    def test_wall_clock_deadline_overrides_frame_count(self):
        mic = self.setup_recorder()
        self.ns['time'] = types.SimpleNamespace(perf_counter=Mock(side_effect=[0, 30]))
        self.assertEqual(self.code._record_audio_chunks(self.manager), (None, 0))
        mic.read.assert_not_called()

    def test_two_turns_start_with_fresh_detector_state(self):
        self.setup_recorder()
        for _ in range(2):
            self.vad.is_speech_detected.side_effect = [True] * 5 + [False] * 16
            chunks, speech_frames = self.code._record_audio_chunks(self.manager)
            self.assertEqual(speech_frames, 5)
            self.assertIsNotNone(chunks)
        self.assertEqual(self.vad.reset.call_count, 2)


if __name__ == '__main__':
    unittest.main()
