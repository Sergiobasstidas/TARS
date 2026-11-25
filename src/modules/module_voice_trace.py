"""Small structured tracer for the voice pipeline.

The tracer stores timings only; it never records or persists microphone audio.
One trace follows a turn from wake detection through STT, LLM and TTS.
"""

from __future__ import annotations

import json
import threading
import time

from modules.module_messageQue import queue_message


_lock = threading.Lock()
_counter = 0
_current = None


def is_active() -> bool:
    with _lock:
        return _current is not None


def begin(source: str, **fields) -> int:
    """Begin a new voice turn and return its monotonically increasing id."""
    global _counter, _current
    with _lock:
        _counter += 1
        _current = {
            "id": _counter,
            "source": source,
            "started": time.monotonic(),
        }
        trace_id = _counter
    event("wake_detected", **fields)
    return trace_id


def event(stage: str, **fields) -> None:
    """Emit one compact JSON timing event for the current voice turn."""
    with _lock:
        current = dict(_current) if _current else None
    if current is None:
        return

    payload = {
        "id": current["id"],
        "source": current["source"],
        "stage": stage,
        "elapsed_ms": round((time.monotonic() - current["started"]) * 1000),
    }
    payload.update(fields)
    queue_message(
        "VOICE_TRACE: "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    )


def finish(stage: str = "turn_complete", **fields) -> None:
    """Emit the final event and clear the active turn."""
    global _current
    event(stage, **fields)
    with _lock:
        _current = None
