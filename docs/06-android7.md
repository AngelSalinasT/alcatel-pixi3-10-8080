# Android 7 (LineageOS 14.1)

## De dónde sale

No existe ninguna ROM para la 8080. Lo que se usa es la de su tablet hermana, la Telekom Puls (`ttab`), con el kernel cambiado por el de este repositorio.

| Dato | Valor |
|---|---|
| Archivo | `lineage-14.1-20220915-UNOFFICIAL-ttab.zip` |
| Tamaño | 292 MB |
| SHA-256 | `9ef45b91be6e914214c3c4a4882ec0d239fcd1e391855112705876dff78d2069` |
| Versión | Android 7.1.2 |

El servidor original de compilaciones ya no existe. El archivo se consiguió en una carpeta compartida enlazada desde el hilo de la Telekom Puls en android-hilfe.de, y el SHA-256 coincide con el publicado ahí. El detalle está en la sección de fuentes.

Según el autor de la ROM, en la versión 16 la cámara no funciona y hay un fallo al despertar; la 14.1 es la estable. Por eso se eligió esta.

## Por qué funciona sin tocar el sistema

Las tres particiones que Android monta tienen el mismo número en las dos tablets: `system` es `mmcblk0p6`, `cache` es `mmcblk0p7` y los datos son `mmcblk0p8`. Así lo declara el fstab de la ROM y así lo reporta la 8080 (`datos-hardware/emmc.txt`).

La imagen del sistema mide 1 467 998 208 bytes y la partición de la 8080 mide 1 468 006 400: cabe.

Hay una sola diferencia que importa. El fstab de la ROM monta `/misc` en `mmcblk0p3`. En la 8080 esa partición es `protect_s`, que guarda datos protegidos de la unidad y no debe escribirse. Esa línea se retira del arranque.

## Pasos

Los nombres de carpeta son los que usan los scripts.

### 1. Extraer la ROM

Descomprimir el zip en `los/x/`. Interesan `boot.img`, `system.new.dat` y `system.transfer.list`.

### 2. Convertir el sistema

La ROM trae el sistema en formato por bloques. Se convierte a una imagen ext4 cruda:

```
herramientas/sdat2img.py los/x/system.transfer.list los/x/system.new.dat raw/system-los14.img
```

El script imprime la firma ext4 de la imagen resultante, que debe ser `53ef`.

### 3. Sacar el ramdisk del arranque de la ROM y retirar `/misc`

El arranque es una imagen de Android con una cabecera de MediaTek de 512 bytes delante del kernel y otra delante del ramdisk. Para obtener el ramdisk se toma el segundo bloque, se le quitan los 512 bytes y se descomprime con gzip. El resultado es `los/x/ramdisk.cpio`.

```
herramientas/ramdisk_quitar_misc.py los/x/ramdisk.cpio los/x/ramdisk-p8080.cpio.gz
```

El script edita el archivo cpio sin extraerlo, para conservar dueños y permisos, e imprime la línea que retiró.

### 4. Compilar el kernel

Rama `p8080-los`, descrita en la sección del kernel. El resultado es un `zImage`.

### 5. Armar el arranque

```
herramientas/empaquetar_boot.py los/x/boot.img <zImage> raw/boot-los-p8080-v2.img los/x/ramdisk-p8080.cpio.gz
```

### 6. Preparar la partición de datos

Para no depender de la pantalla en el primer arranque, se generó en Linux una imagen ext4 de 2 010 120 192 bytes con dos archivos:

| Ruta dentro de la imagen | Contenido |
|---|---|
| `misc/adb/adb_keys` | La llave pública de adb de la computadora. Dueño 1000:2000, permisos 640. |
| `property/persist.sys.usb.config` | `mtp,adb`. Dueño root, permisos 600. |

Con eso adb queda autorizado desde el primer arranque. Si no hace falta, sirve una imagen ext4 vacía o la de fábrica.

No quedó registrado el comando exacto con el que se creó la imagen; el contenido y los permisos de arriba se leyeron de la imagen con `debugfs`.

### 7. Escribir

Con la tablet atrapada (sección de conexión):

```
herramientas/flash_los.sh
```

Escribe el arranque en `0x1d80000` y lo verifica releyéndolo, luego `system` en `0x44580000`, `cache` en `0x9bd80000` y los datos en `0xabd80000`. No toca preloader, LK, `pro_info`, `nvram` ni `custpack`. Tarda unos 10 minutos.

Al terminar hay que desconectar el cable y encender con el botón.

## Resultado

Android 7.1.2 arranca completo. Qué funciona y qué falta está en la sección de estado actual.

## Volver a Android 5

`herramientas/flash.sh` reescribe todo el firmware de fábrica. Está descrito en la sección de flasheo y recuperación.
