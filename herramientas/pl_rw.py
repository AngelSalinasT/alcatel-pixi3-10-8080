import serial, glob, struct
s = serial.Serial(glob.glob('/dev/cu.usbmodem*')[0], 115200, timeout=1.0, write_timeout=1.0)
s.reset_input_buffer()
def echo(b):
    s.write(b); r = s.read(len(b)); return r
print("sync HW_CODE:", (lambda: (s.write(b'\xfd'), s.read(5).hex()))()[1])
# read32 (0xD1): cmd, addr(4), count(4) con eco; status(2); datos; status(2)
def read32(addr, n=1):
    r1 = echo(b'\xd1'); r2 = echo(struct.pack(">I", addr)); r3 = echo(struct.pack(">I", n))
    st = s.read(2); data = s.read(4 * n); st2 = s.read(2)
    return r1.hex(), r2.hex(), r3.hex(), st.hex(), data.hex(), st2.hex()
print("read32 WDT 0x10007000:", read32(0x10007000))
print("read32 0x10206000 (efuse/segmento):", read32(0x10206000))
print("BL_VER:", (lambda: (s.write(b'\xfe'), s.read(1).hex()))()[1])
s.close()
