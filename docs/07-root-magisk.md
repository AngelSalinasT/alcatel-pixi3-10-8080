# Root con Magisk en el Android 5 de fábrica

El root hizo falta para leer datos del kernel de fábrica en ejecución: la tabla de símbolos con direcciones, los buses I2C, el estado de los pines y los registros del cargador. Sin esos datos no se habría podido reconstruir el panel.

Se usó Magisk 25.2. No se usó ningún recovery personalizado: el arranque se parchó a mano por adb.

## Procedimiento

1. Abrir el APK de Magisk como un zip. Los binarios están en `lib/armeabi-v7a/` con nombres del tipo `libmagiskboot.so`; se renombran quitando el prefijo `lib` y la extensión. Hacen falta `magiskboot`, `magiskinit`, `magisk32`, `magiskpolicy` y `busybox`, más los scripts `boot_patch.sh` y `util_functions.sh` de la carpeta `assets/`.
2. Copiar todo a la tablet, a `/data/local/tmp/mg`, junto con el arranque de fábrica (`boot.img`), y dar permiso de ejecución.
3. Ejecutar el parche por adb. No requiere root:

   ```
   adb shell "cd /data/local/tmp/mg && sh boot_patch.sh boot.img"
   ```

   Genera `new-boot.img` en la misma carpeta.
4. Traer `new-boot.img` a la computadora y escribirlo en la partición de arranque (`0x1d80000`) como se describe en la sección de flasheo. En este proyecto esa imagen se llama `raw/boot-magisk.img`.
5. Instalar el APK de Magisk en la tablet.

## Detalles

- La primera vez que `adb shell` pide `su`, Magisk muestra un diálogo de permiso. Los toques enviados con `adb shell input` no funcionan sobre ese diálogo: hay que tocarlo a mano y elegir conceder siempre.
- `herramientas/flash.sh` escribe el arranque de fábrica sin Magisk. Para recuperar el root hay que escribir después `raw/boot-magisk.img`.
- Los arranques `boot-p8080-v*.img` llevan el kernel propio con el ramdisk de Magisk, así que conservan el root.
- Con Android 7 no se instaló Magisk.

## Qué se leyó con root

Los archivos sin identificadores de la unidad están en `datos-hardware/`:

| Archivo | Contenido |
|---|---|
| `cmdline.txt` | Línea de arranque del kernel. De ahí sale el nombre del panel. |
| `i2c_devices.txt`, `i2c_names.txt` | Qué chip hay en cada bus y dirección, y qué controlador lo atiende. |
| `mtgpio_pin.txt` | Estado de los 143 pines. |
| `bateria_vivo.txt`, `battery_sysfs.txt` | Registros del cargador y datos de batería. |
| `emmc.txt`, `dumchar_info.txt`, `partitions.txt` | Particiones. |
| `platform_devices.txt`, `platform_drivers.txt`, `interrupts.txt`, `iomem.txt`, `input_devices.txt`, `cpuinfo.txt` | Resto del inventario. |

La tabla de símbolos del kernel (`/proc/kallsyms` con direcciones reales) no se publica por tamaño. Se obtiene con root después de escribir `0` en `/proc/sys/kernel/kptr_restrict`.
