# Continuar TARS-AI / Enzo desde un Mac mini

Este repositorio ya contiene el código base, la rama de trabajo y el contexto del proyecto. No se necesita iCloud ni un bundle para retomar el desarrollo.

## Clonar

```sh
cd ~/Desktop
git clone https://github.com/Sergiobasstidas/TARS.git
cd TARS
git switch revision/pi5-enzo
```

La rama `main` conserva la base oficial V3. La rama `revision/pi5-enzo` contiene las adaptaciones de Enzo, cámara, configuración headless y correcciones de voz. No fusionar automáticamente: primero revisar:

```sh
git log --oneline main..revision/pi5-enzo
git diff --stat main...revision/pi5-enzo
```

## Leer antes de tocar código o la Raspberry

1. `migracion/CONTEXTO.md`
2. `migracion/INDICE.md`
3. `migracion/instrucciones/INSTRUCCIONES_SERGIO.md`
4. `migracion/instrucciones/REGLAS_CONTINUIDAD.md`
5. `migracion/documentos/VOICE_FIXES.md`

## Estado importante

- La Raspberry Pi no debe encenderse ni iniciar Enzo, micrófono o cámara sin indicación explícita de Sergio.
- Los fixes de voz están en la rama, pasaron pruebas offline, pero no se desplegaron ni validaron con el micrófono real.
- No ejecutar `Install.sh` completo.
- No borrar, regrabar ni reiniciar la Raspberry como parte de una migración.
- Los secretos, memoria privada, modelos descargados, fotos y claves SSH no están en Git. Permanecen fuera del repositorio y se manejan por separado cuando sea necesario.
- El material de contexto sí está en este repositorio; no hace falta iCloud para continuar el desarrollo.

## Primer diagnóstico autorizado cuando Sergio lo solicite

No iniciar el servicio. Conectarse por SSH y revisar estado, servicio, temperatura, disco y últimos logs. Consultar `migracion/CONTEXTO.md` antes de ejecutar comandos o instalar dependencias.
