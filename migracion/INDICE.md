# Índice de migración TARS

Fecha de corte: 6 de noviembre de 2026. Leer primero CONTEXTO.md.

Total: **26 archivos**, incluido este índice. Sin código fuente, .env, claves ni material para CV. El bundle de Git va separado en el Escritorio.

- [IMPORTAR_EN_MAC_MINI.md](IMPORTAR_EN_MAC_MINI.md): Instrucciones de importación de la rama y alcance de la migración; actualiza el estado histórico sin commit.

- [CONTEXTO.md](CONTEXTO.md): Documento principal: objetivos, estado, arquitectura, datos, decisiones, bugs, comandos y pendientes del chat.
- [INDICE.md](INDICE.md): Inventario de esta entrega con descripción de cada archivo y exclusiones.
- [documentos/ARCHITECTURE_historico.md](documentos/ARCHITECTURE_historico.md): Análisis y propuesta de arquitectura; contiene secciones antiguas, contrastar con CONTEXTO.md. Copia íntegra.
- [documentos/ATTRIBUTION.md](documentos/ATTRIBUTION.md): Atribución y autoría original. Copia íntegra.
- [documentos/Cableado_alimentacion_original.svg](documentos/Cableado_alimentacion_original.svg): Diagrama de alimentación original para referencia futura. Copia íntegra.
- [documentos/Cableado_datos_original.svg](documentos/Cableado_datos_original.svg): Diagrama de conexiones de datos original; no equivale al montaje headless actual. Copia íntegra.
- [documentos/DUAL-LICENSE.md](documentos/DUAL-LICENSE.md): Condiciones de licencia dual del proyecto. Copia íntegra.
- [documentos/Dependencias_pi5_headless.txt](documentos/Dependencias_pi5_headless.txt): Manifiesto de dependencias headless; no es un lock de lo instalado. Copia íntegra.
- [documentos/Dependencias_servidor_opcional.txt](documentos/Dependencias_servidor_opcional.txt): Dependencias declaradas del servidor opcional. Copia íntegra.
- [documentos/Dependencias_wakeword_trainer.txt](documentos/Dependencias_wakeword_trainer.txt): Dependencias declaradas del entrenador original. Copia íntegra.
- [documentos/Diagnostico_Pi_historico.txt](documentos/Diagnostico_Pi_historico.txt): Salida de diagnóstico original: sistema, SD, temperatura, RAM, red y drivers; identificadores únicos suprimidos. Copia saneada; solo se omitieron valores sensibles/identificadores.
- [documentos/Discord_OS_Amelia.txt](documentos/Discord_OS_Amelia.txt): Anuncio y changelog OS Amelia aportados por Sergio; credenciales de ejemplo suprimidas. Copia saneada; solo se omitieron valores sensibles/identificadores.
- [documentos/Discord_problemas_audio.txt](documentos/Discord_problemas_audio.txt): Conversaciones aportadas por Sergio sobre micrófonos, activación, STT y ruido. Copia íntegra.
- [documentos/ENLACES.md](documentos/ENLACES.md): Enlaces técnicos, productos y referencias conversadas; no precios vigentes.
- [documentos/ESTADO_GIT.md](documentos/ESTADO_GIT.md): Inventario de cambios sin commit y archivos nuevos; sin diffs de código.
- [documentos/Instrucciones_tapa_5_pulgadas.txt](documentos/Instrucciones_tapa_5_pulgadas.txt): Notas de montaje de una modificación física upstream; fuera del alcance actual. Copia íntegra.
- [documentos/LICENSE.txt](documentos/LICENSE.txt): Texto de licencia original. Copia íntegra.
- [documentos/Licencia_modelos_3D.txt](documentos/Licencia_modelos_3D.txt): Licencia de archivos de impresión, relevantes para una fase física futura. Copia íntegra.
- [documentos/README_upstream.md](documentos/README_upstream.md): Presentación y enlaces del proyecto comunitario. Copia íntegra.
- [documentos/Servidor_opcional_README.txt](documentos/Servidor_opcional_README.txt): Guía del servidor opcional de inferencia; no corresponde al servicio de la Pi. Copia saneada; solo se omitieron valores sensibles/identificadores.
- [documentos/VERSIONES_VERIFICADAS.md](documentos/VERSIONES_VERIFICADAS.md): Versiones realmente comprobadas del venv Mac y sistema Pi histórico, sin inventar versiones faltantes.
- [documentos/VOICE_FIXES.md](documentos/VOICE_FIXES.md): Notas de correcciones locales de voz, dependencias y límites de validación. Copia íntegra.
- [documentos/Wakeword_trainer_README.txt](documentos/Wakeword_trainer_README.txt): Documentación del entrenador de palabra de activación original. Copia íntegra.
- [instrucciones/INSTRUCCIONES_SERGIO.md](instrucciones/INSTRUCCIONES_SERGIO.md): Instrucción textual de Sergio sobre repositorios, autoría, commits y contexto externo.
- [instrucciones/REGLAS_CONTINUIDAD.md](instrucciones/REGLAS_CONTINUIDAD.md): Preferencias y restricciones del chat, reconstruidas e identificadas como tales.

## Alcance y exclusiones

- Los documentos originales reflejan momentos distintos; CONTEXTO.md explica qué quedó obsoleto. Las notas históricas no prueban el estado actual de la Pi.
- Los diagramas SVG son del montaje original, no una especificación validada para el equipo actual.
- Los archivos .md/.txt pueden contener ejemplos de comandos o contratos documentales; no se copió ningún módulo .py, script ejecutable, unidad systemd, configuración .ini/.json real, diff de código ni archivo .env.
- No se exportaron datos de memoria, fotos personales, embeddings de hablantes, audio, modelos, cachés, claves SSH, secretos ni credenciales Wi-Fi/router.
- Se excluyó PROJECT_SUMMARY_CV.md por indicación posterior de Sergio.
- Las capturas del chat estaban en rutas temporales que ya no existen; su información relevante se resume en CONTEXTO.md y ENLACES.md. La foto del router se excluye además por contener contraseñas.
- No hay PDF ni Figma disponible confirmado en los documentos utilizados. No se descargaron páginas ni videos. Los JSON de workflows ComfyUI y los medios genéricos del repositorio se excluyen como configuración/activos no utilizados en el alcance actual.
- No se encontró AGENTS.md físico del proyecto ni en las carpetas superiores examinadas. Se exporta la instrucción del usuario y una síntesis fiel de preferencias, no instrucciones internas de plataforma.
- El paquete no sustituye un respaldo de los cambios sin commit; quien continúe necesitará acceso al repositorio local original.
