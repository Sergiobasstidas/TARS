#!/usr/bin/env python3
"""Silent API and runtime validation for the original TARS-AI pipeline."""

from __future__ import annotations

import argparse
import io
import os
import sys
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--prompt",
        default="Responde únicamente con una confirmación breve de que el razonamiento funciona.",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    src_dir = project_root / "src"
    os.chdir(src_dir)
    sys.path.insert(0, str(src_dir))

    import soundfile as sf
    from openai import OpenAI
    from modules.module_character import CharacterManager
    from modules.module_config import load_config
    from modules.module_llm import initialize_manager_llm, process_completion
    import modules.module_memory as memory_module
    from modules.module_memory import MemoryManager
    from modules.module_openai import _create_speech

    config = load_config()
    character = CharacterManager(config)

    # Validate TTS and STT without sending anything to the physical speaker.
    phrase = "Esta es una prueba silenciosa del sistema de voz de Enzo."
    speech = _create_speech(phrase)
    audio_bytes = speech.read()
    audio_info = sf.info(io.BytesIO(audio_bytes))

    client = OpenAI(api_key=config["TTS"]["openai_api_key"])
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "enzo-validation.wav"
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="es",
        response_format="text",
    )

    class UIStub:
        def think(self):
            return None

    with tempfile.TemporaryDirectory(prefix="tars-validation-") as temp_memory:
        memory_module._MEMORY_DIR = temp_memory
        memory = MemoryManager(
            config=config,
            char_name=character.char_name,
            char_greeting=character.char_greeting,
            ui_manager=UIStub(),
        )
        initialize_manager_llm(memory, character)
        completion = process_completion(args.prompt)

    reply = completion.get("reply") if isinstance(completion, dict) else completion
    print(f"character={character.char_name}")
    print(f"tts={audio_info.samplerate}Hz/{audio_info.channels}ch")
    print(f"stt={str(transcript).strip()}")
    print(f"llm={reply}")


if __name__ == "__main__":
    main()
