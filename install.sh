if [ -z "$1" ]; then
    profan="../profanOS"
else
    profan=$1
fi

build="build"

mkdir -p $profan/out/zapps/f/
mkdir -p $profan/include/addons/
mkdir -p $profan/out/zlibs/tcc/
mkdir -p $profan/out/zlibs/

cp -v include/tccdefs.h $profan/include/addons/

cp -v $build/tcc.elf $profan/out/zapps/f/
cp -v $build/libtcc.so $profan/out/zlibs/
cp -v $build/libtcc.a  $profan/out/zlibs/

cp -v $build/libtcc1.a $profan/out/zlibs/
cp -v $build/*.o $profan/out/zlibs/tcc/
