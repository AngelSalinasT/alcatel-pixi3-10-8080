# Alcatel Pixi 3 (10) WiFi 8080: unbrick, custom kernel and Android 7

Notes, tools and kernel patches for the **Alcatel OneTouch Pixi 3 (10) WiFi, model 8080** (MediaTek MT8127, 1 GB RAM, 16 GB eMMC, shipped with Android 5.0.1).

Alcatel never released the kernel source for this tablet, and there is no custom ROM for it. This repository gets it to boot **LineageOS 14.1 (Android 7.1.2)** by taking the kernel of its sibling, the Telekom Puls (`ttab`), and adding the pieces the 8080 needs. The display driver was rebuilt by disassembling the stock kernel.

It started as a rescue: the tablet was stuck in a boot loop after a failed ROM attempt.

The detailed documentation is in Spanish, in [`docs/`](docs/README.md). This page is the English summary.

## Status

One unit tested. State as of 2026-10-05.

| Feature | Android 7 (LineageOS 14.1, kernel 3.10.108) | Notes |
|---|---|---|
| Boot to launcher | Works | |
| Display, 800×1280 | Works | Reconstructed `rm68200_txd_wxga_pixi3` panel driver |
| Touch (Goodix GT9xx) | Works | |
| WiFi | Works | |
| Internal storage (eMMC 5.1) | Works | Needs the EXT_CSD patch |
| adb | Works | |
| Rotation | Fix flashed, not confirmed yet | First build showed the screen rotated 180° |
| Camera | One camera detected, not tested | |
| Audio | Not tested on Android 7 | Works with the same patches on the Android 5 kernel |
| Charging (BQ24158) | Not measured on Android 7 | Works with the same patches on the Android 5 kernel |
| Battery percentage | Probably inaccurate | Still uses the Puls battery curve |
| Bluetooth, GPS, SD card, HDMI, headphone jack | Not tested | |

The system identifies itself as a Telekom Puls, because the ROM is the unmodified Puls build. There is no device tree for the 8080 yet.

## What is here

| Path | Contents |
|---|---|
| [`docs/`](docs/README.md) | Full write-up (Spanish): connection, partition map, flashing, hardware, kernel, Android 7, root, sources, problems and fixes. |
| `kernel/parches-base-alcatel/` | Patch series on top of Alcatel's original Puls source (Linux 3.10.54), for the stock Android 5. |
| `kernel/parches-base-lineageos/` | Same changes on top of the LineageOS `cm-14.1` kernel (Linux 3.10.108), for Android 7. |
| `kernel/build.sh` | Build script, meant to run inside an Ubuntu 16.04 container. |
| `reconstruido/` | Reverse-engineered pieces: the panel driver and the battery voltage curve read from the device. |
| `herramientas/` | Scripts: catch the preloader, flash, restore, repack MediaTek boot images, convert sparse and block-based images, locate and disassemble the panel driver in the stock kernel. |
| `herramientas/parches-mtkclient/` | Three small patches that make mtkclient work with this tablet over a serial port on macOS. |
| `datos-hardware/` | Hardware data read from the running stock kernel: I2C devices, GPIO state, partitions, charger registers. Serial number redacted. |

No firmware, ROM or kernel binaries are included. The docs say where to get each one, with SHA-256 hashes.

## Kernel changes

Both series apply cleanly on these commits of [mt8127/android_kernel_alcatel_ttab](https://github.com/mt8127/android_kernel_alcatel_ttab):

| Series | Base commit | Kernel |
|---|---|---|
| `parches-base-alcatel` | `4b9e97964ec` ("import PULS_20180308") | 3.10.54 |
| `parches-base-lineageos` | `557d9dfd700` (`cm-14.1`) | 3.10.108 |

```
git clone https://github.com/mt8127/android_kernel_alcatel_ttab
cd android_kernel_alcatel_ttab
git checkout -b p8080-los 557d9dfd700
git am /path/to/kernel/parches-base-lineageos/*.patch
```

What they change, compared with the Puls:

1. **Panel.** New LCM driver `rm68200_txd_wxga_pixi3`: DSI burst video mode, 4 lanes, RGB888, PLL 224 MHz. Timings, init sequence and GPIOs were recovered from the stock kernel binary.
2. **Charger.** BQ24158 instead of FAN5405. The driver was already in the tree.
3. **GPIO27.** On the Puls it is the HDMI power control. On the 8080 it powers the panel, so the HDMI driver must not touch it.
4. **eMMC 5.1.** The kernel rejected EXT_CSD revision 8 and hit a `BUG` during boot. The limit goes from 7 to 8.
5. **Touch.** The GT9xx is on I2C bus 1, not 0, and the driver no longer overwrites the configuration stored in the chip.
6. **Accelerometer.** `direction` 6 instead of 7, the value used by the stock kernel.

The board files, pin table and battery curve are still the Puls ones.

## Talking to the tablet

The tablet has no boot protection (SBC, SLA and DAA are all off), so [mtkclient](https://github.com/bkerler/mtkclient) can read and write the whole eMMC through the preloader. On macOS it only worked over the serial port, with the three patches in `herramientas/parches-mtkclient/` and with `--debugmode`. The preloader window lasts about 3 seconds; `herramientas/pl_catch.py` does the handshake and leaves the tablet waiting for commands.

Everything was done from a Mac. The scripts use macOS paths and tools (`/dev/cu.usbmodem*`, `stat -f`), so they need small changes on Linux.

## Before you flash anything

- Never write the preloader. While it is intact the tablet can always be recovered.
- Do not write `pro_info` or `nvram`. They hold the identity and calibration of your unit. Back them up first.
- Check your panel. The stock kernel supports four panels for this model (`otm1287a_txd`, `otm1287a_tdt`, `rm68200_txd`, `rm68200_yeji`). This work covers only `rm68200_txd`. With root on stock, `cat /proc/cmdline` shows `lcm=1-<panel name>`.
- Check your touch controller too. The stock kernel also declares a FocalTech (`fts`) touch device at I2C `1-0038`; this unit has a Goodix GT9xx at `1-005d`.
- You do this at your own risk.

## Known gaps

- The kernel source for the 8080 was searched for and is not available anywhere; `docs/08-fuentes-y-busquedas.md` lists what was checked. If you have a copy of the Alcatel tarballs that were removed from SourceForge, please open an issue.
- Battery curve and pin table still come from the Puls. Seven pins differ in function (GPIO101 to GPIO106 and GPIO119).
- Camera sensors are not identified.
- Two fields of the panel parameters that the stock kernel sets to 1 could not be identified. The panel works without them.

## Credits

- The [mt8127](https://github.com/mt8127) project, for the Telekom Puls kernel and LineageOS port this is built on.
- [bkerler/mtkclient](https://github.com/bkerler/mtkclient).
- The Telekom Puls thread on android-hilfe.de, where the last LineageOS 14.1 build is still mirrored.

Done by Angel Salinas, working with Claude Code (Anthropic's AI coding assistant) for the reverse engineering, the scripts and this write-up.

## License

- `kernel/` and `reconstruido/`: GPL-2.0, like the Linux kernel they derive from. See `kernel/COPYING`.
- `herramientas/parches-mtkclient/`: GPL-3.0, like mtkclient.
- Everything else: MIT. See `LICENSE`.
