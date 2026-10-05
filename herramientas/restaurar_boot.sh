#!/bin/zsh
# Espera la tablet, la atrapa y restaura el arranque que funciona (Magisk). Luego copia expdb.
cd "$(dirname "$0")/.."
MTK=~/.local/bin/mtk; LOG=restaurar.log; : > $LOG
rm -f .state
~/.local/share/uv/tools/mtkclient/bin/python herramientas/pl_catch.py >> $LOG 2>&1
P=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1); echo "puerto: $P" >> $LOG
[ -z "$P" ] && { echo "SIN PUERTO" >> $LOG; exit 1; }
f() { sed -e 's/\x1b\[[0-9;]*m//g' | grep --line-buffered -vE "TX:|RX:|File \"|^\s*$|SERIAL|readflash|Checksum|DeviceClass$|Progress"; }
IMG=raw/boot-magisk.img; hx=$(printf "0x%x" $(stat -f %z $IMG))
PYTHONUNBUFFERED=1 perl -e 'alarm 240; exec @ARGV' $MTK wo 0x1d80000 $hx $IMG --serialport $P --debugmode 2>&1 | f | tail -6 >> $LOG
rm -f boot_releido.bin
PYTHONUNBUFFERED=1 perl -e 'alarm 120; exec @ARGV' $MTK ro 0x1d80000 $hx boot_releido.bin --serialport $P --debugmode > /dev/null 2>&1
if cmp -s boot_releido.bin $IMG; then echo "VERIFICACION: IDENTICO" >> $LOG; else echo "VERIFICACION: DIFERENTE O SIN LEER" >> $LOG; fi
rm -f expdb_tras_fallo.bin
PYTHONUNBUFFERED=1 perl -e 'alarm 200; exec @ARGV' $MTK ro 0x42f80000 0xa00000 expdb_tras_fallo.bin --serialport $P --debugmode 2>&1 | f | grep -E "Dumped|rror" | tail -2 >> $LOG
PYTHONUNBUFFERED=1 perl -e 'alarm 40; exec @ARGV' $MTK reset --serialport $P --debugmode 2>&1 | f | grep -E "Reset|rror" | tail -1 >> $LOG
rm -f .state; echo "FIN" >> $LOG
