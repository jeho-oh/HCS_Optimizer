#!bin/bash

# $1: target name
# $2: config folder name
# $3: makefile location
# $4: Kconfig directory

echo Building $1 at $2

cd $4
rm -r ./cases/$1/$2/build_out


vagrant ssh -c "cd $3 && driver.sh build $1 $2"