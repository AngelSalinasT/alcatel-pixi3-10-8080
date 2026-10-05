#!/usr/bin/env python3
"""Convierte system.new.dat + system.transfer.list (formato por bloques de las ROM) a una imagen ext4 cruda.

Uso: sdat2img.py <system.transfer.list> <system.new.dat> <system.img>
"""
import sys
tl_path, dat_path, out_path = sys.argv[1:4]
tl = open(tl_path).read().split('\n'); ver = int(tl[0]); total = int(tl[1])
start = 4 if ver >= 2 else 2
BS = 4096
out = open(out_path, 'wb'); out.truncate(total * BS); src = open(dat_path, 'rb'); written = 0
for line in tl[start:]:
    p = line.split()
    if not p: continue
    if p[0] == 'new':
        r = [int(x) for x in p[1].split(',')][1:]
        for a, b in zip(r[0::2], r[1::2]):
            out.seek(a * BS); n = (b - a) * BS
            while n:
                buf = src.read(min(n, 1 << 22)); assert buf, "system.new.dat se acabó antes de tiempo"
                out.write(buf); n -= len(buf); written += len(buf)
    elif p[0] not in ('erase', 'zero'):
        print("comando no manejado:", p[0])
sobrante = bool(src.read(1)); out.close()
magic = open(out_path, 'rb').read(0x43a)[0x438:0x43a].hex()
print(f"versión {ver}, {written // 2**20} MB escritos, sobrante en .dat: {sobrante}, firma ext4 (debe ser 53ef): {magic}")
