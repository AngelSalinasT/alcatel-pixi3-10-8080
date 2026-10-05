#!/bin/zsh
cd "$(dirname "$0")/.."
MTK=~/.local/bin/mtk; PORT=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1)
run() { # nombre offset archivo
  local sz=$(stat -f %z "$3"); local hx=$(printf "0x%x" $sz)
  echo "=== $(date +%H:%M:%S) escribiendo $1 @ $2 ($sz bytes)" >> flash.log
  PYTHONUNBUFFERED=1 perl -e 'alarm 1500; exec @ARGV' $MTK wo $2 $hx "$3" --serialport $PORT --debugmode 2>&1 | sed -e 's/\x1b\[[0-9;]*m//g' | grep --line-buffered -vE "TX:|RX:|File \"|^\s*$|SERIAL|readflash|Checksum|DeviceClass$" | tr '\r' '\n' | grep --line-buffered -vE "^Progress.*[0-9]\.[1-9]%" >> flash.log
  if grep -qE "Wrote .* to sector|Wrote $3|wrote|Done" <(tail -5 flash.log); then echo "--- $1 OK" >> flash.log; else echo "--- $1 SIN CONFIRMACION" >> flash.log; fi
}
run lk       0x1d20000 raw/lk.bin
run boot     0x1d80000 raw/boot.img
# releer boot para comprobar que la escritura es real
PYTHONUNBUFFERED=1 perl -e 'alarm 300; exec @ARGV' $MTK ro 0x1d80000 $(printf "0x%x" $(stat -f %z raw/boot.img)) boot_releido.bin --serialport $PORT --debugmode > /dev/null 2>&1
if cmp -s boot_releido.bin raw/boot.img; then echo "*** VERIFICACION boot: IDENTICO" >> flash.log; else echo "*** VERIFICACION boot: DIFERENTE, me detengo" >> flash.log; exit 1; fi
run recovery 0x2d80000 raw/recovery.img
run secro    0x3d80000 raw/secro.img
run logo     0x4400000 raw/logo.bin
run tee1     0x43980000 raw/tz.img
run tee2     0x43e80000 raw/tz.img
run custpack 0x4780000 raw/custpack.img
run system   0x44580000 raw/system.img
run cache    0x9bd80000 raw/cache.img
run userdata 0xabd80000 raw/userdata.img
echo "=== $(date +%H:%M:%S) TODO ESCRITO" >> flash.log
