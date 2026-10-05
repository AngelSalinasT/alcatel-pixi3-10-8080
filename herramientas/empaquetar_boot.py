#!/usr/bin/env python3
"""Arma una imagen de arranque para la 8080 cambiando el kernel (y opcionalmente el ramdisk)
de una imagen existente. Conserva las cabeceras de MediaTek de 512 bytes (KERNEL / ROOTFS).

Uso:
  empaquetar_boot.py <boot_base.img> <zImage> <salida.img> [ramdisk.cpio.gz]

Ejemplos:
  empaquetar_boot.py raw/boot-magisk.img cmp/zImage_p8080_v3 raw/boot-p8080-v3.img
  empaquetar_boot.py los/x/boot.img los/x/zImage_los_p8080 raw/boot-los-p8080-v1.img los/x/ramdisk-p8080.cpio.gz
"""
import struct, hashlib, sys, gzip

base, zimage, salida = sys.argv[1:4]
ramdisk_nuevo = sys.argv[4] if len(sys.argv) > 4 else None
src = open(base, 'rb').read()
assert src[:8] == b'ANDROID!', "la base no es una imagen de arranque de Android"
ks, ka, rs, ra, ss, sa, ta, page = struct.unpack('<8I', src[8:40])
pad = lambda n: (n + page - 1) // page * page
kern = src[page:page + ks]
rd = src[page + pad(ks):page + pad(ks) + rs]
MTK = b'\x88\x16\x88\x58'
assert kern[:4] == MTK and rd[:4] == MTK, "la base no trae cabeceras de MediaTek"

z = open(zimage, 'rb').read()
kh = bytearray(kern[:512]); kh[4:8] = struct.pack('<I', len(z)); nk = bytes(kh) + z
if ramdisk_nuevo:
    g = open(ramdisk_nuevo, 'rb').read()
    rh = bytearray(rd[:512]); rh[4:8] = struct.pack('<I', len(g)); nr = bytes(rh) + g
else:
    nr = rd

h = bytearray(src[:page])
h[8:12] = struct.pack('<I', len(nk)); h[16:20] = struct.pack('<I', len(nr))
sha = hashlib.sha1()
for b in (nk, nr):
    sha.update(b); sha.update(struct.pack('<I', len(b)))
sha.update(struct.pack('<I', 0))
h[576:608] = sha.digest() + b'\0' * 12
out = bytes(h) + nk + b'\0' * (pad(len(nk)) - len(nk)) + nr + b'\0' * (pad(len(nr)) - len(nr))
open(salida, 'wb').write(out)

# verificación releyendo lo escrito
o = open(salida, 'rb').read()
k2s, _, r2s = struct.unpack('<III', o[8:20])
k2 = o[page:page + k2s]; r2 = o[page + pad(k2s):page + pad(k2s) + r2s]
ok_k = k2[512:] == z
ok_r = len(gzip.decompress(r2[512:])) > 0
print(f"{salida}: {len(o)} bytes | kernel idéntico al zImage: {ok_k} | ramdisk descomprime: {ok_r} | cabe en 16 MB: {len(o) <= 0x1000000}")
sys.exit(0 if ok_k and ok_r and len(o) <= 0x1000000 else 1)
