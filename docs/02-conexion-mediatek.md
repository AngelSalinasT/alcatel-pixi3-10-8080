# Conexión con la tablet por el preloader de MediaTek

Esta es la parte que más costó. Si la tablet no arranca Android, esta es la única vía de entrada.

## La idea

Cada vez que la tablet enciende, su preloader aparece por USB durante unos 3 segundos como "MT65xx Preloader" (fabricante `0x0e8d`, producto `0x2000`). Si en esa ventana se le hace el saludo del protocolo de MediaTek, deja de arrancar y se queda esperando órdenes. Desde ahí se carga un agente de descarga en memoria y se puede leer y escribir toda la eMMC.

En una tablet en bucle de arranque esa ventana se repite sola cada pocos segundos. En una tablet sana hay que provocarla reiniciando (`adb reboot`).

## Herramienta

Se usa mtkclient 2.1.4, instalado con:

```
uv tool install "git+https://github.com/bkerler/mtkclient" --python 3.12
```

El ejecutable queda en `~/.local/bin/mtk`.

### Parches obligatorios en mtkclient

En macOS mtkclient no funciona tal cual con esta tablet. Hay tres cambios aplicados sobre la instalación, con copia `.orig` junto a cada archivo original. Los parches están guardados en `herramientas/parches-mtkclient/`. Si se reinstala mtkclient hay que volver a aplicarlos.

| Archivo | Cambio | Por qué |
|---|---|---|
| `Library/Port.py` | Si la tablet devuelve el mismo byte `0xA0` en vez de su complemento, se da el saludo por hecho. | Cuando la tablet ya fue saludada solo hace eco de los comandos, y mtkclient se quedaba reintentando para siempre. |
| `Library/Connection/seriallib.py` | El tiempo mínimo de espera de lectura sube de 20 ms a 1 s. | Con 20 ms la respuesta no llegaba a tiempo en macOS y el protocolo se desincronizaba. |
| `Library/DA/mtk_da_handler.py` | Por puerto serie, si existe el archivo `.state`, se reutiliza la sesión ya cargada. | Sin esto cada comando nuevo intentaba saludar otra vez a una tablet que ya estaba en modo descarga y se colgaba. |

## Reglas que hay que respetar

1. **Usar el puerto serie, no libusb.** macOS toma el dispositivo antes que libusb y el saludo falla siempre. Hay que pasar `--serialport /dev/cu.usbmodemXXXXX`.
2. **Detectar el nombre del puerto cada vez.** Normalmente es `/dev/cu.usbmodem11300`, pero ha cambiado a `11301`. Usar `ls /dev/cu.usbmodem*`.
3. **Usar siempre `--debugmode`.** Sin esa opción mtkclient falla en silencio con el mensaje "Please disconnect, start mtkclient and reconnect".
4. **Filtrar la salida.** En modo depuración imprime cada byte; sin filtrar, un registro llegó a 720 MB en un minuto. Los scripts filtran las líneas `TX:`, `RX:` y similares.
5. **No dejar procesos de mtkclient vivos.** Dos procesos peleándose por el puerto producen respuestas sin sentido. Antes de empezar: `pgrep -fl "bin/mtk"`.
6. **macOS no trae el comando `timeout`.** Para poner tope de tiempo se usa `perl -e 'alarm N; exec @ARGV' comando`.
7. **Trabajar desde la carpeta del proyecto.** mtkclient guarda ahí el archivo `.state` que permite encadenar comandos. Al terminar una sesión hay que borrarlo.

## Procedimiento

### 1. Atrapar la tablet

```
~/.local/share/uv/tools/mtkclient/bin/python herramientas/pl_catch.py
```

El script espera a que aparezca el puerto, hace el saludo (`A0`, `0A`, `50`, `05`, esperando el complemento de cada byte) y pide el código del chip. Cuando imprime `ENGANCHADA ... HW_CODE=fd81270000` la tablet quedó detenida en modo comandos. El `8127` de esa respuesta es el procesador.

El tiempo de espera está en la segunda línea del script (`end = time.time() + N`).

Si la tablet tiene Android corriendo, se lanza el script en segundo plano y luego `adb reboot`.

### 2. Mandar comandos

Con la tablet atrapada, todos los comandos van con el mismo formato:

```
mtk <comando> --serialport /dev/cu.usbmodem11300 --debugmode
```

El primero carga el agente de descarga (tarda unos segundos más) y crea `.state`. Los siguientes reutilizan la sesión.

| Comando | Qué hace |
|---|---|
| `ro <inicio> <longitud> <archivo>` | Lee de la eMMC a un archivo. |
| `wo <inicio> <longitud> <archivo>` | Escribe un archivo en la eMMC. |
| `printgpt` | Muestra la tabla de particiones. |
| `reset` | Termina la sesión. |

Inicio y longitud van en hexadecimal. Las direcciones de cada partición están en la sección de flasheo.

### 3. Soltar la tablet

Después de `reset` la tablet no reinicia sola. Hay que desconectar el cable USB y encenderla con el botón.

## Cuando la tablet queda trabada en modo descarga

Pasa si un comando falla a medias. Síntomas: el puerto sigue presente pero nada contesta, o los comandos se cuelgan.

1. Cerrar todo proceso de mtkclient.
2. Desconectar el cable.
3. Mantener Encendido unos 15 segundos. Si no reacciona, Encendido más Subir volumen.
4. Reconectar y volver a atrapar.

## Comprobar a mano que la tablet contesta

`herramientas/pl_cmd.py` manda comandos sueltos del protocolo y muestra las respuestas. Con la tablet ya saludada, el comando `0xFD` debe devolver `fd 8127 0000`. Sirve para saber si el problema es de la tablet o de mtkclient.
