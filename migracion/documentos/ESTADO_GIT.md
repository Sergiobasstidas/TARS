# Estado local de publicación

Actualización posterior al inventario: los cambios se guardaron en `revision/pi5-enzo`, commit `057472d53639d9692034a9d9c20cbad34a5281fd`, sin push ni merge. El inventario que sigue es histórico. Solo permanecen archivos .DS_Store sin guardar. Ver IMPORTAR_EN_MAC_MINI.md en la raíz del paquete.

Fecha de inspección: 2026-11-06. Sin commit/push/fetch.

## Rama y HEAD

codex/pi5-headless

7593f8c8b63c35e3c07cc98665970fe55cee2c23

## Archivos modificados/nuevos

```text
 M .DS_Store
 M .gitignore
 M src/config.ini.template
 M src/modules/module_atomik.py
 M src/modules/module_config.py
 M src/modules/module_llm.py
 M src/modules/module_main.py
 M src/modules/module_mic.py
 M src/modules/module_openai.py
 M src/modules/module_stt.py
 M src/modules/module_tts.py
 M src/modules/module_vision.py
 M src/skills/skill_capture_camera_view.py
 M src/skills/skill_take_photo.py
 M src/skills/skill_volume.py
?? "3d Printer Files/.DS_Store"
?? deploy/
?? src/.DS_Store
?? src/character/Enzo/
?? src/modules/module_voice_trace.py
?? tests/
```

## Archivos nuevos individuales

```text
3d Printer Files/.DS_Store
deploy/analyze_voice_trace.py
deploy/configure_pi5_headless.py
deploy/requirements-pi5-headless.txt
deploy/systemd/tars-ai.service
deploy/train_wakeword_templates.py
deploy/validate_camera_vision.py
deploy/validate_original_runtime.py
src/.DS_Store
src/character/Enzo/Enzo.json
src/character/Enzo/persona.ini
src/modules/module_voice_trace.py
tests/test_atomik_template.py
tests/test_voice_capture.py
```

## Diferencias en archivos versionados (sin contenido fuente)

```text
 .DS_Store                               | Bin 6148 -> 10244 bytes
 .gitignore                              |   4 +-
 src/config.ini.template                 |  25 ++-
 src/modules/module_atomik.py            |  78 ++++++++-
 src/modules/module_config.py            |  22 ++-
 src/modules/module_llm.py               |  15 +-
 src/modules/module_main.py              |  51 ++++--
 src/modules/module_mic.py               |  22 ++-
 src/modules/module_openai.py            |  30 ++--
 src/modules/module_stt.py               | 297 +++++++++++++++++++++++++++-----
 src/modules/module_tts.py               |   4 +-
 src/modules/module_vision.py            |  57 +++++-
 src/skills/skill_capture_camera_view.py |  19 +-
 src/skills/skill_take_photo.py          |  12 +-
 src/skills/skill_volume.py              |  17 +-
 15 files changed, 552 insertions(+), 101 deletions(-)
```

## Documentos ignorados

ARCHITECTURE.md y PROJECT_SUMMARY_CV.md están ignorados por Git. El segundo no se incluye por decisión de Sergio.

No hay commits locales por delante de origin/V3; hay trabajo sin commit. La rama personalizada no aparece en el origen consultado. Ver CONTEXTO.md para los hashes remotos comprobados.
