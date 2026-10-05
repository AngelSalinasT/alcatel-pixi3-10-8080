# Kernel propio

## Por qué hizo falta

Alcatel nunca publicó el código del kernel de la 8080. Sin código no se puede adaptar el kernel a un Android más nuevo. Lo que sí existe es el código de una tablet hermana, la Telekom Puls (nombre interno `ttab`), fabricada por Alcatel sobre la misma plataforma. El firmware de la 8080 llama a su cargador `preloader_ttab.bin`, lo que confirma el parentesco.

El kernel propio es el código de la Puls más las piezas de la 8080 obtenidas por ingeniería inversa.

## Dónde está el código

En la máquina Linux donde se compila, carpeta `~/alcatel-8080/`:

| Ruta | Contenido |
|---|---|
| `kernel/` | Clon de `github.com/mt8127/android_kernel_alcatel_ttab`. |
| `stock/` | Árbol de trabajo sobre el código original de Alcatel. Rama local `p8080`. |
| `los/` | Árbol de trabajo sobre el kernel de LineageOS. Rama local `p8080-los`. |
| `toolchain/` | Compilador `arm-eabi-4.8` de AOSP. |
| `out-stock/`, `out-p8080/`, `out-los/` | Resultados de compilación. |
| `build.sh` | Script de compilación dentro del contenedor. |

Los cambios están publicados como parches en `kernel/` de este repositorio, junto con las configuraciones y el script de compilación. Con el repositorio público de la Puls y esos parches se reconstruye todo. Se comprobó aplicando cada serie sobre su commit base: el árbol resultante es idéntico al de la rama de trabajo.

```
git clone https://github.com/mt8127/android_kernel_alcatel_ttab kernel
cd kernel

# base de Alcatel, para Android 5
git worktree add ../stock 4b9e97964ec
git -C ../stock checkout -b p8080
git -C ../stock am ../ruta/a/kernel/parches-base-alcatel/*.patch

# base de LineageOS, para Android 7
git worktree add ../los 557d9dfd700
git -C ../los checkout -b p8080-los
git -C ../los am ../ruta/a/kernel/parches-base-lineageos/*.patch
```

## Las dos bases

| | `stock` (rama `p8080`) | `los` (rama `p8080-los`) |
|---|---|---|
| Punto de partida | Commit `4b9e97964ec`, "import PULS_20180308" | `origin/cm-14.1`, commit `557d9dfd700` |
| Versión | Linux 3.10.54 | Linux 3.10.108 |
| Sirve para | Android 5 de fábrica | Android 7 (LineageOS 14.1) |
| Configuración | `p8080_defconfig` | `p8080_defconfig` |

El primer volcado de Alcatel (`6fa3eb70c07`, "import PULS_20160108") no compila: le faltan ocho constantes de batería. Hay que partir del segundo.

## Cambios respecto a la Puls

Son los mismos en las dos ramas.

1. **Panel.** Nuevo controlador en `drivers/misc/mediatek/lcm/rm68200_txd_wxga_pixi3/`, registrado en `mt65xx_lcm_list.c`. La configuración pone `CONFIG_CUSTOM_KERNEL_LCM="rm68200_txd_wxga_pixi3"`.
2. **Cargador.** `CONFIG_MTK_BQ24158_SUPPORT=y` en lugar de `CONFIG_MTK_FAN5405_SUPPORT`. El controlador ya venía en el código.
3. **Protección de GPIO27.** En `drivers/misc/mediatek/hdmi/internal_hdmi/mt8127/hdmi_drv.c`, las dos guardas `#ifdef GPIO_HDMI_POWER_CONTROL` se desactivan cuando está definido `RM68200_TXD_WXGA_PIXI3`. Sin esto el HDMI apagaría la alimentación de la pantalla.
4. **eMMC 5.1.** En `drivers/mmc/core/mmc.c`, línea 303, el límite de revisión de EXT_CSD pasa de 7 a 8. Sin esto el kernel no inicializa el almacenamiento y entra en bucle. La rama de LineageOS tenía el mismo límite.
5. **Táctil.** En `arch/arm/mach-mt8127/ttab/touchpanel/tpd_custom_gt9xx.h`: `I2C_BUS_NUMBER` pasa de 0 a 1, y `GTP_DRIVER_SEND_CFG` pasa de 1 a 0 para que el kernel no sobrescriba la configuración que el chip ya trae para la pantalla de 10 pulgadas.
6. **Acelerómetro.** En `arch/arm/mach-mt8127/ttab/accelerometer/cust_acc.c`, `direction` pasa de 7 a 6, que es el valor leído del kernel de fábrica de la 8080. Con 7 la pantalla sale girada 180°.

El proyecto sigue llamándose `ttab` (`CONFIG_ARCH_MTK_PROJECT="ttab"`): se usan los archivos de placa de la Puls, incluida su tabla de pines y su curva de batería.

En el repositorio hay una configuración y una carpeta llamadas `pixi3_10`. No corresponden a esta tablet: declaran un panel LVDS de 7 pulgadas y una batería de 4.2 V. No usarlas.

## Compilar

Dentro de un contenedor Ubuntu 16.04, porque un sistema moderno no compila bien un kernel de 2015:

```
cd ~/alcatel-8080
docker rm -f k8080
docker run -d --name k8080 -v ~/alcatel-8080:/work ubuntu:16.04 bash -c "
  (apt-get update -qq && apt-get install -y -qq build-essential bc git python perl wget ca-certificates lzop xz-utils libc6-i386 lib32stdc++6 lib32z1) > /work/apt.log 2>&1
  export PATH=/work/toolchain/bin:\$PATH ARCH=arm CROSS_COMPILE=arm-eabi-
  mkdir -p /work/out-los
  cd /work/los && make O=/work/out-los p8080_defconfig > /work/build-los.log 2>&1 && make O=/work/out-los -j4 zImage >> /work/build-los.log 2>&1
  echo FIN_BUILD rc=\$? >> /work/build-los.log"
```

Para la base de Alcatel se cambia `los` por `stock` y `out-los` por `out-p8080`.

Detalles que ya causaron fallos:

- El contenedor va con `-d`. Sin eso muere al cerrar la sesión de ssh.
- La carpeta de salida debe existir antes de `make O=`.
- El compilador se baja de `android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8/+archive/refs/heads/lollipop-release.tar.gz`. La referencia `nougat-release` no existe.
- Los archivos que crea el contenedor son de root. Para borrarlos hay que hacerlo desde otro contenedor.
- Si el shell es zsh, los patrones con asterisco van entre comillas.

Una compilación completa tarda unos 15 minutos con 4 núcleos; una incremental, uno o dos.

El resultado es `out-*/arch/arm/boot/zImage`. Para comprobar que trae lo esperado:

```
strings out-los/arch/arm/boot/Image | grep -E "Linux version|rm68200_txd_wxga_pixi3"
```

## Empaquetar en una imagen de arranque

El formato es una imagen de arranque de Android con una cabecera extra de MediaTek de 512 bytes delante del kernel (nombre `KERNEL`) y otra delante del ramdisk (nombre `ROOTFS`). Cada cabecera lleva el tamaño de lo que sigue.

Para cambiar solo el kernel de una imagen existente:

1. Leer de la cabecera el tamaño del kernel, el del ramdisk y el tamaño de página (2048).
2. Copiar la cabecera MediaTek del kernel original, poner el tamaño nuevo y pegarle el `zImage`.
3. Actualizar el tamaño del kernel en la cabecera de Android.
4. Rearmar: cabecera, kernel alineado a página, ramdisk alineado a página.

Lo hace `herramientas/empaquetar_boot.py`, que además verifica el resultado releyéndolo:

```
herramientas/empaquetar_boot.py raw/boot-magisk.img cmp/zImage_p8080_v3 raw/boot-p8080-v3.img
```

Con un cuarto argumento sustituye también el ramdisk. Se comprobó que reproduce byte por byte las imágenes de `raw/`.

## Versiones y resultados

| Imagen | Base | Resultado |
|---|---|---|
| `boot-p8080-v1.img` | Alcatel 3.10.54 | Bucle de arranque: no reconocía la eMMC 5.1. |
| `boot-p8080-v2.img` | Alcatel 3.10.54 | Arranca Android 5. Pantalla, almacenamiento, carga, WiFi, gráficos y acelerómetro funcionan. Táctil sin respuesta (bus equivocado). |
| `boot-p8080-v3.img` | Alcatel 3.10.54 | Como la anterior, con táctil funcionando pero con la orientación invertida. Audio comprobado a mano. No detecta cámaras. |
| `boot-los-p8080-v1.img` | LineageOS 3.10.108 | Arranca Android 7 completo. Pantalla girada 180°. |
| `boot-los-p8080-v2.img` | LineageOS 3.10.108 | Como la anterior, con la orientación del acelerómetro corregida. Escrita y verificada por relectura; falta confirmar la rotación en uso. |

## Diferencia con el kernel de fábrica

El kernel de fábrica de la 8080 se compiló con un sistema de pantalla de MediaTek más nuevo que el del código de la Puls. Se midió con el compilador: la estructura de parámetros del panel ocupa `0x2b4` bytes en el kernel de fábrica y `0x1dc` en el código. También acepta eMMC 5.1 sin parche. Por eso no es posible reproducir el kernel de fábrica byte por byte; el objetivo es un kernel funcional.

## Pendientes

- Confirmar que con la orientación del acelerómetro corregida el táctil ya coincide con la imagen. Si no, el controlador tiene las opciones `TPD_WARP_X` y `TPD_WARP_Y` en `tpd_custom_gt9xx.h`.
- Cámaras: identificar los sensores de imagen de la 8080. La Puls usa `ov2680`, `gc2355` y `ov5670`. Con la base de Alcatel no se detecta ninguna; con la de LineageOS se detecta una, sin probar.
- Sustituir la curva de batería de la Puls por la extraída de la tablet.
- Revisar los siete pines con función distinta.
- El gobernador de procesador deja uno o dos núcleos activos en reposo, igual que el de fábrica.
