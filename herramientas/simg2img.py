import struct, sys
def conv(src, dst):
    with open(src,'rb') as f, open(dst,'wb') as o:
        magic,maj,minr,fh,ch,blk,tot,nch,crc = struct.unpack('<IHHHHIIII', f.read(28)); assert magic==0xed26ff3a
        f.read(fh-28); out=0
        for _ in range(nch):
            ct,_,cb,ts = struct.unpack('<HHII', f.read(12)); f.read(ch-12); n=cb*blk
            if ct==0xCAC1:
                left=n
                while left: b=f.read(min(left,1<<22)); o.write(b); left-=len(b)
            elif ct==0xCAC2:
                fill=f.read(4)
                if fill==b'\0\0\0\0': o.seek(n,1)
                else:
                    buf=fill*(1<<18); left=n
                    while left: w=min(left,len(buf)); o.write(buf[:w]); left-=w
            elif ct==0xCAC3: o.seek(n,1)
            elif ct==0xCAC4: f.read(4)
            out+=cb
        o.truncate(tot*blk)
    return tot*blk
for s,d in zip(sys.argv[1::2], sys.argv[2::2]): print(d, conv(s,d))
