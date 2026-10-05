# Problemas y soluciones

Fallos que ya ocurrieron, con la causa encontrada y el arreglo. Están en el orden en que aparecieron.

## Conexión

| Síntoma | Causa | Arreglo |
|---|---|---|
| mtkclient nunca completa el saludo por USB. | macOS toma el dispositivo antes que libusb. | Usar el puerto serie: `--serialport /dev/cu.usbmodemXXXXX`. |
| mtkclient reintenta el saludo para siempre con la tablet ya detenida. | Una tablet ya saludada solo hace eco de los bytes. | Parche de `Port.py`: si devuelve el mismo `0xA0`, dar el saludo por hecho. |
| El protocolo se desincroniza a media sesión. | El tiempo de espera de lectura de 20 ms no alcanza por puerto serie en macOS. | Parche de `seriallib.py`: mínimo de 1 segundo. |
| Cada comando nuevo después del primero se cuelga. | mtkclient intenta saludar otra vez a una tablet que ya tiene el agente de descarga cargado. | Parche de `mtk_da_handler.py`: reutilizar la sesión si existe `.state`. |
| mtkclient termina con "Please disconnect, start mtkclient and reconnect" sin más datos. | Sin modo de depuración falla en silencio. | Usar siempre `--debugmode`. |
| El registro crece a cientos de megabytes en un minuto. | El modo de depuración imprime cada byte. | Filtrar las líneas `TX:` y `RX:`, como hacen los scripts. |
| Los scripts fallan porque no existe `timeout`. | macOS no lo trae. | `perl -e 'alarm N; exec @ARGV' comando`. |
| El puerto no aparece con el nombre de siempre. | El número cambia entre conexiones (`11300`, `11301`). | Detectarlo con `ls /dev/cu.usbmodem*`. |
| La tablet no reinicia después de `mtk reset`. | Se queda esperando mientras tenga el cable. | Desconectar el cable y encender con el botón. |

## Escritura

| Síntoma | Causa | Arreglo |
|---|---|---|
| Las imágenes grandes del firmware no se pueden escribir tal cual. | Vienen en formato sparse de Android. | Convertirlas con `herramientas/simg2img.py`. |
| Leer `expdb` antes de restaurar el arranque dejó la sesión colgada. | Sin identificar. | Primero escribir el arranque bueno y después leer `expdb`. `restaurar_boot.sh` lo hace en ese orden. |
| `dumpsys battery` da dos porcentajes distintos. | Reporta una segunda batería que no existe, fija en 50 %. | Tomar el primer valor o leer `/sys/class/power_supply/battery/capacity`. |

## Kernel

| Síntoma | Causa | Arreglo |
|---|---|---|
| El primer volcado de Alcatel no compila. | A `PULS_20160108` le faltan ocho constantes de batería para `ttab`. | Partir del segundo volcado, `PULS_20180308` (commit `4b9e97964ec`). |
| La compilación muere al cerrar la sesión de ssh. | El contenedor corría en primer plano. | Lanzarlo con `docker run -d`. |
| `make O=...` falla de inmediato. | La carpeta de salida no existe. | Crearla antes. |
| No se puede descargar el compilador. | La referencia `nougat-release` no existe para `arm-eabi-4.8`. | Usar `lollipop-release`. |
| El primer kernel propio entra en bucle de arranque. | `mmc0: unrecognised EXT_CSD revision 8`, seguido de un `BUG` en `msdc_check_init_done`. La eMMC de la 8080 es 5.1 y el kernel solo acepta hasta la revisión 7. | Subir el límite a 8 en `drivers/mmc/core/mmc.c`. La rama de LineageOS tiene el mismo límite. |
| No se sabe por qué un kernel no arrancó. | No se usó consola serie. | Leer la partición `expdb`, que guarda el registro del último fallo grave. |
| La pantalla se apagaría al inicializar el HDMI. | GPIO27 alimenta el panel en la 8080 y es el control de alimentación del HDMI en la Puls. | Guardas en `hdmi_drv.c` cuando el panel es el de la 8080. Se detectó leyendo el código antes de probar. |
| El táctil no responde. | El kernel lo registraba en el bus I2C 0 y el chip está en el bus 1. | `I2C_BUS_NUMBER 1`. |
| Riesgo de dejar el táctil mal calibrado. | El controlador de la Puls reenvía al chip una configuración pensada para una pantalla de 8 pulgadas. | `GTP_DRIVER_SEND_CFG 0`: se conserva la configuración que el chip ya trae. |
| La pantalla sale girada 180° en Android 7. | La Puls declara el acelerómetro con `direction = 7`; el kernel de fábrica de la 8080 usa 6. | Cambiarlo en `cust_acc.c`. El valor se leyó del kernel de fábrica. |
| El táctil parece invertido en Android 5 con el kernel propio. | Probablemente lo mismo que el punto anterior: ni el kernel de fábrica ni el de la Puls transforman las coordenadas del táctil. Sin confirmar. | Ver el punto anterior. |
| No es posible reproducir el kernel de fábrica byte por byte. | Se compiló con una versión más nueva del sistema de pantalla de MediaTek: la estructura de parámetros del panel mide `0x2b4` bytes en el binario y `0x1dc` en el código disponible. | Ninguno. El objetivo pasó a ser un kernel funcional. |

## Android 7

| Síntoma | Causa | Arreglo |
|---|---|---|
| El fstab de la ROM monta `/misc` en `mmcblk0p3`. | En la 8080 esa partición es `protect_s`. | Retirar la línea con `herramientas/ramdisk_quitar_misc.py`. Se detectó comparando particiones antes de escribir. |
| No se puede autorizar adb sin pasar por el asistente inicial. | La depuración USB viene apagada. | Partición de datos con la llave de adb ya puesta, descrita en la sección de Android 7. |
| El diálogo de permiso de Magisk ignora los toques enviados por adb. | No se investigó. | Tocarlo a mano. |
