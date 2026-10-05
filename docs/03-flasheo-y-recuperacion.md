# Flasheo y recuperación

Antes de usar cualquier cosa de aquí hay que saber atrapar la tablet; eso está en la sección de conexión con MediaTek.

## Mapa de particiones

Todas están en el área de usuario de la eMMC. Las direcciones se leyeron de la propia tablet y coinciden con el archivo scatter del firmware de fábrica (`fw/KECFEMMCBD00.sca`).

| Partición | Inicio | Tamaño | Nodo en Android | Se puede escribir |
|---|---|---|---|---|
| preloader | zona de arranque 1 | 0x40000 | no tiene | **Nunca** |
| MBR, EBR1, EBR2 | 0x0, 0x80000, 0x4700000 | 0x80000 cada una | | No hace falta |
| pro_info | 0x100000 | 0x300000 | | **No.** Identidad de la tablet |
| nvram | 0x400000 | 0x500000 | | **No.** Calibraciones y direcciones de red |
| protect_f | 0x900000 | 0xa00000 | mmcblk0p2 | No |
| protect_s | 0x1300000 | 0xa00000 | mmcblk0p3 | No |
| seccfg | 0x1d00000 | 0x20000 | | No |
| uboot (LK) | 0x1d20000 | 0x60000 | | Solo con el LK de fábrica |
| bootimg | 0x1d80000 | 0x1000000 | | Sí |
| recovery | 0x2d80000 | 0x1000000 | | Sí |
| sec_ro | 0x3d80000 | 0x600000 | mmcblk0p4 | Solo con el de fábrica |
| misc | 0x4380000 | 0x80000 | | Normalmente vacía |
| logo | 0x4400000 | 0x300000 | | Solo con el de fábrica |
| custpack | 0x4780000 | 0x3e800000 | mmcblk0p5 | Sí |
| expdb | 0x42f80000 | 0xa00000 | | Solo lectura: registros de fallo |
| tee1, tee2 | 0x43980000, 0x43e80000 | 0x500000 cada una | | Solo con el de fábrica |
| android (system) | 0x44580000 | 0x57800000 | mmcblk0p6 | Sí |
| cache | 0x9bd80000 | 0x10000000 | mmcblk0p7 | Sí |
| usrdata | 0xabd80000 | resto del disco | mmcblk0p8 | Sí |

## Imágenes disponibles en `raw/`

La carpeta `raw/` no está en el repositorio: son imágenes de varios gigabytes y parte de ellas es firmware de Alcatel. Se generan a partir del firmware de fábrica y de la ROM con las herramientas de este repositorio; dónde conseguir cada cosa está en la sección de fuentes.

| Archivo | Qué es |
|---|---|
| `boot.img` | Arranque de fábrica sin modificar (kernel de Alcatel de 2017). |
| `boot-magisk.img` | Arranque de fábrica con Magisk. El punto de retorno habitual para Android 5. |
| `boot-p8080-v3.img` | Kernel propio sobre el arranque con Magisk. Funciona con Android 5; el táctil sale invertido. |
| `boot-los-p8080-v1.img` | Kernel de LineageOS con nuestros cambios, más el arranque de la ROM. Para Android 7. La pantalla sale girada 180°. |
| `boot-los-p8080-v2.img` | Igual que la anterior, con la orientación del acelerómetro corregida. Es la que está escrita en la tablet. |
| `system.img`, `custpack.img`, `cache.img`, `userdata.img` | Android 5 de fábrica, convertido a formato crudo. |
| `recovery.img`, `lk.bin`, `logo.bin`, `tz.img`, `secro.img` | Resto del firmware de fábrica. |
| `system-los14.img` | Sistema LineageOS 14.1. |
| `userdata-los14.img` | Datos vacíos para Android 7, con la depuración USB de la Mac preautorizada. |

El respaldo de la zona inicial de la tablet antes de tocar nada está en `inicio_0x0-0x4780000.bin`. Contiene pro_info y nvram originales.

## Escribir una partición

```
mtk wo <inicio> <tamaño del archivo en hex> <archivo> --serialport <puerto> --debugmode
```

El tamaño es el del archivo, no el de la partición. Los scripts lo calculan con `printf "0x%x" $(stat -f %z archivo)`.

La velocidad real es de unos 7 MB por segundo. Escribir `system` toma unos 3 minutos y medio; `userdata`, unos 5.

Después de escribir algo importante conviene releerlo y compararlo:

```
mtk ro <inicio> <tamaño> releido.bin --serialport <puerto> --debugmode
cmp releido.bin archivo
```

## Convertir imágenes

- **Imágenes sparse de Android** (las `.mbn` grandes del firmware): `herramientas/simg2img.py entrada salida`.
- **Formato por bloques de las ROM** (`system.new.dat` más `system.transfer.list`): el procedimiento está descrito en la sección de Android 7.

Una imagen ext4 válida tiene los bytes `53 ef` en la posición `0x438`.

## Qué hacer según el caso

### La tablet arranca pero quiero volver al Android 5 de fábrica

1. Lanzar `pl_catch.py` en segundo plano y ejecutar `adb reboot`.
2. Ejecutar `herramientas/flash.sh`. Escribe LK, arranque, recovery, secro, logo, TEE, custpack, system, cache y userdata, y verifica el arranque con una relectura.
3. Mandar `mtk reset`, desconectar el cable y encender.

El primer arranque tarda entre 10 y 15 minutos porque Android 5 compila todas las apps. Viene en portugués; el idioma se cambia en el asistente inicial.

`flash.sh` escribe el arranque sin Magisk. Para recuperar el root hay que escribir después `raw/boot-magisk.img` en `0x1d80000`.

### Probé un kernel o un arranque nuevo y entró en bucle

1. Conectar la tablet a la Mac tal como está.
2. Ejecutar `herramientas/restaurar_boot.sh`. La atrapa sola, escribe `raw/boot-magisk.img`, lo verifica, copia la partición `expdb` a `expdb_tras_fallo.bin` y manda el reinicio.
3. Desconectar el cable y encender.

Este script solo sirve si el sistema instalado es el Android 5. Con Android 7 instalado, el arranque bueno es `raw/boot-los-p8080-v2.img`.

El orden importa: primero se restaura el arranque y después se lee `expdb`. Al revés, la lectura falló una vez y dejó la tablet trabada.

### Quiero saber por qué no arrancó

La partición `expdb` guarda el registro del último fallo grave del kernel. Se lee con:

```
mtk ro 0x42f80000 0xa00000 expdb.bin --serialport <puerto> --debugmode
```

El contenido es texto mezclado con bytes de control. Buscar `Kernel BUG`, `Kernel panic`, `PC is at` y las líneas anteriores. Así se encontró el fallo de la eMMC que se describe en la sección de problemas.

### La tablet no enciende la pantalla y no aparece por USB

Lo más probable es batería agotada o que se quedó en modo descarga. Dejarla 30 a 40 minutos en un cargador de pared, hacer el reinicio forzado (Encendido 15 segundos) y volver a conectar. En modo descarga casi no carga.

### La tablet aparece como "MT65xx Android Phone" y no avanza del logo

El kernel arrancó y Android está subiendo. En un primer arranque es normal que tarde. Si `adb devices` no la lista es porque la depuración USB está apagada o no autorizada.

## Lectura de batería

`dumpsys battery` devuelve cada dato dos veces en esta tablet: una vez para la batería real y otra para una segunda batería que no existe, con 50 % de relleno. El valor correcto es el primero, o directamente `/sys/class/power_supply/battery/capacity`.
