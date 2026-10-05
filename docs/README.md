# Alcatel Pixi 3 (10) WiFi 8080: rescate, kernel propio y Android 7

Documentación del trabajo hecho sobre esta tablet a partir del 4 de octubre de 2026. Cada archivo se puede leer por separado: empieza por el estado actual y abre solo la sección que necesites.

## Índice

| Archivo | Para qué sirve |
|---|---|
| [01-estado-actual.md](01-estado-actual.md) | Qué tiene la tablet ahora, qué funciona, qué falta. Empieza aquí. |
| [02-conexion-mediatek.md](02-conexion-mediatek.md) | Cómo hablar con la tablet desde una Mac por la ventana de 3 segundos del preloader. |
| [03-flasheo-y-recuperacion.md](03-flasheo-y-recuperacion.md) | Mapa de particiones, cómo escribir y leer, y cómo volver a un estado bueno según el caso. |
| [04-hardware.md](04-hardware.md) | Hardware confirmado de esta unidad y cómo se obtuvo cada dato. |
| [05-kernel-propio.md](05-kernel-propio.md) | El kernel compilado para la 8080: base, cambios, cómo compilar y cómo empaquetar. |
| [06-android7.md](06-android7.md) | La ROM LineageOS 14.1, cómo se adaptó y cómo se escribe. |
| [07-root-magisk.md](07-root-magisk.md) | Root con Magisk en el Android 5 de fábrica. |
| [08-fuentes-y-busquedas.md](08-fuentes-y-busquedas.md) | Dónde está cada cosa en internet y qué búsquedas ya se agotaron. |
| [09-problemas-y-soluciones.md](09-problemas-y-soluciones.md) | Fallos que ya ocurrieron, con su causa y su arreglo. |

## Lo mínimo que hay que saber

- La tablet es una Alcatel OneTouch Pixi 3 (10) WiFi, modelo 8080, con procesador MediaTek MT8127, 1 GB de RAM y eMMC de 16 GB.
- No tiene ninguna protección de arranque activa. Se puede leer y escribir cualquier partición desde la computadora.
- El preloader nunca se tocó y no debe tocarse: mientras esté intacto, la tablet siempre se puede recuperar.
- Tampoco se tocaron `pro_info` ni `nvram`, que guardan la identidad y las calibraciones de cada unidad.
- Volver al Android 5 de fábrica toma unos 12 minutos con `herramientas/flash.sh`.
- Todo se hizo con una sola unidad. Otra 8080 puede traer otro panel u otro táctil; cómo comprobarlo está en la sección de hardware.

## Qué hay en cada carpeta

En el repositorio:

| Carpeta | Contenido |
|---|---|
| `docs/` | Esta documentación. |
| `herramientas/` | Scripts para atrapar la tablet, escribir, restaurar y hacer ingeniería inversa, más los parches aplicados a mtkclient. |
| `kernel/` | Parches del kernel, las configuraciones y el script de compilación. |
| `reconstruido/` | Piezas obtenidas por ingeniería inversa: controlador del panel y curva de batería. |
| `datos-hardware/` | Datos leídos del kernel de fábrica en ejecución, con el número de serie redactado. |

Carpetas de trabajo que los scripts esperan y que no están en el repositorio, porque son binarios grandes o firmware de terceros:

| Carpeta | Contenido | Cómo se obtiene |
|---|---|---|
| `fw/` | Firmware de fábrica tal como viene en el paquete de Alcatel. | Descomprimir el paquete indicado en la sección de fuentes. |
| `raw/` | Imágenes listas para escribir: firmware convertido, arranques y Android 7. | Con `simg2img.py`, `sdat2img.py` y `empaquetar_boot.py`. |
| `los/` | La ROM LineageOS 14.1 descargada y sus archivos extraídos. | Sección de Android 7. |
| `cmp/` | Kernel de fábrica descomprimido y kernels compilados. | Del arranque de fábrica y de la compilación. |
| `dump_vivo/` | Volcados completos del sistema de fábrica, incluida la tabla de símbolos del kernel. | Con root, desde la propia tablet. |
