import struct, re, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB
K = open('cmp/kernel_8080.bin','rb').read()
syms = {}; names = {}
for l in open('dump_vivo/dv/kallsyms.txt'):
    p = l.split()
    if len(p) >= 3:
        a = int(p[0],16); syms.setdefault(p[2], []).append(a); names[a] = p[2]
BASE = min(syms['_text']) if '_text' in syms else 0xc0008000
print("base _text = 0x%x, stext=%s" % (BASE, [hex(x) for x in syms.get('stext',[])]))
off = lambda a: a - BASE
def rd(a, n): return K[off(a):off(a)+n]
def cstr(a):
    b = rd(a, 80); return b.split(b'\0')[0].decode('latin1')
# localizar las estructuras LCM_DRIVER por el puntero al nombre
for nm in (b'rm68200_txd_wxga_pixi3', b'rm68200_yeji_wxga_pixi3', b'otm1287a_txd_wxga_pixi3', b'otm1287a_tdt_wxga_pixi3'):
    for m in re.finditer(re.escape(nm + b'\0'), K):
        sa = BASE + m.start()
        for pm in re.finditer(re.escape(struct.pack('<I', sa)), K):
            st = BASE + pm.start()
            ptrs = struct.unpack('<12I', rd(st, 48))
            print("\nLCM_DRIVER %s @0x%x (cadena @0x%x)" % (nm.decode(), st, sa))
            for i, p in enumerate(ptrs[1:], 1):
                print("   campo %2d = 0x%08x %s" % (i, p, names.get(p & ~1, '')))
