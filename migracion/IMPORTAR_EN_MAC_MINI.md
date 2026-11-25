# Importar los cambios para revisión

> **Actualización:** esta guía describe el respaldo previo mediante bundle. Tras la publicación del repositorio personal, la fuente principal es GitHub y la guía vigente es `MIGRACION_MAC_MINI.md` en la raíz. El bundle ya no es necesario para clonar en el Mac mini.

Estado: 6 de noviembre de 2026. Rama local `revision/pi5-enzo`. Commit `057472d53639d9692034a9d9c20cbad34a5281fd`.

Se guardaron 26 archivos del proyecto en un commit, sin push ni merge. Las diez pruebas offline pasaron. No se incluyeron secretos, notas internas ni archivos .DS_Store. La rama V3 permanece intacta.

## Qué transferir

1. La carpeta `migracion-TARS` con documentación.
2. El archivo independiente `TARS-cambios-pendientes.bundle`, junto a ella en el Escritorio.

El bundle es incremental: contiene el commit de trabajo y necesita la base oficial V3. No es un clon completo ni contiene configuración privada, memoria, modelos o claves. Se verificó con `git bundle verify`.

## En el Mac mini: repositorio nuevo

Colocar ambos elementos en el Escritorio. Si no existe una copia local de TARS-AI:

```sh
cd ~/Desktop
git clone --branch V3 https://github.com/TARS-AI-Community/TARS-AI.git TARS-AI
cd TARS-AI
git bundle verify ~/Desktop/TARS-cambios-pendientes.bundle
git fetch ~/Desktop/TARS-cambios-pendientes.bundle refs/heads/revision/pi5-enzo:refs/heads/revision/pi5-enzo
git switch revision/pi5-enzo
```

No usar un clon shallow que excluya el commit base. Si ya existe un repositorio, revisar primero `git status`; no sobrescribir cambios ni recrear carpetas. Después se puede verificar e importar el bundle desde esa copia si contiene la base requerida.

## Revisar antes de integrar

```sh
git log --oneline V3..revision/pi5-enzo
git diff --stat V3...revision/pi5-enzo
git diff V3...revision/pi5-enzo
```

La rama principal de esta base se llama **V3**, no main. No fusionar automáticamente. Si se quiere una rama personal main, decidirlo en la nueva copia. Al ser un commit de conservación con varios componentes, se puede integrar completo o revisar/seleccionar partes mediante una operación posterior explícita.

## Qué falta fuera de Git

- Datos privados, configuración real, modelos y memoria están fuera de esta entrega. La Pi histórica contiene la instalación; no borrarla ni regrabarla para migrar el trabajo de edición.
- La clave SSH del Mac no se copia. Configurar acceso seguro desde el Mac mini, generando una clave nueva o transfiriendo la existente por un medio privado autorizado.
- Si se reinstala la Pi o cambia de dispositivo, respaldar primero memoria, fotos, configuración y modelos con un procedimiento separado. No añadirlos al repositorio por comodidad.
- El venv no se transfiere: recrearlo con las dependencias apropiadas y comprobar las versiones.
- Los fixes de audio no se desplegaron en la Pi. Sigue pendiente instalar/verificar Silero y hacer validación real autorizada.

Para continuar el desarrollo desde el Mac mini, código y contexto están preparados. Para una migración completa del entorno de ejecución, todavía faltan el acceso SSH y el inventario/respaldo de los datos y configuración reales.
