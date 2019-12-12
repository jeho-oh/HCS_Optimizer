#!bin/bash

# $1: target name
# $2: config folder name
# $3: makefile location
# $4: Kconfig directory

echo Building $1 at $2

cd $4

export KCONFIG_CASE_STUDIES="/home/nod/Desktop/kconfig_case_studies"
"cd /media/space/elkdat/linux &&  /media/space/HC2/HCS_Optimizer/driver.sh build linux_4_17_6 nbuild/configs"
