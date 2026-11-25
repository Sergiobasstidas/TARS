#!/usr/bin/env python3
"""Validate one on-demand camera capture and Terra vision without mic or TTS."""

from __future__ import annotations

import argparse
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
        default="Describe brevemente lo principal que aparece frente a la cámara.",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    src_dir = project_root / "src"
    os.chdir(src_dir)
    sys.path.insert(0, str(src_dir))

    from modules.module_character import CharacterManager
    from modules.module_config import load_config
    from modules.module_llm import initialize_manager_llm, process_completion
    import modules.module_memory as memory_module
    from modules.module_memory import MemoryManager
    from modules.module_vision import capture_camera_base64

    config = load_config()
    if not config["VISION"]["enabled"]:
        raise RuntimeError("Vision is disabled in config.ini")

    character = CharacterManager(config)

    class UIStub:
        def think(self):
            return None

        def save_memory(self):
            return None

    with tempfile.TemporaryDirectory(prefix="enzo-camera-validation-") as temp_memory:
        memory_module._MEMORY_DIR = temp_memory
        memory = MemoryManager(
            config=config,
            char_name=character.char_name,
            char_greeting=character.char_greeting,
            ui_manager=UIStub(),
        )
        initialize_manager_llm(memory, character)
        image_b64, capture_error = capture_camera_base64()
        if capture_error:
            raise RuntimeError(capture_error)
        completion = process_completion(
            "La imagen de la cámara ya está adjunta. Analízala directamente; "
            "no llames herramientas ni inventes detalles.\n\n"
            f"Consulta: {args.prompt}",
            image_b64=image_b64,
        )
        reply = completion.get("reply") if isinstance(completion, dict) else completion

    print(f"camera_backend={config['VISION']['camera_backend']}")
    print(f"model={config['LLM']['openai_model']}")
    print(f"vision={reply}")


if __name__ == "__main__":
    main()
