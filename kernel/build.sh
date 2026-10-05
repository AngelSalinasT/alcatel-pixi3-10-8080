#!/bin/bash
# Compila el kernel dentro de un contenedor ubuntu:16.04. Uso: build.sh <arbol> <defconfig>
set -e
TREE=$1; CFG=$2
if [ ! -d /work/toolchain/bin ]; then
  mkdir -p /work/toolchain && cd /work/toolchain
  wget -q -O tc.tar.gz "https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8/+archive/refs/heads/lollipop-release.tar.gz"
  tar xzf tc.tar.gz && rm tc.tar.gz
fi
export PATH=/work/toolchain/bin:$PATH ARCH=arm CROSS_COMPILE=arm-eabi-
cd /work/$TREE
arm-eabi-gcc --version | head -1
mkdir -p /work/out-$TREE
make O=/work/out-$TREE $CFG
make O=/work/out-$TREE -j4 zImage 2>&1 | tail -60
ls -la /work/out-$TREE/arch/arm/boot/
