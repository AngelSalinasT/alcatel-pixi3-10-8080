#!/usr/bin/env python3
"""Edita un ramdisk cpio (formato newc) sin extraerlo, para conservar dueños y permisos.
Retira del fstab la línea que monta /misc en mmcblk0p3: en la Puls esa partición es misc,
en la 8080 es protect_s y no debe escribirse.

Uso: ramdisk_quitar_misc.py <ramdisk.cpio> <salida.cpio.gz> [nombre_del_fstab]
"""
import sys, gzip
src = open(sys.argv[1], 'rb').read(); salida = sys.argv[2]
fstab = sys.argv[3] if len(sys.argv) > 3 else 'fstab.mt8127'
pad4 = lambda b: b + b'\0' * ((4 - len(b) % 4) % 4)
out = bytearray(); p = 0; n = 0; retirada = None
while p < len(src):
    h = src[p:p + 110]; assert h[:6] == b'070701', "no es cpio newc"
    f = [int(h[6 + i * 8:14 + i * 8], 16) for i in range(13)]
    fsize, nsize = f[6], f[11]
    name = src[p + 110:p + 110 + nsize]; q = p + 110 + nsize; q += (4 - q % 4) % 4
    data = src[q:q + fsize]; nxt = q + fsize; nxt += (4 - nxt % 4) % 4
    nm = name.rstrip(b'\0').decode()
    if nm == fstab:
        nuevas = []
        for l in data.decode().split('\n'):
            if 'mmcblk0p3' in l and '/misc' in l:
                retirada = l; nuevas.append('# p8080: mmcblk0p3 es protect_s en la Pixi 3 (10); linea retirada')
            else:
                nuevas.append(l)
        data = '\n'.join(nuevas).encode(); f[6] = len(data)
    out += pad4(b'070701' + b''.join(b'%08X' % x for x in f) + name) + pad4(data); n += 1; p = nxt
    if nm == 'TRAILER!!!': break
out += b'\0' * ((512 - len(out) % 512) % 512)
open(salida, 'wb').write(gzip.compress(bytes(out), 9))
print(f"{n} entradas; línea retirada: {(retirada or 'NINGUNA').strip()}")
