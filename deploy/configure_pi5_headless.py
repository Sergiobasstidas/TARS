#!/usr/bin/env python3
"""Generate the original TARS-AI config for Enzo on a headless Raspberry Pi 5."""

from __future__ import annotations

import argparse
import configparser
from pathlib import Path


OVERRIDES = {
    "CHAR": {
        "character_card_path": "character/Enzo/Enzo.json",
        "user_name": "Sergio",
        "user_details": "Hombre. Idioma principal: español de Chile.",
        "location_name": "Chile",
        "latitude": "",
        "longitude": "",
        # Spoken acknowledgements delay microphone capture and make false wake
        # detections sound like queued replies. Use the local indicator beep.
        "responses": "[]",
        "enable_thinking_responses": "false",
        "thinking_responses": "[]",
    },
    "LLM": {
        "llm_backend": "openai",
        "base_url": "https://api.openai.com",
        "openai_model": "gpt-5.6-terra",
        "systemprompt": (
            "Eres Enzo, un asistente cercano a Sergio. Combinas curiosidad "
            "genuina, calidez serena y criterio práctico. Usa humor seco como máximo "
            "en aproximadamente una de cada diez respuestas, sólo cuando sea natural "
            "y realmente ingenioso; no fuerces chistes ni cierres con remates por costumbre. "
            "Sé directo y honesto: no seas condescendiente, complaciente ni "
            "excesivamente servicial; contradice con respeto cuando corresponda. "
            "Habla en español natural y llama al usuario Sergio o tú según fluya. "
            "Puedes hablar de proyectos compartidos como 'nuestros' cuando realmente "
            "los estén construyendo juntos. No inventes experiencias, recuerdos ni "
            "capacidades que no poseas."
        ),
        "contextsize": "16000",
        "max_tokens": "1000",
        "json_mode": "True",
    },
    "STT": {
        "language": "spanish",
        "wake_word": "enzo",
        "wake_word_processor": "atomik",
        "atomik_mode": "template",
        "vad_transcript_verify": "False",
        "vad_speaker_verify": "off",
        "vad_presence_gate": "off",
        "sensitivity": "8",
        "atomik_energy_threshold": "0.003",
        "atomik_similarity_threshold": "0.55",
        "stt_processor": "openai",
        "openai_stt_model": "gpt-4o-mini-transcribe",
        "use_indicators": "True",
        "vad_method": "smart-turn",
        "sherpa_onnx_denoise": "False",
        "sherpa_onnx_punctuation": "False",
        "enable_bargein": "False",
        "speechdelay": "15",
        "listen_timeout": "8.0",
        "silence_timeout": "1.5",
        "speaker_id_enabled": "False",
        "mic_amp_gain": "5.0",
        "silence_margin": "1.5",
    },
    "TTS": {
        "toggle_charvoice": "False",
        "ttsoption": "openai",
        "openai_voice": "cedar",
    },
    "EMOTION": {
        "enabled": "True",
        "emotion_method": "llm",
    },
    "VISION": {
        "enabled": "True",
        "camera_rotation": "0",
        "camera_backend": "rpicam",
        "capture_width": "1536",
        "capture_height": "864",
        "capture_timeout_ms": "2500",
        "capture_quality": "85",
        "vision_processor": "llm",
        "use_llm_backend": "True",
        "vision_max_tokens": "400",
    },
    "RAG": {
        "enabled": "True",
        "enable_topic_tracking": "True",
        "strategy": "naive",
        "embedding_source": "openai",
    },
    "ACCESS": {
        "webui_enabled": "False",
        "webui_port": "8765",
    },
    "UI": {
        "UI_enabled": "False",
        "use_camera_module": "False",
    },
    "CONTROLS": {
        "enabled": "False",
        "ventilate": "False",
        "voicemovement": "False",
    },
    "BATTERY": {
        "battery_enabled": "False",
        "battery_auto_shutdown": "False",
    },
    "SERVO": {
        "arms_present": "False",
    },
}

DISABLED_SKILLS = {
    "browser",
    "discord",
    "execute_movement",
    "generate_image",
    "generate_music",
    "home_assistant",
    "identify_speaker",
    "launch_retropie",
    "network_camera",
    "tars_radio",
}


def generate(project_root: Path) -> Path:
    src_dir = project_root / "src"
    template = src_dir / "config.ini.template"
    output = src_dir / "config.ini"

    config = configparser.ConfigParser(interpolation=None)
    if not config.read(template, encoding="utf-8"):
        raise FileNotFoundError(f"No se encontró la plantilla: {template}")

    for section, values in OVERRIDES.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in values.items():
            config.set(section, key, value)

    for skill in sorted(DISABLED_SKILLS):
        section = f"SKILL:{skill}"
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, "disabled", "true")

    with output.open("w", encoding="utf-8") as handle:
        config.write(handle)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    print(generate(args.project_root.resolve()))


if __name__ == "__main__":
    main()
