#!/usr/bin/env python3
"""Summarize TARS voice timing logs from stdin or a journal export."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path


PREFIXES = ("VOICE_TRACE: ", "WAKE_SCORE: ", "WAKE_CANDIDATE: ", "WAKE_REJECTED: ")


def parse(lines):
    events = []
    for line in lines:
        for prefix in PREFIXES:
            marker = line.find(prefix)
            if marker < 0:
                continue
            try:
                payload = json.loads(line[marker + len(prefix):].strip())
            except json.JSONDecodeError:
                break
            events.append((prefix.strip(), payload))
            break
    return events


def summarize(events):
    traces = defaultdict(list)
    wake_scores = []
    counters = Counter(kind for kind, _ in events)

    for kind, payload in events:
        if kind == "VOICE_TRACE:" and "id" in payload:
            traces[payload["id"]].append(payload)
        elif kind in ("WAKE_SCORE:", "WAKE_CANDIDATE:"):
            if isinstance(payload.get("score"), (int, float)):
                wake_scores.append(float(payload["score"]))

    print(
        "wake: "
        f"scores={counters['WAKE_SCORE:']} "
        f"candidates={counters['WAKE_CANDIDATE:']} "
        f"rejected={counters['WAKE_REJECTED:']}"
    )
    if wake_scores:
        print(
            "wake_scores: "
            f"max={max(wake_scores):.3f} "
            f"median={statistics.median(wake_scores):.3f}"
        )

    if not traces:
        print("turns: no VOICE_TRACE events")
        return

    for trace_id in sorted(traces):
        turn = traces[trace_id]
        first = turn[0]
        last = turn[-1]
        by_stage = {event.get("stage"): event for event in turn}
        stt = by_stage.get("stt_response_received", {})
        record = by_stage.get("recording_finished", {})
        print(
            f"turn {trace_id}: source={first.get('source', '?')} "
            f"end={last.get('stage', '?')} "
            f"total_ms={last.get('elapsed_ms', '?')} "
            f"record={record.get('reason', '?')} "
            f"audio_ms={record.get('audio_ms', '?')} "
            f"stt_ms={stt.get('request_ms', '?')}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log", nargs="?", type=Path)
    args = parser.parse_args()
    if args.log:
        with args.log.open(encoding="utf-8", errors="replace") as handle:
            events = parse(handle)
    else:
        events = parse(sys.stdin)
    summarize(events)


if __name__ == "__main__":
    main()
