import struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
K = open('cmp/kernel_8080.bin','rb').read(); BASE = 0xc0008000
names = {}
for l in open('dump_vivo/dv/kallsyms.txt'):
    p = l.split()
    if len(p) >= 3: names.setdefault(int(p[0],16), p[2])
md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
def dis(start, end, title):
    print("\n==== %s  0x%x-0x%x" % (title, start, end))
    code = K[start-BASE:end-BASE]
    for i in md.disasm(code, start):
        extra = ''
        if i.mnemonic in ('bl','b','blx') and i.op_str.startswith('#'):
            t = int(i.op_str[1:],16); extra = '  ; ' + names.get(t, '?')
        if 'pc' in i.op_str and i.mnemonic.startswith('ldr') and '[pc' in i.op_str:
            try:
                o = int(i.op_str.split('#')[1].rstrip(']'),16) if '#' in i.op_str else 0
                a = i.address + 8 + o; v = struct.unpack('<I', K[a-BASE:a-BASE+4])[0]
                extra = '  ; =0x%08x %s' % (v, names.get(v, ''))
            except Exception: pass
        print("  %08x  %-7s %s%s" % (i.address, i.mnemonic, i.op_str, extra))
a = [int(x,16) for x in sys.argv[2:]]
dis(a[0], a[1], sys.argv[1])
