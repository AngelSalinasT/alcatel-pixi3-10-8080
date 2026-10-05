import serial, time, glob, struct
end = time.time() + 120; seen = 0
while time.time() < end:
    ports = glob.glob('/dev/cu.usbmodem*')
    if not ports: time.sleep(0.01); continue
    try: s = serial.Serial(ports[0], 115200, timeout=0.05, write_timeout=0.2)
    except Exception: time.sleep(0.01); continue
    seen += 1; ok = False
    try:
        t0 = time.time(); i = 0; seq = b"\xa0\x0a\x50\x05"; echo = 0
        while i < 4 and time.time() - t0 < 4:
            s.write(seq[i:i+1]); r = s.read(1)
            if r and r[0] == (~seq[i]) & 0xFF: i += 1
            elif r and i == 0 and r[0] == 0xA0:
                echo += 1
                if echo > 3: i = 4; print("ya estaba en modo comandos (eco)")
            else: i = 0
        if i == 4:
            s.timeout = 1; s.reset_input_buffer(); s.write(b'\xfd'); r = s.read(5)
            print(f"ENGANCHADA en {time.time()-t0:.2f}s (aparición #{seen}); HW_CODE={r.hex()}")
            ok = len(r) == 5 and r[0] == 0xFD
    except Exception as e:
        pass
    finally:
        try: s.close()
        except Exception: pass
    if ok: break
    time.sleep(0.05)
else:
    print("no se logró en 120 s; apariciones:", seen)
