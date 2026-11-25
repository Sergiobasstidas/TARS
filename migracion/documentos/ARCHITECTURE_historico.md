# Arquitectura de TARS-AI

> Documento de análisis y propuesta. No describe cambios de código ya implementados.
> La adaptación directa a Raspberry Pi 5 y la nueva memoria deben revisarse y aprobarse antes de modificar el código.
> La plataforma base de la Raspberry sí fue diagnosticada, actualizada y asegurada para acceso remoto antes de esta revisión.

## Actualización de implementación — 31 de julio de 2026

La propuesta original de este documento ya comenzó a implementarse. La Camera
Module 3 Wide (`imx708_wide`) está instalada y validada en la Raspberry Pi 5.
La integración headless usa `rpicam-still` para abrir el sensor, estabilizar el
autofocus, capturar un único JPEG de 1536×864 y cerrarlo. Los skills originales
`capture_camera_view` y `take_photo` quedaron habilitados: el primero envía la
captura a `gpt-5.6-terra` y el segundo conserva un archivo local. No existe video
continuo ni se carga Pygame/OpenCV/Picamera2 en el runtime headless.

La captura física, el análisis visual con Terra y el guardado de fotos fueron
probados correctamente. El servicio `tars-ai` permanece detenido por solicitud
del usuario debido a los falsos despertares del micrófono actual; la validación
de cámara se hizo de forma silenciosa, sin STT ni TTS. La memoria v2 descrita en
este documento continúa como diseño pendiente.

## 1. Propósito y alcance

La primera etapa de este proyecto construye solamente la “mente” de TARS:

- conversación profunda y coherente;
- personalidad configurable;
- memoria de largo plazo;
- visión por imágenes bajo demanda;
- voz local en español;
- percepción del entorno sin movimiento físico.

Quedan fuera de esta etapa el cuerpo, los servos, el movimiento, la batería y la pantalla física. El desarrollo y la ejecución se harán directamente en una Raspberry Pi 5 de 8 GB, ya encendida, conectada permanentemente a corriente y protegida por case y Active Cooler. La lógica de conversación debe permanecer separada de los controladores físicos para que el cuerpo pueda agregarse después sin reescribir la mente.

La IA de conversación y visión será un único modelo: **GPT-5.6 Terra**, con identificador oficial `gpt-5.6-terra`. Según la [documentación oficial del modelo](https://developers.openai.com/api/docs/models/gpt-5.6-terra), acepta texto e imágenes como entrada y soporta streaming, function calling y structured outputs, pero no audio. Por eso STT y TTS permanecerán locales. No se propone selección dinámica, fallback entre modelos ni enrutamiento por tarea.

## 2. Estado del repositorio analizado

- Rama activa: `develop`.
- `develop`, `V3` y `origin/V3` apuntan al mismo commit: `7593f8c8b63c35e3c07cc98665970fe55cee2c23`.
- Por lo tanto, en el momento de este análisis no hay diferencias entre la rama activa y la rama oficial `V3`.
- El árbol de trabajo estaba limpio antes de crear este documento.
- No existe `AGENTS.md` en el repositorio.
- El entorno local del repositorio es Python 3.11.15 en `.venv/` en la raíz.
- La Raspberry definitiva ejecuta Python 3.13.5; todo `src/` compiló sintácticamente con esa versión en una copia temporal, pero todavía no se han validado las dependencias de ejecución.
- El lanzador y `Install.sh` esperan, en cambio, un entorno en `src/.venv/`.
- No existen todavía `src/config.ini` ni `.env`; solamente sus plantillas.
- No se ejecutó `Install.sh`, no se inició la aplicación y no se descargaron modelos. El análisis del código sigue siendo estático.
- La Raspberry Pi 5 de 8 GB ya fue diagnosticada con la microSD permanente SanDisk High Endurance de 128 GB, case, Active Cooler y fuente oficial de 27 W.
- Cámara, Waveshare USB TO AUDIO, micrófono y parlante todavía no están conectados; sus pruebas permanecen aplazadas.

### 2.1 Plataforma real validada

| Componente | Estado verificado |
|---|---|
| Sistema | Debian GNU/Linux 13 `trixie`, arquitectura `arm64`. |
| Kernel | `6.18.34+rpt-rpi-2712`, específico para Raspberry Pi 5. |
| Python | 3.13.5 del sistema; `venv` disponible. |
| RAM | 7.9 GiB detectados; alrededor de 7.6 GiB disponibles en reposo. |
| Almacenamiento | SanDisk High Endurance 128 GB; 119.2 GB físicos, partición raíz `ext4` en modo `rw`. |
| Temperatura | Entre 33 °C y 46 °C durante diagnóstico y actualizaciones. |
| Alimentación | `vcgencmd get_throttled` devuelve `0x0`; sin undervoltage ni throttling histórico. |
| Refrigeración | Driver `pwm_fan` cargado; estado 0 bajo temperatura baja, comportamiento correcto. |
| Red | Wi-Fi 2.4 GHz estable, IPv4/IPv6, DNS e Internet operativos. Ethernet permanece sin uso. |
| Bluetooth | Controlador cargado y radio sin bloqueos. |
| USB/PCIe/RP1 | Root hubs USB, puente PCIe BCM2712 y controlador RP1 detectados con sus drivers. |
| SSH | Activo; acceso automatizado mediante una clave Ed25519 exclusiva guardada en el Mac. |
| Servicios | Estado `running`, sin unidades fallidas después de corregir la espera de red. |
| Bootloader | Canal `default`, actualizado a la versión estable del 26 de mayo de 2026. |

Se instalaron todas las actualizaciones oficiales disponibles de Debian/Raspberry Pi OS y se verificó el reinicio posterior. `NetworkManager-wait-online` quedó deshabilitado porque mantenía el arranque esperando durante 60 segundos por Ethernet sin cable. Esto no deshabilita NetworkManager, Wi-Fi ni Ethernet; obliga a que el futuro servicio TARS tenga comprobación y reintento de conectividad propios.

La microSD anterior de 16 GB se usó solamente para diagnóstico inicial y compilación sintáctica. No contiene la instalación permanente. El repositorio aún no se ha desplegado en la tarjeta High Endurance.

## 3. Vista general de la arquitectura actual

TARS-AI es hoy un monolito Python dirigido por callbacks y varios hilos. Sus módulos comparten singletons y referencias globales. La aplicación mezcla cuatro responsabilidades:

1. arranque y ciclo de vida;
2. conversación, prompt y LLM;
3. interfaces de voz, cámara y web;
4. control de hardware físico y UI de la Raspberry.

```text
App-Start.py / tars-launcher.sh
              |
              v
          src/app.py
              |
     +--------+---------+--------------------+
     |                  |                    |
     v                  v                    v
 STTManager       Character/Memory       UI + WebUI
     |                  |                    |
     +----callbacks----> module_main <-------+
                              |
                              v
                        module_llm
                              |
                              v
                        module_prompt
                       /      |      \
              personality  memory   skills
                              |
                              v
                        Terra/API actual
                              |
                    JSON + function calls
                       /              \
                    skills             TTS
                       |                 |
                  vision/hardware     sounddevice
```

### 3.1 Puntos de entrada

| Archivo | Función actual |
|---|---|
| `tars-launcher.sh` | Activa `src/.venv`, usa utilidades Linux y abre `App-Start.py`. |
| `App-Start.py` | Lanzador gráfico Pygame, verificación de actualizaciones, AEC, entrenamiento de wake word y elección de UI. Ejecuta `src/app.py`. |
| `src/app.py` | Punto de entrada real del asistente. Carga configuración, crea managers, inicia WebUI/STT/UI y mantiene el proceso vivo. |
| `src/app_cms.py` | Gestor y metadatos de configuración; también puede ejecutarse como utilidad. |
| `TARS-AI_Server/app-server.py` | Servidor FastAPI opcional para STT, TTS, LLM, visión, embeddings e imagen/música. No es el proceso principal del robot. |

Para la etapa “mente en Raspberry Pi”, `src/app.py` es el punto de entrada funcional relevante. `App-Start.py` y `tars-launcher.sh` están orientados a una instalación completa con pantalla y hardware físico; no deben controlar el arranque headless de esta primera etapa.

### 3.2 Inicialización actual

`src/app.py` realiza, en orden aproximado:

1. cambia el directorio de trabajo a `src/`;
2. carga `config.ini` mediante `module_config`;
3. asigna el perfil `pi5` y aplica sus capacidades;
4. descubre skills;
5. importa y opcionalmente inicia UI, WebUI, visión y Bluetooth;
6. importa siempre batería, temperatura y servos;
7. construye `CharacterManager`, `MemoryManager` y `STTManager`;
8. registra callbacks de voz en `module_main`;
9. inyecta los managers compartidos en `module_main` y `module_llm`;
10. inicializa servos y monitor térmico;
11. inicia STT y entra en un bucle hasta recibir apagado;
12. al cerrar, fuerza el guardado de memoria y detiene subsistemas.

La composición depende de imports y variables globales, no de interfaces. Esto explica por qué desactivar una función en configuración no siempre evita importar su dependencia física.

## 4. Flujo actual escuchar → pensar → responder

### 4.1 Captura y activación

`module_mic.py` usa `sounddevice`/PortAudio y mantiene un único stream compartido mediante `_AudioHub`. Detecta el dispositivo de entrada, trabaja a su frecuencia nativa y remuestrea a 16 kHz. Esta base es adecuada para la Raspberry, pero hoy la selección depende del orden de dispositivos y no de una identidad estable del Waveshare USB TO AUDIO.

`STTManager` implementa:

- wake word: Atomik, FastRTC o sherpa-onnx;
- VAD/fin de turno: RMS, Silero, sherpa-onnx o Smart Turn;
- STT: FastRTC, Silero, sherpa-onnx, OpenAI o servidor externo;
- indicadores sonoros;
- pre-roll, cancelación, barge-in y transcripción especulativa;
- envío opcional de audio a identificación de hablante.

No existe integración con Whisper.cpp. La opción local española pedida deberá agregarse como un adaptador nuevo, no incrustarse dentro de `STTManager`.

### 4.2 Orquestación del turno de voz

Cuando STT produce texto, `module_main.utterance_callback()`:

1. interpreta el JSON emitido por STT;
2. precomputa el embedding de la consulta;
3. intenta resolver la identidad del hablante;
4. cambia el estado global a `THINKING`;
5. crea un pipeline TTS por frases;
6. llama a `module_llm.process_completion()`;
7. transmite los tokens visibles del campo JSON `reply` al UI y al TTS;
8. detecta emoción;
9. ejecuta function calls/skills;
10. guarda conversación, actividades y nuevos recuerdos en hilos de fondo;
11. reproduce una respuesta de seguimiento si un skill bloqueante cambió el resultado;
12. vuelve a `LISTENING` y luego a `STANDBY` cuando vence la sesión.

El estado central (`BOOTING`, `STANDBY`, `LISTENING`, `THINKING`, `TALKING`) vive en `module_state.py` y notifica listeners.

### 4.3 Construcción del prompt y personalidad

`module_character.py` carga una tarjeta JSON por personaje. Para TARS usa:

- `src/character/TARS/TARS.json`: descripción, personalidad, escenario, saludo y ejemplos;
- `src/character/TARS/persona.ini`: rasgos numéricos;
- modelos de voz dentro de la carpeta del personaje.

`module_prompt.py` construye un prompt grande en cada turno. Incluye:

- esquema JSON de respuesta;
- definiciones y ejemplos de skills habilitados;
- reglas de extracción de nuevos recuerdos y actividad actual;
- instrucciones conversacionales;
- rasgos de personalidad, especialmente verbosidad, humor y sarcasmo;
- identidad del hablante y personas visibles;
- estado emocional;
- conversación reciente, resumen heurístico y recuperación RAG;
- fecha, hora y ubicación.

Los rasgos se vuelven a leer si cambió `persona.ini`. La personalidad está parcialmente basada en datos, pero gran parte del comportamiento está codificado directamente en un único prompt de más de 800 líneas. La tarjeta de personaje se carga, aunque su `character_card` completo no es el centro del prompt actual.

### 4.4 LLM

`module_llm.py` es un cliente OpenAI-compatible construido directamente sobre `requests`:

- usa `/v1/chat/completions` (con una variante para DeepInfra);
- soporta los nombres de backend `openai`, `grok`, `deepinfra` y `other`;
- solicita streaming SSE y JSON;
- extrae `reply` mientras llegan tokens;
- repara JSON incompleto o mal formado;
- devuelve `reply`, `function_calls`, `new_memories`, `current_activity` y opcionalmente `emotion`;
- ejecuta skills y escritura de memoria fuera del parseo principal.

Para el objetivo actual no hace falta conservar el selector multi-backend en la capa de dominio. Basta un puerto `LLMClient` con una implementación Terra. El nombre del modelo debe estar en configuración para despliegue, pero no decidirse dinámicamente durante un turno.

### 4.5 TTS y salida

`module_tts.py` separa texto en frases y solapa generación/reproducción con el streaming del LLM. `sounddevice` reproduce audio y soporta interrupción por barge-in. Puede delegar síntesis a Piper, Silero, eSpeak, ElevenLabs, OpenAI o un servidor.

Piper es la elección correcta para voz local. `module_piper.py` carga `libasound.so` de forma incondicional, lo que es compatible con Raspberry Pi OS, pero acopla síntesis y plataforma. Conviene que Piper produzca PCM/WAV y que un adaptador ALSA/PortAudio separado reproduzca el audio; así se pueden reiniciar o diagnosticar ambos componentes por separado.

### 4.6 Flujo WebUI

`module_chatui.py` aloja Flask + Socket.IO, configuración, dashboard, chat, carga de imágenes, voz desde navegador, edición de memoria y control físico. El endpoint `/process_llm` replica gran parte del pipeline de voz:

- construye el turno;
- llama al LLM;
- transmite texto y audio al navegador;
- ejecuta skills;
- guarda memoria y analítica.

Hay duplicación sustancial entre el flujo WebUI y `module_main.utterance_callback()`. Esto puede producir diferencias de comportamiento. La WebUI debería ser un adaptador de entrada/salida que llame a un único `ConversationService`.

`module_router.py` recuerda el último canal activo (`voice`, `webui` u otro registrado) y entrega mensajes allí. Es útil, pero usa estado global mutable y “último canal gana”, algo problemático si se agregan sesiones simultáneas.

## 5. Memoria actual

### 5.1 Almacenamiento

En Pi 4/5 se usa `MemoryManager` + `HyperDB`:

- archivo principal: `src/memory/<personaje>.pickle.gz`;
- documentos con `timestamp`, `user_input`, `bot_response`, actividad, hablante y personas presentes;
- vectores NumPy dentro del mismo pickle;
- `extra_data` para temas y actividades recientes;
- embeddings locales `all-MiniLM-L6-v2`, OpenAI o servidor externo;
- búsqueda vectorial o híbrida (vector + BM25 + RRF + FlashRank);
- boost por recencia y referencias temporales simples;
- expansión por vecinos de conversación;
- flush diferido cada 30 segundos.

En equipos Pi con perfil limitado se usa `MemoryManagerLite`, que guarda JSON y recupera por palabras clave. En la Pi 5 actual se selecciona la memoria completa con embeddings.

### 5.2 Capas lógicas existentes

Aunque el código las llama de forma distinta, hoy existen aproximaciones a:

- **memoria de trabajo:** turnos recientes tomados del final del mismo almacén;
- **memoria episódica:** conversaciones completas con timestamp, recuperadas por RAG;
- **actividad transitoria:** frases con TTL de cuatro horas;
- **memoria semántica:** lista de “topics” extraída por el LLM;
- **resumen reciente:** agrupación heurística de hasta 12 intercambios de las últimas 24 horas.

### 5.3 Limitaciones para el objetivo de años de memoria

1. El pickle es un único archivo que mezcla documentos, vectores y metadatos. No ofrece consultas estructuradas, migraciones de esquema, integridad relacional ni recuperación parcial robusta.
2. `pickle` no debe tratarse como formato confiable o portable entre versiones; cargar un pickle manipulado también es inseguro.
3. Todos los documentos y vectores se cargan en RAM. El costo crecerá con años de conversaciones.
4. Los “topics” están limitados a 100 y su deduplicación es una heurística léxica en inglés.
5. El “resumen” no es un resumen semántico persistente ni jerárquico; se recompone truncando turnos recientes.
6. No hay distinción formal entre perfil permanente, hecho semántico, episodio, resumen o recuerdo importante.
7. No hay procedencia, confianza, contradicción, vigencia o historial de correcciones para un hecho.
8. Los endpoints de edición y borrado usan índices posicionales; esos índices cambian al borrar elementos.
9. No existen comandos conversacionales dedicados para recordar, olvidar, corregir o listar recuerdos.
10. No se almacenan recuerdos visuales ni relación entre una imagen, su análisis, personas, lugar y conversación.
11. Las escrituras se hacen desde hilos sueltos; no hay una cola transaccional única ni garantía clara de orden.
12. La recuperación mezcla la conversación cruda con hechos permanentes y puede introducir ruido o contradicciones en el prompt.

## 6. Sistema de skills actual

`module_skills.py` descubre automáticamente cada `src/skills/skill_*.py`. Un skill expone:

- un diccionario `SKILL` con nombre, prompt, ejemplos, parámetros y configuración;
- una función `execute(parameters, context)`;
- opcionalmente `followup=True` para ejecutar antes de la respuesta final.

La configuración se guarda en secciones `[SKILL:<nombre>]` de `config.ini`. Las definiciones textuales de todos los skills habilitados se concatenan dentro del prompt del LLM. La ejecución se despacha desde `module_llm.execute_function_call()`.

Skills presentes: personalidad, navegador, cámara, Discord, movimiento, generación de imagen/música, Home Assistant, identificación de hablante, RetroPie, cámaras de red, recordatorios, ejecución Python, control del sistema, fotografía, radio, volumen y búsqueda web.

Problemas relevantes:

- todos los archivos se importan durante el descubrimiento, por lo que un skill con dependencia incompatible puede fallar antes de usarse;
- capacidad, permisos y plataforma no forman parte del contrato del skill;
- las definiciones se inyectan como texto, no como tools estructuradas de la API;
- skills físicos pueden quedar visibles al LLM aunque no exista hardware;
- no hay skills de memoria explícita;
- algunos skills ejecutan comandos Linux (`amixer`, `sudo shutdown`, Chromium/lxterminal).

## 7. Visión y cámara actuales

`module_vision.py` ofrece cuatro procesadores:

- BLIP local;
- el mismo backend LLM multimodal;
- OpenAI Vision separado;
- servidor externo de captioning.

El skill `capture_camera_view` es bloqueante. Cuando el modelo decide mirar:

- para backends multimodales captura una imagen y vuelve a llamar al LLM con ella;
- para BLIP/servidor genera primero un caption y hace una segunda llamada de texto;
- `take_photo` captura y persiste un JPEG.

La captura física depende de `UI.module_ui_camera.CameraModule`, que importa `picamera2` y mantiene un hilo continuo de frames. La cámara está además ligada a Pygame y a la UI, aunque esta primera etapa no tendrá pantalla.

Esto contradice parcialmente la política deseada de “no video continuo”: si se inicializa el módulo actual, la cámara captura continuamente para preview/detección aunque solo se envíen snapshots. La nueva etapa debe abrir la cámara únicamente al solicitar una observación, capturar uno o pocos frames, cerrarla y enviar una sola imagen a Terra. Reconocimiento facial continuo o iniciativa propia deben quedar deshabilitados hasta una decisión posterior de privacidad.

## 8. Dependencias y acoplamientos relevantes en Raspberry Pi

### 8.1 Dependencias físicas directas

| Área | Dependencia actual | Riesgo para la etapa “mente” |
|---|---|---|
| Cámara | `picamera2`, `libcamera`, CSI | Está ligada a UI y captura continua; debe funcionar por snapshot sin pantalla. |
| Servos | `board`, `busio`, `adafruit_pca9685`, I²C | Se importan aunque no habrá movimiento y agregan puntos de fallo. |
| Batería | `board`, `adafruit_ina260`, I²C | Se importa aunque el sistema estará siempre conectado a corriente. |
| Temperatura | `/sys/class/thermal/...` | Es útil, pero debe observar CPU/throttling sin activar movimientos de ventilación. |
| Piper | `libasound.so` + modelo ONNX | Debe aislar síntesis de reproducción y validar una voz española. |
| Audio USB | orden de dispositivos PortAudio/ALSA | El índice puede cambiar al reiniciar; debe seleccionarse por nombre/ID estable. |
| Volumen | `amixer` | Debe operar sobre el control correcto del Waveshare, no siempre `Master`. |
| Lanzamiento | `setcap`, `lxterminal`, UI Pygame | Introduce privilegios y pantalla innecesarios para un servicio headless. |
| Apagado | `sudo shutdown now` | Requiere política de autorización y no debe quedar expuesto sin protección. |
| AEC/barge-in | ALSA/Pulse/loopback | Puede realimentar la propia voz de TARS y necesita calibración con el parlante final. |

### 8.2 Dependencias de software principales

- Núcleo: `requests`, `python-dotenv`, `tiktoken`, NumPy.
- Audio: `sounddevice`, `soundfile`, `soxr`/SciPy, Piper.
- STT/VAD actuales: `sherpa-onnx`, FastRTC, Silero, ONNX Runtime, Torch/librosa según configuración.
- Memoria: `sentence-transformers`, `bm25s`, PyStemmer, HyperDB, FlashRank.
- Web: Flask, Flask-CORS, Flask-SocketIO, Eventlet, Pillow.
- Visión/UI: OpenCV, Pillow, Pygame, Transformers/Torch para BLIP, Picamera2.
- Hardware: Adafruit Blinka, PCA9685, INA260, `lgpio` en Pi 5.

`Install.sh` genera un conjunto amplio por modelo de Pi, instala paquetes `apt`, habilita system-site-packages, configura puerto 80 y descarga varios modelos. Aunque ahora estamos en Raspberry, no conviene ejecutarlo a ciegas: instala UI, servos, batería, modelos locales y servicios que no pertenecen a esta etapa. Primero se debe inspeccionar la Pi y acordar una instalación mínima y reproducible.

## 9. Arquitectura propuesta

### 9.1 Principios

1. **Núcleo independiente de hardware.** Conversación, personalidad, memoria y políticas solo dependen de interfaces.
2. **Composición explícita.** Un `bootstrap` carga el perfil `pi5-headless` o `test`; ningún módulo inicializa hardware por el solo hecho de ser importado.
3. **Un solo orquestador de conversación.** Voz, WebUI y futuros canales llaman al mismo servicio.
4. **Terra único.** Un solo cliente y modelo para conversación y visión, sin router dinámico.
5. **Captura visual bajo demanda.** La cámara no corre continuamente.
6. **Memoria canónica estructurada.** La base de datos es la fuente de verdad; índices vectoriales y resúmenes son derivados y reconstruibles.
7. **Degradación explícita.** Una capacidad ausente usa un adaptador `disabled`, no imports fallidos.
8. **Efectos controlados.** Skills declaran capacidades, permisos, plataforma y modo de ejecución.
9. **Configuración validada y sin secretos.** Configuración común versionable; secretos solo en `.env` o almacén del sistema.

### 9.2 Capas

```text
Entradas
  VoiceSession | WebSession | CLI/TestSession
        |
        v
Application
  ConversationService
  VisionService
  MemoryService
  SkillService
  Session/State Service
        |
        v
Domain
  Turn, Message, Persona, Memory, Episode, Fact, Observation, ToolCall
        |
        v
Ports (interfaces)
  LLM | STT | TTS | AudioInput | AudioOutput | Camera | MemoryStore
  Embeddings | Skill | Clock | EventBus | Movement | Power | Display
        |
        v
Adapters
  Terra Responses API | whisper.cpp | Piper | PortAudio/ALSA | Picamera2
  SQLite | disabled hardware | Flask/Socket.IO
```

### 9.3 Estructura objetivo sugerida

```text
src/
  tars/
    bootstrap.py                 # composition root
    domain/
      conversation.py
      persona.py
      memory.py
      vision.py
      skills.py
    application/
      conversation_service.py
      memory_service.py
      vision_service.py
      skill_service.py
      state_service.py
    ports/
      llm.py
      speech_to_text.py
      text_to_speech.py
      audio.py
      camera.py
      memory_store.py
      embeddings.py
      movement.py
      power.py
      display.py
    adapters/
      llm/terra_responses.py
      stt/whisper_cpp.py
      tts/piper.py
      memory/sqlite_store.py
      memory/vector_index.py
      web/flask_socketio.py
  devices/
    camera/
      pi_camera.py               # Picamera2, snapshot only
      disabled.py
    audio/
      waveshare_input.py         # PortAudio/ALSA, selección estable
      waveshare_output.py
      browser_audio.py
    movement/
      pi_pca9685.py
      disabled.py
    power/
      pi_ina260.py
      mains_only.py              # etapa actual: siempre conectado
    display/
      disabled.py
      pi_display.py
  config/
    base.toml
    pi5-headless.toml
    test.toml
  data/                          # fuera del paquete de código
    tars.db
    media/visual/
    indexes/
    backups/
```

Los nombres pueden adaptarse al estilo del proyecto, pero la frontera entre `application`, `ports`, `adapters` y `devices` es la decisión importante. No se propone reescribir todo de una vez: estas fronteras deben extraerse gradualmente, manteniendo el sistema arrancable después de cada fase.

### 9.4 Contratos mínimos

```python
class CameraPort(Protocol):
    def capture(self, request: CaptureRequest) -> CapturedImage: ...

class SpeechToTextPort(Protocol):
    def transcribe(self, audio: AudioBuffer, language: str) -> Transcript: ...

class TextToSpeechPort(Protocol):
    def synthesize(self, text: str, voice: str, language: str) -> AudioStream: ...

class LLMPort(Protocol):
    def respond(self, request: ModelRequest) -> ModelResponse: ...

class MemoryStorePort(Protocol):
    def append_turn(self, turn: Turn) -> str: ...
    def remember(self, memory: MemoryCandidate) -> str: ...
    def search(self, query: MemoryQuery) -> list[MemoryHit]: ...
    def correct(self, memory_id: str, replacement: str) -> str: ...
    def forget(self, selector: MemorySelector) -> ForgetResult: ...
```

Los contratos no deben devolver diccionarios arbitrarios ni exponer objetos de una librería concreta.

### 9.5 Integración Terra

El código actual usa Chat Completions y obliga al modelo a redactar JSON para representar respuesta, tools y recuerdos. Para la nueva arquitectura se recomienda:

- modelo fijo `gpt-5.6-terra`;
- Responses API como interfaz central, tal como recomienda la [guía oficial de modelos GPT-5.6](https://developers.openai.com/api/docs/guides/latest-model);
- streaming para comenzar TTS sin esperar toda la respuesta;
- function calling nativo para skills;
- structured outputs para extracción de memoria;
- entrada multimodal directa para snapshots de cámara;
- `reasoning.effort` configurable globalmente, comenzando con `low` para voz y comparándolo con `medium` mediante pruebas reales;
- timeouts, reintentos acotados y manejo explícito de falta de Internet;
- sin fallback a otro modelo: ante indisponibilidad, TARS informa el problema y conserva el turno pendiente.

La conversación de voz es sensible a latencia. No se debe enviar el historial completo aunque Terra tenga una ventana grande: usar más contexto incrementa costo y demora. El presupuesto de contexto debe ser pequeño, relevante y medido.

## 10. Flujo objetivo de conversación

```text
Micrófono
   |
Wake/VAD -> Audio del turno -> Whisper.cpp (español)
                              |
                              v
                       ConversationService
                      /        |          \
               personalidad  memoria    skills disponibles
                      \        |          /
                              v
                         Terra (stream)
                       /             \
                 respuesta       tool calls
                                    |
                         si necesita mirar
                                    v
                         Camera.capture_once()
                                    |
                         Terra + imagen + contexto
                                    |
                              respuesta final
                                    v
                            Piper -> parlante
                                    |
                         persistencia transaccional
```

Reglas del orquestador:

- cada turno tiene `session_id`, `turn_id`, canal, hablante y timestamps;
- el texto del usuario se persiste antes de efectos externos;
- el contexto recuperado se limita por relevancia y presupuesto de tokens;
- Terra puede pedir `look`, pero la política de visión autoriza solo una captura bajo demanda;
- una imagen enviada por el usuario evita capturar otra;
- tools con resultados necesarios para responder se ejecutan antes de la respuesta final;
- tools de efecto posterior se encolan con estado observable;
- TTS consume solamente texto final/visible, nunca JSON ni razonamiento;
- la misma secuencia se usa desde voz y WebUI.

## 11. Arquitectura de memoria objetivo

### 11.1 Fuente de verdad

Se recomienda **SQLite con WAL** en Raspberry Pi:

- está disponible localmente y no requiere un servidor;
- soporta transacciones, índices, migraciones y backups consistentes;
- puede almacenar años de metadatos y texto;
- permite respaldar o restaurar la memoria sin desplegar un servidor de base de datos;
- los blobs grandes pueden permanecer como archivos, referenciados por hash y ruta.

El índice vectorial debe considerarse una proyección reconstruible. En la primera versión puede guardarse una tabla de embeddings o un índice local sencillo; si el volumen crece, puede reemplazarse sin migrar la historia canónica. En microSD, WAL debe combinarse con checkpoints y escrituras agrupadas para evitar crecimiento indefinido y desgaste innecesario.

### 11.2 Entidades sugeridas

| Entidad | Contenido |
|---|---|
| `people` | Persona, aliases, preferencias de identidad. |
| `conversations` | Sesión, canal, inicio/fin y participantes. |
| `turns` | Mensajes crudos, respuesta, tool calls, timestamps y modelo. |
| `episodes` | Eventos concretos derivados de uno o más turnos. |
| `facts` | Hechos semánticos estables del perfil, con confianza y vigencia. |
| `summaries` | Resúmenes por sesión/día/mes y su rango fuente. |
| `memories` | Recuerdos explícitos o importantes, tipo, prioridad y propietario. |
| `visual_memories` | Imagen, caption, observación, personas, lugar y vínculo al turno. |
| `memory_links` | Relaciones: deriva de, contradice, reemplaza, pertenece a. |
| `embeddings` | Vector, modelo/versión, entidad origen; regenerable. |
| `memory_events` | Auditoría de creación, corrección, olvido y restauración. |

Cada registro debe usar UUID estable, no posición en una lista.

### 11.3 Tipos de memoria

- **Perfil permanente:** nombre, relaciones, preferencias, datos estables y configuración consentida.
- **Episódica:** qué ocurrió, cuándo, con quién, dónde y en qué conversación.
- **Semántica:** conocimiento consolidado sobre la persona o sus proyectos.
- **Actividad reciente:** estado de corta duración con expiración.
- **Recuerdo importante:** marcado explícitamente o por una política revisable.
- **Visual:** imagen opcional, descripción de Terra, objetos/personas y contexto.
- **Resumen:** compresión con referencias a sus turnos fuente; nunca reemplaza el dato crudo.

### 11.4 Escritura y consolidación

1. Guardar el turno crudo de forma transaccional.
2. Pedir a Terra candidatos estructurados: episodio, hechos, actividad e importancia.
3. Validar esquema, longitud, propietario y procedencia.
4. Comparar candidatos con hechos vigentes.
5. Insertar, reforzar o marcar contradicción; no sobrescribir silenciosamente.
6. Generar embeddings fuera del camino crítico mediante una cola local persistente.
7. Consolidar resúmenes al cerrar sesión y después en niveles diario/mensual.

La conversación no debe fallar si el embedding o resumen demora: el turno ya queda seguro y el trabajo pendiente puede reintentarse.

### 11.5 Recuperación

La consulta debe combinar:

- perfil permanente relevante;
- últimos turnos de la sesión;
- episodios por similitud semántica y palabras clave;
- filtros por persona, rango temporal, tipo y estado;
- recencia e importancia;
- diversidad para no devolver cinco variantes del mismo recuerdo;
- resúmenes solo cuando el detalle crudo exceda el presupuesto.

El prompt debe identificar claramente qué contenido es dato recordado y nunca convertir una inferencia en hecho.

### 11.6 Comandos conversacionales

Agregar skills estructurados y testeables:

- `memory_remember`: “TARS recuerda esto”. Crea un recuerdo explícito de alta prioridad y confirma qué se guardó.
- `memory_forget`: “TARS olvida esto”. Busca candidatos, desambigua si hay varios y aplica tombstone/auditoría; el contenido sensible puede purgarse físicamente según política.
- `memory_correct`: “TARS corrige ese recuerdo”. Marca el anterior como reemplazado y crea la versión corregida preservando procedencia.
- `memory_recall`: “TARS qué recuerdas sobre…”. Consulta por tipo/persona/tiempo y responde con trazabilidad comprensible.

“Olvidar” y “corregir” no deben depender solamente de que el LLM redacte bien un texto. El servicio de memoria decide sobre IDs y mantiene un historial consistente.

### 11.7 Memoria visual y privacidad

- No guardar automáticamente toda captura.
- Guardar la imagen solo si el usuario lo pide o la política marca el evento como importante y está habilitada.
- Guardar siempre hash, hora, motivo de captura, conversación, caption y modelo.
- Permitir olvidar tanto la metadata como el archivo.
- Definir retención y backups cifrados antes de acumular datos personales.
- Una observación de Terra debe distinguirse de un hecho confirmado.

### 11.8 Migración desde el pickle

La migración debe ser una utilidad separada y repetible:

1. backup del pickle original;
2. lectura local una sola vez desde una fuente confiable;
3. inserción de documentos como `turns` con IDs;
4. conversión de topics a candidatos de `facts` con procedencia “legacy”;
5. copia de actividades vigentes;
6. generación nueva de embeddings;
7. comparación de conteos y muestras;
8. mantener el pickle intacto hasta aprobar la migración.

## 12. Perfiles de ejecución

### 12.1 Perfil Raspberry Pi 5 headless

- cámara: Picamera2/Camera Module 3 Wide, captura única;
- audio: PortAudio/ALSA seleccionando Waveshare USB TO AUDIO por identificador estable;
- STT: Whisper.cpp local en español, sujeto a benchmark de modelo;
- TTS: Piper local con voz española;
- LLM: Responses API con modelo fijo `gpt-5.6-terra`;
- visión: snapshot JPEG enviado a ese mismo modelo;
- movimiento: `disabled` durante la etapa mente; `pi_pca9685` en una etapa futura;
- alimentación: `mains_only`, sin monitor de batería;
- pantalla: `disabled` durante esta etapa;
- UI: WebUI headless en un puerto no privilegiado;
- memoria: SQLite local y backups;
- supervisión: systemd, health check, temperatura, throttling, disco y memoria.

La Waveshare no necesita contaminar el dominio: es solamente una selección de dispositivos de entrada/salida. El case y el cooler tampoco cambian la lógica; se observan mediante temperatura y flags de throttling.

### 12.2 Perfil diagnóstico

- no llama a Terra ni reproduce audio automáticamente;
- enumera dispositivos ALSA/PortAudio;
- prueba micrófono y parlante por separado;
- captura una imagen de prueba;
- informa temperatura, undervoltage/throttling, RAM, disco e Internet;
- verifica permisos y rutas de datos;
- no inicia servos, batería, pantalla ni skills con efectos.

El diagnóstico base del sistema ya se hizo mediante comandos de solo lectura y quedó registrado en la sección 2.1. Este perfil sigue siendo necesario como programa reproducible para repetir esas comprobaciones después de actualizaciones y para incorporar las pruebas de cámara y Waveshare cuando llegue el hardware.

### 12.3 Perfil test automatizado

- cámara con imágenes fixture;
- STT con transcripciones prefijadas;
- TTS que guarda audio o registra llamadas sin reproducir;
- LLM fake determinista;
- reloj controlable;
- SQLite temporal;
- todos los dispositivos físicos deshabilitados.

Este perfil permitirá probar personalidad, memoria, visión y skills sin micrófono ni red.

## 13. Configuración y dependencias propuestas

Separar configuración, secretos y datos:

```text
config/base.toml            # persona, español, memoria y políticas
config/pi5-headless.toml    # audio USB, Picamera2, recursos y rutas
config/test.toml            # adaptadores fake
.env                        # OPENAI_API_KEY; nunca versionado
data/                       # base, índices, imágenes, logs y backups
```

Grupos de dependencias sugeridos:

- `core`: dominio, configuración, SQLite, HTTP y validación;
- `audio`: sounddevice, soundfile, Piper y wrapper Whisper.cpp;
- `vision-pi`: Picamera2/libcamera mediante paquetes del sistema;
- `web`: Flask/Socket.IO;
- `memory`: embeddings/ranking elegidos;
- `hardware-pi`: Blinka/PCA9685/INA260, solo cuando se habilite cuerpo físico;
- `dev`: pytest, linters, adaptadores fake y herramientas de migración.

No se debe importar un extra que el perfil no haya seleccionado. Tampoco se debe instalar control de servos, batería, UI OpenGL, BLIP o clasificadores Torch si Terra ya cubre visión y emoción.

## 14. Optimizaciones específicas para Raspberry Pi 5

### 14.1 RAM y CPU

- No cargar BLIP, Transformers/Torch ni el clasificador GoEmotions; usar Terra para visión y emoción estructurada.
- No ejecutar simultáneamente varios motores STT. Elegir Whisper.cpp y mantener VAD/wake word como componentes pequeños.
- Cargar Piper una vez y reutilizar el modelo.
- Hacer lazy loading de cámara, speaker ID y skills opcionales.
- Limitar workers e hilos; hoy cada turno puede crear varios hilos sin una cola central.
- Medir RSS, temperatura, throttling, tiempo al primer token y tiempo al primer audio.
- Empezar `reasoning.effort=low` para conversación; subir a `medium` solo si pruebas de calidad lo justifican.

### 14.2 Latencia de voz

- Capturar a la frecuencia nativa del Waveshare y remuestrear una sola vez a 16 kHz.
- Fijar el dispositivo por nombre o propiedad ALSA, nunca solo por índice.
- Mantener VAD ligero antes de Whisper para no transcribir silencio.
- Enviar la consulta a Terra inmediatamente después de cerrar el turno.
- Alimentar Piper por frases desde el streaming de Terra.
- Calibrar AEC y barge-in con el micrófono/parlante definitivos para evitar que TARS se escuche a sí mismo.
- Mantener sonidos de wake/indicadores fuera del buffer que se envía a STT.

### 14.3 Cámara y visión

- No mantener un hilo de video continuo.
- Abrir Picamera2, permitir estabilización breve de exposición/autofoco, capturar un JPEG y liberar la cámara.
- Usar resolución suficiente para la pregunta, no siempre 12 MP; una imagen menor reduce latencia, RAM y costo.
- Conservar la imagen solo cuando el usuario lo pida o la política de memoria visual lo autorice.
- Limitar concurrencia a una captura/análisis a la vez.
- Registrar motivo, hora, tamaño y resultado de cada observación.

Existe un tradeoff que debe decidirse: abrir/cerrar la cámara maximiza privacidad y libera recursos, pero agrega latencia; mantenerla configurada sin enviar imágenes responde más rápido, pero conserva el sensor activo. La recomendación inicial es abrir/capturar/cerrar.

### 14.4 microSD y persistencia

- Usar SQLite WAL con transacciones cortas y escrituras agrupadas.
- Configurar checkpoints y límites de WAL.
- Rotar logs y evitar escribir métricas cada segundo.
- Guardar imágenes comprimidas y aplicar retención.
- Mantener índices/embeddings reconstruibles para no convertirlos en única copia.
- Hacer backup periódico a un destino distinto de la microSD.
- Probar recuperación después de cierre forzado antes de confiar años de memoria al dispositivo.

### 14.5 Red y resiliencia

- Timeouts explícitos para Terra y servicios externos.
- Reintentos solo para fallos transitorios, con backoff y límite.
- Cola persistente para consolidaciones de memoria pendientes.
- Mensaje local breve si Internet cae; no cambiar a otro modelo.
- Health check que distinga sin Internet, sin API, sin audio y sin cámara.
- Sincronización horaria correcta, porque recuerdos y recordatorios dependen de timestamps.
- No depender de `NetworkManager-wait-online`: el servicio TARS debe comprobar conectividad al iniciar, tolerar que Wi-Fi tarde en asociarse y recuperarse sin reiniciar el sistema.

### 14.6 Seguridad

- WebUI en puerto no privilegiado y acceso inicialmente solo por LAN.
- Reemplazar la contraseña por defecto y no exponer túneles automáticos.
- Mantener SSH por clave Ed25519; después de validar recuperación, considerar deshabilitar autenticación SSH por contraseña.
- API key únicamente en `.env` con permisos restrictivos.
- Skills de apagado, ejecución de código, navegador, movimiento y administración deshabilitados por defecto.
- Confirmación explícita para acciones destructivas o físicas.
- Backups cifrados si contienen conversaciones, voces, rostros o imágenes personales.

### 14.7 Operación continua

- Ejecutar mediante systemd con usuario sin privilegios, reinicio acotado y logs rotados.
- Separar diagnóstico de arranque normal.
- Esperar red y dispositivos de audio sin entrar en bucles agresivos.
- Apagado ordenado que vacíe memoria y detenga audio/cámara.
- Watchdog solo después de distinguir un cuelgue real de una llamada lenta a Terra.
- Registrar versión de código, esquema de memoria, modelo y configuración en cada arranque.

## 15. Cambios propuestos por fases

Cada fase termina en una revisión contigo. Antes de comenzar la siguiente se presentarán alternativas, impacto y resultados; no se asumirá una decisión relevante sin consultarla.

### Fase 0 — Inventario real de la Raspberry — completada para el hardware disponible

- Sistema, arquitectura, kernel, Python, RAM y almacenamiento: confirmados.
- Temperatura, Active Cooler, undervoltage y throttling: verificados sin fallas.
- Wi-Fi, Internet, Bluetooth, USB, PCIe/RP1 y SSH: operativos.
- SanDisk High Endurance 128 GB: instalada como almacenamiento permanente.
- Sistema operativo y bootloader: actualizados; reinicio y servicios verificados.
- Repositorio: todavía permanece únicamente en el Mac; no hay datos TARS que migrar desde la Pi.
- Cámara y audio: pendientes porque los dispositivos aún no han llegado.
- `Install.sh`: revisado estáticamente y descartado como instalador de esta etapa.
- Backup: debe definirse antes de comenzar a almacenar memoria real.

**Resultado:** plataforma permanente saludable y accesible, todavía sin cambios de código ni instalación de TARS.

### Fase 1 — Arranque mínimo headless

- Desplegar el repositorio desde el Mac a una ruta versionada de la Pi mediante `rsync`/Git.
- Crear instalación mínima y reproducible para Pi 5.
- Crear un entorno virtual propio en la Pi y resolver compatibilidad real de dependencias con Python 3.13.
- Corregir la ubicación del venv y validar configuración sin secretos.
- Introducir `bootstrap` para `pi5-headless` y `test`.
- Implementar `disabled`/`mains_only`.
- Evitar imports/inicialización de servos, batería, pantalla y UI.
- Añadir smoke tests sin hardware físico.

**Resultado:** TARS arranca y se cierra correctamente como servicio headless sin cámara ni voz.

### Fase 2 — Conversación escrita con Terra

- Extraer `ConversationService` desde `module_main` y `module_chatui`.
- Mantener WebUI como primer adaptador de entrada/salida.
- Encapsular estado de sesión y eliminar globals de managers gradualmente.
- Implementar Responses API con `gpt-5.6-terra`, streaming, function calling y structured outputs.
- Deshabilitar skills físicos o peligrosos.

**Resultado:** conversación de texto completa en la Pi, con personalidad y registro de turnos.

### Fase 3 — Voz local española

- Implementar Whisper.cpp como `SpeechToTextPort`.
- Mantener wake word y VAD como componentes separados.
- Integrar el Waveshare USB por identidad estable.
- Refactorizar Piper y seleccionar/validar una voz española.
- Probar primero pulsar-para-hablar, después wake word y finalmente barge-in/AEC.

**Resultado:** escuchar y hablar en español en la Raspberry sin API de voz.

### Fase 4 — Visión bajo demanda

- Implementar `pi_camera` detrás del contrato de cámara.
- Abrir/capturar/cerrar por observación.
- Enviar la imagen directamente a Terra.
- Desactivar preview y reconocimiento facial continuo por defecto.
- Agregar política y auditoría de capturas.

**Resultado:** “¿qué ves?” funciona con Camera Module 3 sin video continuo.

### Fase 5 — Memoria v2

- Crear esquema SQLite y repositorios.
- Guardar turnos transaccionalmente.
- Implementar perfil, episodios, hechos, resúmenes y memoria visual.
- Agregar comandos recordar/olvidar/corregir/consultar.
- Construir proyecciones vectoriales regenerables.
- Migrar y validar el pickle existente si contiene datos.

**Resultado:** memoria corregible, auditable y escalable a años.

### Fase 6 — Endurecimiento para operación continua

- Pruebas de duración, corte de corriente y recuperación.
- Backup/restore y migraciones de esquema.
- Medición de CPU/RAM/latencia en Pi 5.
- Selección explícita de Waveshare USB y Camera Module 3.
- Servicio systemd, health checks, seguridad y logs rotados.

**Resultado:** TARS puede operar durante largos períodos y recuperarse sin corromper memoria.

## 16. Riesgos y decisiones pendientes de revisión

### Decisiones recomendadas

1. SQLite como fuente canónica; vectores como índice reconstruible.
2. WebUI sin pantalla física para desarrollo.
3. Cámara estrictamente bajo demanda.
4. Whisper.cpp y Piper locales detrás de puertos.
5. Terra único para conversación y visión.
6. Hardware físico deshabilitado mediante adaptadores reales, no flags dispersos.

### Decisiones que deben confirmarse antes de implementar

- aceptar Debian 13/Python 3.13 como base o aislar una versión alternativa solo si una dependencia esencial lo exige;
- método de despliegue desde el Mac: `rsync` directo o Git con una rama de adaptación;
- cámara, Waveshare, micrófono y parlante se integrarán cuando lleguen; la microSD definitiva ya está instalada;
- destino inicial de backup para configuración y memoria; no existen todavía datos previos que migrar;
- Responses API con `gpt-5.6-terra` y esfuerzo inicial `low` o `medium`;
- modelo concreto de Whisper.cpp y objetivo de latencia/calidad en español;
- voz Piper española y si se requiere una voz TARS personalizada;
- pulsar-para-hablar primero o wake word desde la primera versión;
- política de cámara: abrir/cerrar o mantener configurada sin transmitir;
- política de almacenamiento de imágenes y datos biométricos;
- destino, frecuencia y cifrado de backups;
- si se conserva la UI Pygame como extra futuro o se congela durante la etapa mente;
- qué skills no físicos se habilitan inicialmente.

## 17. Criterios de aceptación para Raspberry Pi 5

La primera implementación se considerará lista cuando:

1. arranque de forma reproducible y headless en Raspberry Pi OS;
2. no inicialice servos, batería, movimiento ni pantalla;
3. use explícitamente el micrófono y parlante del Waveshare USB;
4. transcriba español localmente con Whisper.cpp;
5. sintetice español localmente con Piper;
6. use solamente `gpt-5.6-terra` para conversación y visión;
7. capture una imagen solo cuando una interacción visual lo requiera;
8. voz y WebUI compartan el mismo `ConversationService`;
9. movimiento, batería y pantalla estén explícitamente deshabilitados;
10. memoria soporte recordar, consultar, corregir y olvidar por IDs estables;
11. los turnos sobrevivan a reinicios y un índice pueda reconstruirse;
12. existan pruebas con adaptadores fake y una prueba manual completa escuchar → pensar → mirar opcionalmente → responder → recordar;
13. un corte/reinicio no corrompa la memoria;
14. temperatura, RAM, disco, red, audio y cámara puedan diagnosticarse;
15. WebUI y secrets queden protegidos para uso local.

## 18. Protocolo de decisiones antes de tocar código

Antes de cada bloque de implementación:

1. se inspecciona el estado real relacionado;
2. se presentan las opciones viables y sus tradeoffs;
3. se recomienda una opción, explicando costo, latencia, privacidad y mantenimiento;
4. se espera tu aprobación;
5. recién entonces se modifica código o configuración;
6. se prueba el bloque y se muestran resultados antes de continuar.

Acciones externas importantes —instalar paquetes, ejecutar `Install.sh`, cambiar configuración del sistema, habilitar servicios, abrir puertos, borrar memoria, mover datos o apagar el equipo— también requieren acuerdo previo.

## 19. Archivos actuales que serán afectados en una implementación futura

Este documento no los modifica, pero la adaptación probablemente tocará o reemplazará gradualmente:

- `src/app.py` y los lanzadores;
- `module_config.py`;
- `module_main.py`, `module_llm.py` y `module_prompt.py`;
- `module_stt.py`, `module_mic.py`, `module_tts.py`, `module_piper.py`;
- `module_vision.py` y `UI/module_ui_camera.py`;
- `module_memory.py`, `module_memory_lite.py`, `module_hyperdb.py`;
- `module_skills.py` y nuevos skills de memoria;
- `module_chatui.py`;
- imports de batería, servos, temperatura, UI y control del sistema;
- dependencias y scripts de arranque por plataforma.

Hasta aprobar esta arquitectura no debe hacerse ninguno de esos cambios.
