# Preferencias y límites de trabajo derivados del chat

Documento reconstruido a partir de solicitudes explícitas de Sergio; no existía como archivo local.

- Responder en español, breve y claro. No repetir toda la explicación en cada paso.
- Explicar decisiones relevantes y posibles mejoras antes de cambiar código, modelos, proveedores, arquitectura o hardware. Ejecutar lo aprobado sin ampliar silenciosamente el alcance.
- Partir del proyecto original y mejorar con evidencia; no cambiar a otro motor por conveniencia sin acordarlo.
- No volver a diseñar una etapa Mac-first. La ejecución final es en Raspberry; el Mac administra y edita.
- No activar TARS, micrófono o cámara sin indicación. La última restricción operativa sigue siendo no arrancar el asistente.
- No pedir repeticiones temporizadas de «Enzo» como diagnóstico principal. Preferir audio reproducible, trazas por etapa y pruebas de sesiones consecutivas.
- No afirmar que la memoria es completa, que existe una voz entrenada o que los fixes de audio están validados en la Pi si solo hay diseño o tests con mocks.
- Preservar modificaciones locales, memoria, configuración y modelos. No resetear ni reemplazar todo el config sin revisar.
- No ejecutar Install.sh a ciegas. La instalación headless se preparó para evitar componentes ajenos al alcance.
- No introducir selección dinámica de modelos. Mantener el modelo de conversación/visión configurado hasta nueva decisión explícita.
- No inventar recuerdos ni experiencias personales de Enzo. Dar prioridad a curiosidad, gentileza, criterio propio y honestidad; humor ocasional sin remates automáticos.
- No exportar claves, contraseñas, tokens, archivos .env, datos biométricos o conversaciones privadas por defecto.
- No crear notas internas dentro del repositorio. Guardar continuidad fuera de él y hacer commits limpios en español.
- El material para CV se excluye: Sergio indicó que ya no lo necesita.
- Esta entrega no autoriza un commit, push, despliegue ni encendido. El código sigue en el repositorio local y no se incluye en esta carpeta.
