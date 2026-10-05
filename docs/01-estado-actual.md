# Estado actual

Al 5 de octubre de 2026.

## Qué tiene instalado la tablet

| Partición | Contenido |
|---|---|
| preloader, pro_info, nvram | Los de fábrica, sin tocar. |
| LK, logo, TEE, sec_ro | Firmware de fábrica vECF-0. |
| boot | `boot-los-p8080-v2.img`: kernel Linux 3.10.108 de LineageOS con los parches de este repositorio, más el arranque de la ROM con una línea del fstab retirada. |
| system | LineageOS 14.1 (Android 7.1.2), compilación no oficial del 15 de septiembre de 2022 para la Telekom Puls. |
| userdata | Vacía, con la depuración USB preautorizada. |
| custpack | La de fábrica. Android 7 no la usa. |

La escritura del arranque se verificó releyendo la partición y comparándola byte por byte con la imagen.

Android se identifica como `lineage_ttab` / `Telekom_Puls`, porque el sistema es el de la Puls sin modificar.

## Qué funciona

Comprobado con Android 7 y el kernel propio:

- Arranca hasta el escritorio y el uso general se siente fluido.
- Pantalla a 800×1280 con el controlador de panel reconstruido.
- Táctil.
- WiFi.
- Almacenamiento interno (eMMC 5.1).
- adb.
- El sistema detecta una cámara.

Comprobado con el mismo conjunto de cambios sobre el kernel de Alcatel y Android 5:

- Audio.
- Carga por USB con el BQ24158, a unos 670 mA.
- Acelerómetro.
- Gráficos Mali-450, a unos 55 cuadros por segundo, igual que con el kernel de fábrica.

## Qué falta confirmar

- Que la rotación quedó bien con la segunda versión del arranque. La primera mostraba la pantalla girada 180°; la causa se encontró en la orientación del acelerómetro y se corrigió, pero no se ha confirmado en uso.
- Audio en Android 7.
- Que la cámara tome fotos. Solo se sabe que el sistema la lista.
- Bluetooth, GPS, tarjeta SD, HDMI y salida de audífonos: sin probar.
- Comportamiento en reposo y consumo de batería.

## Qué se sabe que está mal o incompleto

- La curva de batería es la de la Puls. La de la 8080 ya está extraída (`reconstruido/battery_profile_8080.json`) pero no se integró al kernel. El porcentaje puede no ser exacto.
- La tabla de pines es la de la Puls. Siete pines tienen una función distinta en la 8080 (GPIO101 a GPIO106 y GPIO119) y no se ha revisado qué son.
- Con el kernel de base Alcatel (Android 5) no se detecta ninguna cámara.
- El dispositivo se anuncia como Telekom Puls. No hay árbol de dispositivo propio para la 8080.
- El controlador del panel deja sin establecer dos campos que el kernel de fábrica pone en 1. El panel funciona sin ellos.

## Cómo volver atrás

- Al Android 5 de fábrica: `herramientas/flash.sh`. Unos 12 minutos de escritura y de 10 a 15 de primer arranque.
- Solo el arranque, si un kernel nuevo no enciende: escribir `raw/boot-los-p8080-v2.img` en `0x1d80000`.

El detalle de cada caso está en la sección de flasheo y recuperación.
