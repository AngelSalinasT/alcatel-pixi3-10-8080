import serial, glob, struct
ports = glob.glob('/dev/cu.usbmodem*'); print("puertos:", ports)
if ports:
    s = serial.Serial(ports[0], 115200, timeout=1.0, write_timeout=1.0)
    def cmd(b, n, name):
        s.reset_input_buffer(); s.write(bytes([b])); r = s.read(1 + n)
        print(f"{name}: eco={r[:1].hex()} datos={r[1:].hex()}"); return r[1:]
    d = cmd(0xFD, 4, "GET_HW_CODE")
    if len(d) == 4: print("   hwcode=0x%04x status=0x%04x" % struct.unpack(">HH", d))
    d = cmd(0xFC, 8, "GET_HW_SW_VER")
    if len(d) == 8: print("   hwsub=0x%04x hwver=0x%04x swver=0x%04x status=0x%04x" % struct.unpack(">HHHH", d))
    d = cmd(0xD8, 6, "GET_TARGET_CONFIG")
    if len(d) == 6:
        cfg, st = struct.unpack(">IH", d); print("   target_config=0x%08x status=0x%04x  SBC=%d SLA=%d DAA=%d" % (cfg, st, cfg & 1, (cfg >> 1) & 1, (cfg >> 2) & 1))
    cmd(0xFE, 1, "GET_BL_VER")
    cmd(0xFF, 1, "GET_VERSION")
    s.close()
