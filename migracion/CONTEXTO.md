# TARS-AI / Enzo — Contexto de continuidad

Fecha de corte: 6 de noviembre de 2026, America/Santiago.

## Actualización posterior: cambios preservados en una rama

Después de preparar este documento, Sergio autorizó guardar el trabajo para revisarlo en el Mac mini. Se creó `revision/pi5-enzo` y el commit `057472d53639d9692034a9d9c20cbad34a5281fd` con 26 archivos. No se hizo push ni merge. Las diez pruebas offline volvieron a pasar. Solo quedaron `.DS_Store` fuera del commit. Los apartados siguientes que hablan de cambios sin commit describen el inventario anterior a esta actualización.

El archivo externo `~/Desktop/TARS-cambios-pendientes.bundle` transporta ese commit y requiere la base V3 `7593f8c8b63c35e3c07cc98665970fe55cee2c23`. Ver `IMPORTAR_EN_MAC_MINI.md`. La carpeta documental sigue sin código; el bundle va separado. Los fixes siguen sin desplegar en la Pi y no se inició ningún servicio.

Este documento reúne las decisiones del chat y una inspección de solo lectura del repositorio local. Distingue implementación, resultados históricos y planes. No es una certificación del estado actual de la Raspberry: no se contactó ni arrancó el dispositivo para preparar este paquete. No contiene código fuente, credenciales ni archivos de entorno. El material para CV se excluyó por petición expresa de Sergio.

## 1. Lo primero que debe saber quien retome

- Propietario y usuario: Sergio Bastidas Acosta. Es un proyecto personal, no un encargo para un cliente externo identificado.
- Proyecto base: TARS-AI Community. Nombre provisional actual del personaje: **Enzo**; antes se consideraron TARS y Ogan.
- Plataforma real: Raspberry Pi 5 de 8 GB. El Mac es estación de edición/administración, no el servidor de conversación definitivo.
- El principal bloqueo es la conversación por micrófono: falsos despertares por teclado, voz ignorada y respuestas tardías. No está resuelto en hardware.
- Los últimos fixes están **solo en los archivos locales**, sin commit y sin desplegar en la Pi. Pasaron diez pruebas automatizadas en la sesión anterior, con dobles de prueba; no validan el modelo real ni la acústica.
- La memoria v2, el reconocimiento fiable de personas y una voz propia siguen pendientes. No presentarlos como terminados.
- No encender Enzo, iniciar servicios, activar micrófono/cámara ni lanzar pruebas habladas sin una nueva indicación. La instrucción anterior fue analizar y corregir sin arrancar el sistema.
- Sergio no quiere pruebas temporizadas del tipo «di Enzo ahora» repetidas. Quiere registros y pruebas reproducibles que expliquen la causa.
- Esta carpeta es documentación, **no un respaldo del código ni de los datos persistentes**. Un clon de GitHub no recuperará las modificaciones locales.

## 2. Estado exacto de Git y publicación

Ruta local: `/Users/sergiobastidasacosta/Desktop/TARS-AI`.

Origen: https://github.com/TARS-AI-Community/TARS-AI.git

Rama activa: `codex/pi5-headless` (nombre preexistente, no creado durante esta migración).

HEAD: `7593f8c8b63c35e3c07cc98665970fe55cee2c23`, del 13 de abril de 2026, merge de la corrección de detección del dispositivo de micrófono.

Comprobación remota realizada con `git ls-remote --heads origin` el 6 de noviembre:

| Rama remota | Commit |
|---|---|
| V3 | 7593f8c8b63c35e3c07cc98665970fe55cee2c23 |
| Development | d2181be5ebf0d94fb923ae26144daf500e9f6f61 |
| V2 | 0949deea35212e737812445e14f428e8e2de90de |
| V1 | 5a8796b3f08b9598e8007ca0bc55bcd34f28bd64 |

No aparece la rama local personalizada entre las ramas publicadas. No hay commits locales adicionales respecto de `origin/V3`: el contador es cero. Hay **15 archivos versionados modificados y 14 archivos nuevos sin seguimiento**; los segundos incluyen dos `.DS_Store`, por lo que no todos son entregables. Los cambios todavía no se convirtieron en commits. Las ramas locales `V3` y `develop` también están en ese HEAD. No se descargó ni comparó `Development`; no afirmar que carece de mejoras.

Archivos versionados modificados: `.DS_Store`, `.gitignore`, `src/config.ini.template`, módulos `module_atomik`, `module_config`, `module_llm`, `module_main`, `module_mic`, `module_openai`, `module_stt`, `module_tts`, `module_vision`, y skills `skill_capture_camera_view`, `skill_take_photo`, `skill_volume`.

Nuevos relevantes: scripts y servicio bajo `deploy/`, `src/character/Enzo/Enzo.json`, `src/character/Enzo/persona.ini`, `src/modules/module_voice_trace.py`, `tests/test_atomik_template.py`, `tests/test_voice_capture.py`.

`ARCHITECTURE.md` y `PROJECT_SUMMARY_CV.md` están ignorados por Git; el primero se rescata aquí. `deploy/VOICE_FIXES.md` existe aunque no aparece entre los archivos nuevos de `git status`; se incluye como apoyo. No se hizo commit, push, fetch, reset ni modificación del repositorio para esta migración. Antes de publicar, revisar destinos y permisos: `origin` apunta al proyecto comunitario, no a un fork personal confirmado.

## 3. Objetivo, alcance y hardware

Construir la mente de un asistente físico inspirado en TARS: conversación profunda, personalidad propia y evolutiva, memoria duradera, voz expresiva, visión y percepción contextual. Primera etapa sin cuerpo, servos, movimiento, batería ni pantalla. La conexión a Internet y a corriente es permanente.

Hardware confirmado por el chat y los documentos históricos:

- Raspberry Pi 5, 8 GB, case y Active Cooler oficial.
- Fuente oficial Raspberry Pi 27 W.
- SanDisk High Endurance 128 GB, tarjeta definitiva. Una tarjeta de 16 GB se utilizó temporalmente; no es el sistema permanente.
- Raspberry Pi Camera Module 3 Wide, sensor identificado como `imx708_wide`, cable CSI de 15 a 22 pines. Integración histórica validada.
- Waveshare USB TO AUDIO, referencia Amazon B0CN1C1VPR, con micrófono integrado.
- Dos parlantes pasivos de 8 Ω / 5 W según el historial. El conector de cuatro pines fue fotografiado, pero su paso/pinout no se debe dar por certificado solo con la imagen.
- Micrófono de campo lejano ReSpeaker XVF3800/Lite estudiado, **sin compra ni instalación confirmadas**.

Al inicio se quería desarrollar todo primero en Mac M1; Sergio descartó expresamente ese camino al recibir la Pi. Se mantuvo la idea de desacoplar hardware, pero no hay obligación de construir primero proveedores de cámara/audio del Mac.

## 4. Stack y versiones: comprobado versus pendiente

| Componente | Versión o selección | Evidencia / límite |
|---|---|---|
| Sistema Pi | Raspberry Pi OS Lite 64-bit / Debian 13 Trixie; diagnóstico reporta Debian 13.5 | Diagnóstico histórico adjunto |
| Arquitectura | aarch64 / ARM64 | Diagnóstico histórico |
| Kernel Pi | 6.18.34+rpt-rpi-2712 | Diagnóstico histórico; no reconsultado |
| Python Pi | 3.13.5 | Diagnóstico histórico; paquetes instalados no inventariados ahora |
| Python `.venv` del Mac | 3.11.15 | Verificado el 6 de noviembre |
| Paquetes del `.venv` Mac | packaging 26.2, pip 26.1.2, setuptools 83.0.0, wheel 0.47.0 | Es un entorno casi vacío, no el runtime de la Pi |
| NumPy requerido headless | 2.1 | Única versión fijada explícitamente en ese manifiesto |
| LLM configurado | `gpt-5.6-terra` | Cadena literal del proyecto y decisión de Sergio; disponibilidad comercial actual no verificada en esta migración |
| STT configurado localmente | `gpt-4o-mini-transcribe`, idioma español | La revisión anterior usaba `whisper-1`; config real de la Pi no leída ahora |
| TTS provisional | `gpt-4o-mini-tts`, voz `cedar` | Código y generador actual |
| Activación | Atomik, modo `template`, palabra `enzo` | Código local |
| Detección de habla | Silero VAD mediante sherpa-onnx | Añadido localmente; falta instalación/modelo y prueba en Pi |
| Fin semántico de turno | Smart Turn, archivo `smart-turn-v3.2-cpu.onnx` | Nombre esperado por el código; no inventario remoto |
| Cámara | `rpicam-still`, JPEG 1536×864 | Configuración local e integración histórica |
| API LLM | Chat Completions sobre requests/SSE | Responses API es propuesta, no migración completada |

Dependencias headless: openai, tiktoken, numpy, scipy, soxr, sounddevice, soundfile, pydub, requests, configobj, python-dotenv, joblib, onnxruntime, sherpa-onnx, transformers, bm25s, pystemmer, hyperdb-python, flashrank, Adafruit Blinka/PCA9685/INA260, lgpio, flask, flask-cors, flask-socketio, eventlet y Pillow. La mayoría no tienen versión fijada. No existe un lock reproducible completo en la entrega. El manifiesto copiado no equivale a `pip freeze` de la Pi.

Otros componentes del proyecto base: PortAudio/ALSA, systemd, Piper, Pygame, Picamera2, Torch/librosa según backend, servidor FastAPI opcional. No todos están activos ni instalados en el perfil actual. Los IDs de modelo son identificadores configurados, no versiones inmutables certificadas.

## 5. Arquitectura que existe realmente

Es un monolito Python con callbacks, hilos, managers compartidos y estado global. No se completó la separación en puertos/adaptadores.

### Arranque y servicios

- `src/app.py`: entrada funcional. Carga configuración, managers, skills y callbacks; inicia las capacidades habilitadas y el ciclo de vida.
- `App-Start.py` y `tars-launcher.sh`: lanzadores originales orientados a la instalación completa; esperan el venv en otra ruta y pueden activar UI/hardware.
- `deploy/systemd/tars-ai.service`: servicio headless, usuario/grupo `sergio`, directorio de trabajo `/home/sergio/TARS-AI/src`, venv `/home/sergio/TARS-AI/.venv`. Ejecuta `app.py show_ui=false speed=true`, reinicia ante fallo y limita permisos. Lee secretos de un archivo de entorno externo al versionado.
- `TARS-AI_Server/app-server.py`: servidor opcional de inferencia local/remota; no es requisito del despliegue vigente.
- WebUI Flask/Socket.IO: se usó para conversar por texto, con acceso histórico desde `localhost:8765`. El generador actual tiene `webui_enabled=False`; no asumir que sigue abierta.

### Flujo de voz

Micrófono USB → `_AudioHub` en `module_mic.py` → remuestreo a 16 kHz mono → Atomik reconoce activación → grabación del turno → Silero clasifica voz/ruido y Smart Turn evalúa el final → transcripción OpenAI → `module_main` → construcción de prompt/memoria/skills → LLM en streaming → TTS por frases → parlantes → persistencia de conversación y metadatos.

La transcripción actual es por audio grabado al finalizar el turno. No es un flujo OpenAI Realtime instalado y validado. Semantic VAD de OpenAI y Smart Turn local no son lo mismo. Silero aquí detecta habla: no transcribe palabras ni impone el idioma de SenseVoice.

### Módulos y responsabilidades

| Área | Archivos o directorios |
|---|---|
| Orquestación/estado | `module_main.py`, `module_state.py` |
| Audio/activación/transcripción | `module_mic.py`, `module_atomik.py`, `module_stt.py` |
| Síntesis/salida | `module_tts.py`, `module_openai.py`, otros proveedores |
| Modelo/prompt | `module_llm.py`, `module_prompt.py`, `module_character.py` |
| Memoria | `module_memory.py`, `module_hyperdb.py`, `module_memory_lite.py` |
| Skills | `module_skills.py`, `src/skills/skill_*.py` |
| Cámara | `module_vision.py`, skills de captura/foto |
| Web/canales | `module_chatui.py`, `module_router.py` |
| Identidad | `module_identity.py`, `module_speaker_id.py` |
| Recordatorios | `module_heartbeat.py`, `skill_reminder.py` |
| Diagnóstico | `module_speed.py`, `module_voice_trace.py`, `deploy/analyze_voice_trace.py` |

Estados: `BOOTING`, `STANDBY`, `LISTENING`, `THINKING`, `TALKING`. Voz y WebUI todavía duplican partes del flujo. El enrutador usa el canal activo global.

### Visión

`capture_camera_view` permite obtener una imagen y usar el mismo modelo de conversación para interpretarla. `take_photo` guarda una fotografía. El adaptador headless abre `rpicam-still`, permite estabilización/autofoco, captura y finaliza; no transmite video continuo. Dimensiones 1536×864, timeout de captura configurado de 2500 ms y calidad JPEG 85. La UI original conserva rutas distintas con Picamera2; no confundirlas con el camino headless.

### Skills

Se descubren archivos `skill_*.py`; exponen diccionario `SKILL` y función `execute(parameters, context)`. La configuración usa secciones `[SKILL:nombre]`. Las definiciones se insertan en el prompt; no existe aún la migración completa a herramientas nativas tipadas.

Hay skills de volumen, personalidad, cámara/foto, búsqueda, recordatorios, control del sistema, navegador, Discord, Home Assistant, radio, música, imagen, movimiento, RetroPie, cámara de red y ejecución en sandbox. El perfil deshabilita navegador, Discord, movimiento, generación de imagen/música, Home Assistant, identificación de hablante, RetroPie, cámara de red y radio. No asumir que todo lo demás es seguro por defecto: revisar especialmente control de sistema y ejecución de código antes de habilitar exposición remota.

## 6. Modelo de datos actual

**No hay una base SQL implementada como memoria canónica.** No inventar tablas actuales basándose en la propuesta SQLite.

| Archivo/entidad actual | Estructura y relación |
|---|---|
| `src/memory/<personaje>.pickle.gz` | HyperDB serializa `documents`, `vectors`, `extra_data`. Vectores alineados con documentos, sin claves foráneas SQL |
| Documento de conversación | `timestamp`, `user_input`, `bot_response`, opcional `activity_context`, `speaker`, `present` |
| Topics/actividades | Metadatos asociados al almacén; actividades con expiración, topics recuperables. Existe ruta legacy `<personaje>_topics.json` |
| `initial_memory.json` | Semilla opcional de memoria |
| `voice_memory.json` | Lista `speakers`: nombre, rol, embeddings, creación; nombres vinculan hablantes con conversaciones |
| `<personaje>_interaction_log.json` | Log de dashboard, hasta 500 entradas; prompt detallado solo en las 50 más recientes. No es archivo histórico de años |
| `scheduled_tasks.json` | Recordatorios persistentes de una vez; tareas recurrentes se registran al arrancar |
| Tarjeta de personaje JSON | Descripción, personalidad, escenario, saludo, ejemplos y metadatos |
| `persona.ini` | Rasgos numéricos de personalidad |
| Configuración INI | Secciones funcionales y skills; separar de secretos |
| Fotos y caché de TTS | Archivos de medios; no constituyen por sí mismos memoria visual estructurada |

Recuperación: contexto reciente + embeddings/RAG, opcional búsqueda híbrida BM25/RRF/FlashRank, recencia y vecinos. El perfil local usa RAG `naive`, embeddings OpenAI y seguimiento de topics. El pickle carga documentos/vectores en RAM; hay guardado diferido. Parte del resumen es heurística y no una consolidación durable por niveles.

### Modelo propuesto, todavía pendiente

SQLite con WAL como fuente canónica. Entidades: `people`, `conversations`, `turns`, `episodes`, `facts`, `summaries`, `memories`, `visual_memories`, `memory_links`, `embeddings`, `memory_events`. IDs estables; personas participan en conversaciones; conversaciones contienen turnos; episodios/hechos/resúmenes derivan de turnos; recuerdos visuales referencian imagen y turno; enlaces registran contradicción/reemplazo; eventos auditan cambios. Índices vectoriales reconstruibles y medios en archivos separados.

Guardar primero el turno crudo; extraer candidatos, validar, resolver contradicciones y luego consolidar/embeber en segundo plano. Definir backup, retención y borrado coherente antes de acumular años de datos. Skills futuros: recordar, olvidar, corregir y consultar recuerdos con desambiguación y trazabilidad.

## 7. Roles, permisos y reglas de negocio

- Sergio administra el equipo y define políticas. No se diseñó un sistema multiusuario empresarial ni un RBAC integral.
- `voice_memory` admite etiquetas `admin`, `guest`, `unknown`, pero una etiqueta biométrica no garantiza autorización efectiva en todos los skills.
- Identificación de hablante y gates de persona/presencia/verificación de transcripción están deshabilitados en la configuración local actual.
- La WebUI tiene autenticación por contraseña/sesión Flask; no publicar contraseñas por defecto ni exponer el servicio a Internet por comodidad.
- SSH por clave Ed25519 se configuró históricamente. No se copian claves, firmas ni credenciales en esta entrega.
- Servicio ejecutado como usuario no root, con `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem` y restricciones de escritura; las capacidades de cada skill requieren revisión adicional.
- No mirar ni grabar continuamente. Captura por petición visual o necesidad de responder; iniciativa visual futura requiere una política explícita de frecuencia, costo y privacidad.
- No inventar recuerdos, experiencias, sentidos ni hardware disponible. Diferenciar observación, inferencia y dato confirmado.
- Mantener un solo modelo para conversación y visión, sin selección dinámica. No cambiar STT/TTS/proveedor silenciosamente: Sergio ha objetado cambios no acordados.
- Acciones destructivas, cambios de sistema, despliegues y activación de sensores deben acordarse según el alcance. En esta migración solo se autorizó lectura y creación de documentación externa.

## 8. Identidad y estilo de Enzo

Sergio quiere una mezcla de amigo/colaborador, competencia sobria de JARVIS y sabiduría cálida de Iroh. También mencionó el ingenio de House como referencia de picardía, no de crueldad. Masculino, gentil, curioso, directo, cálido, sereno, emocionalmente perceptivo, capaz de discrepar y sin condescendencia ni servilismo teatral.

La curiosidad debe ser natural: reconocer temas abiertos, consultar si ya se hablaron, decidir si retomarlos aporta y elegir el momento. No preguntar por obligación en cada respuesta. Se necesita memoria y política de iniciativa; no basta un adjetivo en el prompt.

Le gusta la cercanía de expresiones como «nuestros proyectos» o «nuestros discos» cuando tiene sentido real. Tratarlo de Sergio o tú según fluya. No fingir vivencias humanas ni vulnerabilidad biográfica inventada.

Humor: molestaban remates plásticos en cada respuesta. Dirección actual: muy ocasional, aproximadamente una de cada diez respuestas, sutil y creativo; no es un contador obligatorio. En momentos serios reducirlo al mínimo sin prohibición absoluta mecánica. Honradez y capacidad de discrepar no deben confundirse con sarcasmo.

Valores actuales de `persona.ini`: verbosity 35; humor 25; sarcasm 30; honesty 95; empathy 80; curiosity 95; confidence 75; formality 30; adaptability 75; discipline 80; imagination 70; emotional_stability 80; pragmatism 80; optimism 65; resourcefulness 90; cheerfulness 55; engagement 85; respectfulness 75. Son parámetros de prompt, no garantías matemáticas de comportamiento.

Advertencia de inconsistencia: la tarjeta conserva un `world_scenario` antiguo que dice que no hay cámara, y ejemplos iniciales con remates más frecuentes. Otras partes de la misma tarjeta ya expresan la nueva política. Revisar conjuntamente tarjeta, `persona.ini`, system prompt del generador y `module_prompt.py`; no asumir que un solo archivo controla todo.

## 9. Decisiones tomadas, alternativas y evolución

| Tema | Decisión actual / explicación |
|---|---|
| Plataforma | Pi directa; se descartó esperar/desarrollar primero toda la versión Mac |
| Hardware | Sin cuerpo/pantalla/servos/batería por ahora; separar capacidades para añadirlos después |
| Instalación | Evitar `Install.sh` completo a ciegas: instala más hardware, UI y modelos de los necesarios |
| Modelo | Terra fijo para pensar y ver; no router dinámico |
| STT | El deseo inicial era local y gratuito, con Whisper.cpp en evaluación. Más adelante Sergio pidió volver al flujo original y aceptó explorar API. Actualmente el código local usa mini-transcribe; la Pi puede conservar otra revisión |
| Realtime | Se discutieron Realtime y Semantic VAD; no tratarlos como implementados. No reemplazar la arquitectura sin explicar costo, latencia y controles |
| TTS | Piper español se probó y no convenció por fluidez/expresividad; OpenAI cedar quedó provisional. Español de España descartado; neutro latino o mexicano |
| Volumen | Primero 40%, después 30%; control por voz mediante skill adaptado a tarjeta/control ALSA |
| Voz propia | Interés en crear/poseer/descargar una voz, no solo pagar una biblioteca. Qwen/Chatterbox y GPU alquilada en Runpod fueron explorados, sin entrenamiento/exportación final confirmados |
| Costos | Sergio pidió comparar dos horas de conversación al día, suscripciones/anualidad y pago por uso. No hay presupuesto ni tarifa vigente fijados; no reutilizar precios viejos como actuales |
| Reconocimiento de personas | Aprendizaje progresivo durante conversaciones, sin obligar a cada invitado a recitar frases. Identidad provisional y confianza antes de asignar nombre; voz+rostro para segunda iteración |
| Cámara | Capturas únicas, no video continuo. Cámara instalada posteriormente; memoria visual pendiente |
| Memoria | El RAG actual no basta. Perfil, episodios, hechos, resúmenes e instrucciones explícitas de memoria son prioridad de diseño |
| Almacenamiento | High Endurance 128 GB definitiva; SSD/otro equipo de red se conversó, sin decisión de migración. Respaldar fuera de la SD sigue pendiente |
| Micrófono | ReSpeaker considerado; no culpar exclusivamente a hardware: se encontraron problemas de software |

Una GPU alquilada es un computador remoto para ejecutar inferencia/entrenamiento. Crear una referencia de voz o descargar pesos no significa que la Pi pueda sintetizar esa voz con baja latencia; aún hay costo de cómputo y licencia. No afirmar que hubo un despliegue Runpod activo ni que existe una voz entrenada.

## 10. Diagnóstico de voz y fixes locales

Síntomas: primera llamada responde a veces; segunda pregunta se pierde; minutos después una tos, tarareo o teclado dispara «sí, Sergio / te escucho». La voz baja a veces sí se captura. No se probó que sea exclusivamente ganancia, API lenta, español o una cola de cinco minutos. Los registros previos también mostraban nuevas falsas activaciones repetidas.

Discord aportó casos similares: necesidad de hablar cerca, ruido del ventilador, frases incompletas y timeouts. El autor recomendó consola de debug y Atomik `template` en lugar de sherpa para wake word; eso ya se usaba aquí. Otro participante mejoró con PipeWire, pero no es una solución demostrada para esta instalación. El changelog OS Amelia describe Smart Turn, streaming TTS, gates y arreglos de concurrencia; no prueba que todos los errores estén solucionados.

### Cambios implementados localmente en septiembre

1. Umbral de similitud de wake word del generador: 0.20 → 0.55. Es punto de partida, no calibración validada. El archivo config.ini existente en Pi no se actualiza automáticamente.
2. Smart Turn usa detección de habla Silero vía sherpa-onnx antes de decidir silencio/voz, en lugar de solo RMS. No cambia el backend de transcripción a SenseVoice.
3. Conserva pausas en el audio semántico y rellena al inicio hasta ocho segundos según la referencia de Smart Turn.
4. Lectura de micrófono con presupuesto total de espera de un segundo; se descarta una lectura fallida en el grabador compartido.
5. Límite de tiempo real del turno, cancelación y reseteo del detector entre capturas. Se cuentan frames clasificados como voz para Smart Turn.
6. Si falta Silero en el grabador compartido, aborta explícitamente en vez de degradar silenciosamente a detección por volumen. Sin Smart Turn pero con Silero, usa fin por silencio.
7. Dependencia sherpa-onnx agregada al manifiesto headless. Falta asegurar `src/stt/silero_vad.onnx` en la Pi.

Ya había otros cambios anteriores: bloques de 100 ms, timeout de inicio de voz de 8 s, silencio de 1.5 s, indicadores locales y acknowledgements hablados vacíos, traces por etapa, revisión de ventana completa Atomik y filtros de impulsos. El último perfil mantiene ganancia 5.0, energía mínima 0.003, sensibilidad 8, barge-in desactivado. No suponer que cada ajuste fue validado acústicamente.

Pruebas previas: diez tests pasaron. Cubren impulso rechazado, pausa preservada, relleno inicial, VAD ausente, timeout de lectura, silencio, límite de reloj y dos turnos consecutivos. Los tests extraen métodos por AST y usan mocks para evitar iniciar hardware. No prueban la precisión real de Silero contra un teclado ni el rendimiento en Pi.

### Riesgos abiertos que no se deben ocultar

- Cálculo de MFCC/detección Atomik todavía en callback de audio; puede consumir tiempo del hilo de captura.
- `post_utterance_callback` reinicia escucha mediante llamada recursiva a transcripción; revisar sesiones largas y cancelación.
- Ajustes de tamaño de bloque no son uniformes entre todos los backends: la ruta sherpa conserva lecturas de 4000 muestras y requiere auditoría de tiempos.
- El cambio de timeout del hub es global; necesita probarse con todos los consumidores utilizados.
- Verificar indicación sonora y pre-roll para no contaminar/transcribir el beep ni perder el inicio de la pregunta.
- Silero tiene histéresis; distinguir frames de voz de cola de silencio al medir mínimo de habla.
- Smart Turn requiere probar caché/inferencias en curso al llenar la ventana y entre pausas; no basta un test de padding.
- Timeouts/reintentos de red y TTS aún pueden bloquear el flujo síncrono.
- No se midieron p50/p95 de fin de voz→STT→primer token→primer audio con el hardware actual.

## 11. Estado por prioridad

### Hecho o históricamente probado

Preparación de Pi/SD/SSH; diagnóstico de sistema; servicio headless; conversación escrita; identidad Enzo; pipeline voz demostrado pero inestable; salida USB y volumen; cámara bajo demanda e interpretación; scripts de configuración/validación; arquitectura y análisis de memoria; fixes locales y tests offline.

### Prioridad 0 — preservar y verificar

1. Respaldar/versionar cambios locales antes de cambiar de equipo o clonar de nuevo. Este paquete no incluye código por instrucción expresa.
2. Verificar, cuando Sergio autorice contacto con Pi, qué revisión/config/modelos/dependencias tiene y si el servicio está detenido. No arrancarlo como efecto lateral del diagnóstico.
3. Revisar y desplegar fixes mínimos preservando configuración y datos; instalar solo la dependencia/modelo faltantes. Revisar también diferencias en rama remota Development, sin merge masivo ni reset.

### Prioridad 1 — voz confiable

4. Pruebas offline con grabaciones consentidas/reproducibles de voz, silencio y teclado; verificar pérdida de audio, falsos despertares y cierre de turno.
5. Medición por etapas, pruebas de dos preguntas consecutivas y cancelación. Sin pedir repetir el nombre artificialmente durante ventanas cortas.
6. Decidir micrófono/ubicación/AEC solo después de separar software y acústica. ReSpeaker sigue siendo opción, no requisito ya comprado.

### Prioridad 2 — coherencia y memoria

7. Corregir inconsistencias de identidad y calibrar humor con ejemplos reales.
8. Diseñar/implementar memoria v2, comandos explícitos y backup/restauración; conservar datos legacy hasta validar migración.
9. Unificar conversación de voz/WebUI y separar hardware gradualmente; no reescribir todo sin plan revisable.

### Prioridad 3 — expansión

10. Voz propia expresiva, prosodia variable, pausas y sonidos no verbales; comparar costo total y viabilidad local/remota.
11. Identificación progresiva de voces, luego fusión con rostro; privacidad, consentimiento, incertidumbre y separación de recuerdos por persona.
12. Memoria visual, iniciativa de observación con presupuesto y control; cuerpo físico más adelante.

## 12. Otras deudas técnicas

No hay lock completo de dependencias ni inventario actual de Pi. Memoria en pickle no escala ni ofrece migraciones/transacciones; guardados/hilos y recuperación tras corte requieren pruebas. Dashboard no conserva todos los detalles para siempre. Índices posicionales dificultan borrar/corregir recuerdos de forma segura. Temporalidad/deduplicación tienen heurísticas en inglés. Faltan permisos de skills transversales y aislamiento real por usuario. Imports siguen acoplando hardware aunque esté desactivado. UI y voz duplican orquestación. Selección de dispositivos/mezcla estéreo debe comprobarse con el equipo final.

`ARCHITECTURE.md` conserva secciones antiguas: rama develop, hardware aún pendiente, voz local Piper/Whisper.cpp, cámara Picamera2, Responses API y SQLite como futuro. La actualización inicial de ese archivo no reescribe todo. Este CONTEXTO prioriza el código actual y las decisiones posteriores. No copiar los criterios antiguos como si fueran el estado real.

## 13. Convenciones y estructura

- Python; módulos funcionales `module_*.py`, skills `skill_*.py`, clases de managers y funciones snake_case. Predominan comentarios/docstrings en inglés en el upstream.
- `src/character/<Nombre>/` agrupa tarjeta y persona. `src/memory/` son datos, no código. `src/tts/` y `src/stt/` contienen modelos/caché. `deploy/` reúne operación headless; `tests/` pruebas offline.
- Configuración INI con secciones funcionales; secretos por variables de entorno. No versionar claves, datos privados, audio personal ni plantillas biométricas sin decisión explícita.
- Mantener licencias y atribución de autores originales. No atribuirse la creación íntegra de TARS-AI.
- Commits en español, sin firmas, coautorías ni menciones a herramientas de asistencia. No crear instrucciones, relevo o notas internas dentro del repositorio. Esta carpeta externa contiene la continuidad.
- Preservar cambios del usuario y no hacer `git reset --hard`, checkout destructivo ni ejecutar el instalador general por conveniencia.
- Sergio prefiere respuestas breves, sin repetir contexto. Explicar alternativas/impacto antes de cambios de dirección; la autorización de una tarea concreta permite ejecutar esa tarea, no cambiar silenciosamente de proveedor o arquitectura.

## 14. Variables de entorno — solo nombres

Necesaria para el perfil actual: `OPENAI_API_KEY`.

Operación/audio/servicio: `TARS_AUDIO_CARD`, `TARS_AUDIO_CONTROL`, `PYTHONUNBUFFERED`, `PYTHONPYCACHEPREFIX`, `SDL_AUDIODRIVER`, `TOKENIZERS_PARALLELISM`.

Si se habilita WebUI: `FLASK_SECRET_KEY`. La contraseña de acceso de WebUI se gestiona en configuración y no se copia aquí.

Opcionales del proyecto base, según integraciones activadas: `VISION_API_KEY`, `EXTERNAL_API_KEY`, `ELEVENLABS_API_KEY`, `GROK_API_KEY`, `DEEPINFRA_API_KEY`, `OTHER_API_KEY`, `DISCORD_TOKEN`, `HA_TOKEN`.

No se necesitan todas para arrancar el perfil actual. Ningún valor se incluye en este apartado ni se copian archivos de entorno.

## 15. Comandos y procedimiento operativo

Son instrucciones para una ejecución futura autorizada; no se ejecutaron contra la Pi al generar este paquete. No copiar bloques de arranque sin revisar el estado y permisos.

### Lectura de estado local, sin cambios

```sh
cd /Users/sergiobastidasacosta/Desktop/TARS-AI
git status --short
git branch -vv
git diff --stat
git ls-remote --heads origin
```

### Acceso a Pi

```sh
ssh sergio@tars.local
```

Se configuró una clave privada dedicada en el Mac; localizarla de forma segura si SSH normal no la selecciona. No se entrega la clave. La IP LAN histórica fue 192.168.0.15; puede cambiar. Si cambia la huella SSH tras regrabar la SD, confirmar identidad antes de eliminar el registro conocido. No desactivar verificación de host.

### Diagnóstico Pi sin iniciar el asistente

```sh
hostnamectl
python3 --version
vcgencmd measure_temp
vcgencmd get_throttled
free -h
df -h /
systemctl is-active tars-ai
systemctl --failed
journalctl -u tars-ai -n 150 --no-pager
```

Revisar logs antes de compartirlos: pueden contener conversación privada. Para inventario de versiones, usar `python -m pip list --format=freeze` desde el venv de la Pi y revisar la salida antes de exportarla.

### Instalación headless en Pi (paso pendiente de aprobación)

Ruta prevista `/home/sergio/TARS-AI`; crear venv solo si no existe:

```sh
cd /home/sergio/TARS-AI
python3 -m venv .venv
.venv/bin/python -m pip install -r deploy/requirements-pi5-headless.txt
```

Necesita bibliotecas del sistema para ALSA/PortAudio y cámara rpicam. No hay receta apt completamente congelada/verificada para reinstalar todo en esta entrega. Obtener `silero_vad.onnx` desde el enlace oficial del apartado de recursos y colocarlo en `src/stt/`; comprobar carga con la versión instalada. Mantener Smart Turn en su ruta esperada. No sustituir STT por SenseVoice al instalar sherpa-onnx.

El generador `deploy/configure_pi5_headless.py --project-root /home/sergio/TARS-AI` **reescribe config.ini completo**. Solo usar en instalación nueva o después de respaldar/comparar; para una Pi ya configurada aplicar cambios selectivos. Nunca copiar una configuración con secretos al paquete documental.

### Pruebas offline, desde la raíz

```sh
PYTHONPYCACHEPREFIX=/tmp/tars-pycache PYTHONPATH=src python3 -m unittest discover -s tests -v
git diff --check
```

Requieren NumPy/SciPy en el intérprete de pruebas. El venv Mac inventariado no los tiene; no afirmar que ese venv ejecuta la batería sin preparación. Las diez pruebas históricas corrieron con otro intérprete local disponible. Los scripts `validate_original_runtime.py` y `validate_camera_vision.py` son distintos: pueden llamar APIs de pago y el segundo abre cámara. «Silencioso» significa sin parlante, no sin sensores ni red.

### Despliegue y servicio

Transferir solo archivos revisados mediante Git/rsync, sin `--delete`, preservando memoria, modelos, fotos y configuración real. Un clon remoto hoy no basta para obtener los cambios. No subir secretos. Comprobar si el servicio está activo antes de cambiar archivos; acordar detención/despliegue.

Cuando se autorice instalar la unidad:

```sh
sudo cp deploy/systemd/tars-ai.service /etc/systemd/system/tars-ai.service
sudo systemctl daemon-reload
```

Arranque explícito para probar (activa escucha): `sudo systemctl start tars-ai`.
Detener escucha/proceso: `sudo systemctl stop tars-ai`.
Arranque automático, solo si se vuelve a acordar: `sudo systemctl enable tars-ai`.
Apagar toda la Pi: `sudo shutdown -h now`.

Históricamente Sergio autorizó arranque automático, pero después pidió detener el micrófono/servicio por falsas respuestas. No interpretar esa autorización antigua como permiso para reactivarlo ahora.

Analizar trazas ya existentes sin iniciar servicio:

```sh
cd /home/sergio/TARS-AI
journalctl -u tars-ai --no-pager | .venv/bin/python deploy/analyze_voice_trace.py
```

## 16. Recursos, documentos y límites de la migración

Consultar `INDICE.md` para cada copia y `documentos/ENLACES.md` para repositorios, productos y referencias. Se incluyen los dos textos de Discord, diagnóstico histórico, arquitectura, notas del fix y diagramas de cableado upstream. Se preservaron licencias. Los documentos heredados pueden incluir ejemplos de código dentro del texto, pero no se copiaron archivos fuente ejecutables del repositorio.

Las capturas temporales referidas en el chat ya no están disponibles en sus rutas. No se inventaron imágenes ni se exportó la foto del router con credenciales. No hay PDF, archivo Figma o diseño externo disponible confirmado en el material inspeccionado. Se excluyeron el documento de CV, `.env`, claves, configuraciones con secretos, datos de memoria, modelos de voz, audio personal y código fuente. Donde una copia documental contenía credenciales de ejemplo, se eliminaron sus valores.

No se exportan instrucciones internas de plataforma ni archivos globales ajenos al proyecto. En `instrucciones/` se conserva la instrucción proporcionada por Sergio y las reglas de continuidad derivadas del chat, identificadas como tales; no se finge que existía un AGENTS.md local cuando no se encontró.

La siguiente persona debe leer primero este archivo, luego las notas del fix y los textos de Discord. La tarea inmediata es preservar el código sin commit y terminar la validación de voz; no volver a la etapa inicial de instalar una Pi desde cero.
