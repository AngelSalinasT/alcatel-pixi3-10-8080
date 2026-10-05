#!/bin/zsh
# Escribe Android 7 (LineageOS 14.1 de ttab + kernel p8080) en la 8080. No toca preloader, LK ni identidad.
cd "$(dirname "$0")/.."
MTK=~/.local/bin/mtk; LOG=flash_los.log; : > $LOG; rm -f .state
P=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1); echo "puerto: $P" >> $LOG
f() { sed -e 's/\x1b\[[0-9;]*m//g' | grep --line-buffered -vE "TX:|RX:|File \"|^\s*$|SERIAL|readflash|Checksum|DeviceClass$" | tr '\r' '\n' | grep --line-buffered -vE "^Progress"; }
run() { local sz=$(stat -f %z "$3"); local hx=$(printf "0x%x" $sz); echo "=== $(date +%H:%M:%S) $1 @ $2 ($sz bytes)" >> $LOG
  PYTHONUNBUFFERED=1 perl -e 'alarm 1500; exec @ARGV' $MTK wo $2 $hx "$3" --serialport $P --debugmode 2>&1 | f | grep -E "Wrote|rror|Traceback" | tail -2 >> $LOG
  tail -1 $LOG | grep -q "^Wrote" && echo "--- $1 OK" >> $LOG || { echo "--- $1 FALLO" >> $LOG; return 1; } }
run boot 0x1d80000 raw/boot-los-p8080-v2.img || exit 1
hx=$(printf "0x%x" $(stat -f %z raw/boot-los-p8080-v2.img)); rm -f boot_releido.bin
PYTHONUNBUFFERED=1 perl -e 'alarm 120; exec @ARGV' $MTK ro 0x1d80000 $hx boot_releido.bin --serialport $P --debugmode > /dev/null 2>&1
cmp -s boot_releido.bin raw/boot-los-p8080-v2.img && echo "*** VERIFICACION boot: IDENTICO" >> $LOG || { echo "*** VERIFICACION boot: DIFERENTE" >> $LOG; exit 1; }
run system   0x44580000 raw/system-los14.img || exit 1
run cache    0x9bd80000 raw/cache.img || exit 1
run userdata 0xabd80000 raw/userdata-los14.img || exit 1
PYTHONUNBUFFERED=1 perl -e 'alarm 40; exec @ARGV' $MTK reset --serialport $P --debugmode 2>&1 | f | grep -E "Reset|rror" | tail -1 >> $LOG
rm -f .state; echo "=== $(date +%H:%M:%S) TODO ESCRITO" >> $LOG
