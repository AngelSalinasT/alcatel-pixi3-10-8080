# Fuentes y búsquedas

Dónde está cada cosa y qué caminos ya se recorrieron sin resultado, para no repetirlos. Todo se revisó el 4 de octubre de 2026.

## Lo que sí existe

| Qué | Dónde | Notas |
|---|---|---|
| Firmware de fábrica de la 8080 | `Alcatel_OneTouch_Pixi_3_8080_2CALBR6_20171127_SMTK.zip`, en alcatelfirmware.com y firmwarefile.com | 925 MB, formato Sugar MTK, versión vECF-0, Android 5.0.1. SHA-256 `f5b0851ca6d4c7805c1bfefeaf09b64976141d3f835962e8cae45d0bada6dcc3`. |
| Código del kernel de la Telekom Puls | github.com/mt8127/android_kernel_alcatel_ttab | Trae los dos volcados originales de Alcatel y las ramas de LineageOS. Sin actividad desde febrero de 2019. |
| ROM LineageOS 14.1 de la Puls | Carpeta compartida enlazada en el hilo de la Telekom Puls en android-hilfe.de, página 21 | Trae también Android 9 y TWRP para la Puls. El servidor original de compilaciones, `lineage.stricted.net`, ya no responde. |
| mtkclient | github.com/bkerler/mtkclient | Versión 2.1.4, con los tres parches de `herramientas/parches-mtkclient/`. |
| Compilador | `android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8`, referencia `lollipop-release` | La referencia `nougat-release` no existe. |
| Magisk 25.2 | github.com/topjohnwu/Magisk, sección de versiones | |
| Datos regulatorios | fccid.io, FCC ID `2ACCJB024` | Modelo interno B024, TCL, agosto de 2015. |

## El código del kernel de la 8080 no existe públicamente

Alcatel publicaba su código en SourceForge. Hoy esa página no lista la 8080 ni sus variantes (8079, 8070).

- El historial de la página en Wayback Machine muestra que hubo paquetes de tablets hermanas: `OT_9010_2016523.tar.xz`, `OT_9005_20160524`, `OT_9002_20160524`, `9007_20160216`, `9022_20160216`, `OT_Pixi3_20150507`, `OT_8063_20170412`, `PULS_20160108` y `PULS_20180308`.
- Comprobado con navegador: SourceForge borró esos archivos. Pedir uno redirige al listado.
- Wayback Machine solo guardó las redirecciones, no los archivos.
- No se encontraron copias en archive.org ni importaciones en GitHub.
- La 9010X, que por nombre parecía la más cercana (Pixi 3 (10) 3G), usa MT6580 y no MT8127. Aunque apareciera su código, no serviría.
- En el hilo de la Pixi 3 en XDA, de 167 páginas, al menos dos personas cuentan que pidieron el código a Alcatel y recibieron una negativa "por restricciones internas" (2019 y febrero de 2025). Otra persona buscaba los mismos paquetes borrados en enero de 2025.

Conclusión: el único camino práctico es el de este repositorio, que parte del código de la Puls y reconstruye lo que falta.

Queda una vía sin intentar: abrir una solicitud de código GPL en github.com/TCLOpenSource/TCL_Kernel_OpenSource.

## Otros proyectos relacionados

| Proyecto | Qué es | Utilidad |
|---|---|---|
| github.com/mt8127 | Organización con kernel, árbol de dispositivo y ROM de la Puls: LineageOS 14.1, 15.1 y 16.0 | Es la base de todo. Su kernel no trae los paneles de la 8080. |
| `pixi3_10_defconfig` dentro de ese kernel | Configuración con el nombre de esta tablet | No sirve: declara un panel LVDS de 7 pulgadas y una batería de 4.2 V. |
| github.com/kirito96/android_device_alcatel_Pixi3_10_Wifi | Árbol de dispositivo para CyanogenMod con el kernel de fábrica precompilado, de 2018 | Sin versiones publicadas. No se probó. |
| github.com/andrew264/android_kernel_lenovo_mt8127 | Kernel 3.10.54 de otra tablet MT8127 | Posible referencia para controladores que falten. No se usó. |

## Notas sobre cómo buscar

- SourceForge responde con error 403 a las descargas automáticas. Hay que comprobarlo con un navegador real.
- XDA y Reddit tampoco cargan bien sin navegador real. El buscador interno de XDA pide iniciar sesión.
- Para encontrar el nombre de compilación de una tablet MediaTek sirven las cadenas del kernel de fábrica: en la 8080 aparece `Pixi310_Wifi_Global_Release`, y el firmware llama a su cargador `preloader_ttab.bin`. Esa segunda cadena es la que delata el parentesco con la Puls.
