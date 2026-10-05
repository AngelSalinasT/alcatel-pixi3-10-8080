# Hardware de esta unidad

Solo se listan datos comprobados, con el origen de cada uno. Lo que no se pudo confirmar va al final.

## Identificación

| Dato | Valor | Origen |
|---|---|---|
| Modelo | Alcatel OneTouch Pixi 3 (10) WiFi, 8080 | `ro.product.model` y etiqueta trasera |
| Referencia comercial | 8080-2BOFMX1 (México) | Partición pro_info y etiqueta |
| FCC ID | 2ACCJB024 (modelo interno B024, TCL, agosto de 2015) | fccid.io |
| Número de serie | (omitido) | pro_info y adb |
| MAC de WiFi | (omitida) | `/sys/class/net/wlan0/address` |
| Nombre de compilación de fábrica | `Pixi310_Wifi_Global_Release` | Cadenas del kernel de fábrica |
| Nombre de dispositivo | `Pixi3-10_WiFi` | adb |

## Componentes

| Componente | Lo que tiene | Origen |
|---|---|---|
| Procesador | MediaTek MT8127, cuatro núcleos a 1.3 GHz | Código `0x8127` del preloader |
| RAM | 1 GB (996 MB visibles) | `/proc/meminfo` |
| Almacenamiento | eMMC 5.1 de 16 GB (EXT_CSD revisión 8) | Agente de descarga y registro de fallo del kernel |
| Gráficos | Mali-450 MP, OpenGL ES 2.0 | SurfaceFlinger |
| Pantalla | 800×1280, panel `rm68200_txd_wxga_pixi3` | Línea de arranque del kernel: `lcm=1-rm68200_txd_wxga_pixi3` |
| Táctil | Goodix GT9xx en el bus I2C 1, dirección 0x5d | Controlador enlazado en `1-005d` |
| Cargador | BQ24158 en el bus I2C 1, dirección 0x6a | Controlador enlazado en `1-006a` |
| Acelerómetro | Bosch BMA2xx en el bus I2C 2, dirección 0x18 | Controlador enlazado en `2-0018` |
| Enfoque de cámara | FM50AF en el bus I2C 0, dirección 0x18 | Controlador enlazado |
| PMIC | MT6323 | Nombres de regulador en el kernel |
| Batería | 4060 mAh a temperatura normal, 3400 mAh en frío, química de 4.35 V | Desensamblado de `fgauge_get_Q_max` y tablas de voltaje |

El kernel de fábrica soporta cuatro paneles: `otm1287a_txd`, `otm1287a_tdt`, `rm68200_txd` y `rm68200_yeji`, todos con sufijo `_wxga_pixi3`. Esta unidad usa el `rm68200_txd`. Otra unidad del mismo modelo podría traer otro.

## Pantalla en detalle

Valores extraídos del desensamblado del kernel de fábrica. El controlador reconstruido está en `reconstruido/rm68200_txd_wxga_pixi3.c`.

| Parámetro | Valor |
|---|---|
| Interfaz | DSI, modo video en ráfaga, 4 carriles, RGB888 |
| Vertical: sync, back porch, front porch | 4, 8, 8 |
| Horizontal: sync, back porch, front porch | 4, 132, 24 |
| Reloj PLL | 224 MHz |
| Refresco medido | unos 55 cuadros por segundo |

Pines: GPIO27 y GPIO26 habilitan la alimentación del panel y GPIO83 es el reset. En la Telekom Puls GPIO27 es el control de alimentación del HDMI, de ahí el conflicto descrito en la sección del kernel.

Secuencia de encendido: GPIO27 arriba, 5 ms; GPIO26 arriba, 5 ms; reset arriba 5 ms, abajo 10 ms, arriba 20 ms; comandos `FE 0E`, `01 63`, `FE 00`, `11`; espera de 34 ms; `29`; espera de 180 ms.

## Carga

Registros del BQ24158 leídos con la tablet cargando por USB: `[0]=0xd0 [1]=0xf8 [2]=0xae [3]=0x51 [4]=0x0a [5]=0x03 [6]=0x78`.

- Voltaje final: 4.36 V.
- Corriente por USB: 550 mA.
- Tope de seguridad: 1250 mA.

La inicialización del kernel de fábrica escribe `reg6=0x77`, `reg1=0xB8`, `reg0=0xC0`, `reg5=0x03`, `reg4=0x1A`. El controlador `charging_hw_bq24158.c` del código de Alcatel escribe exactamente lo mismo.

La curva de voltaje contra porcentaje extraída de la tablet está en `reconstruido/battery_profile_8080.json` (copia en `datos-hardware/`): cuatro tablas de 101 puntos, idénticas entre sí, con máximo de 4332 mV.

## Táctil

Alimentación: regulador VGP2 del PMIC a 2.8 V, comprobado desensamblando `tpd_i2c_probe` del kernel de fábrica. Reset en GPIO25, interrupción en GPIO30.

## Pines

El estado de los pines leído del kernel de fábrica en ejecución está en `datos-hardware/mtgpio_pin.txt`. El formato de cada línea es `pin: modo, sentido de la resistencia, entrada, salida, resistencia activa, dirección, IES`.

Comparado con la tabla de arranque de la Telekom Puls (`cust_gpio_boot.h`, que genera la herramienta DrvGen del código de la Puls): 103 de 132 pines son idénticos, 22 difieren solo en dirección o resistencia, y 7 difieren en función (GPIO101 a GPIO106 y GPIO119).

## Sin confirmar

- Qué hacen GPIO101 a GPIO106 y GPIO119. La sospecha es que son las líneas de la tarjeta SD.
- Los sensores de imagen de las cámaras. Con el kernel propio no se detecta ninguna.
- Dos campos de la estructura del panel que el kernel de fábrica pone en 1 y que no se pudieron identificar. El panel funciona sin establecerlos.
- Si el táctil "invertido" que se vio con el kernel propio sobre Android 5 era en realidad la pantalla girada 180° por la orientación del acelerómetro (ya corregida). Es la hipótesis más probable, sin comprobar.
