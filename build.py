import os, sys

profan_path = "../profanOS"
if sys.argv[1:]:
    profan_path = sys.argv[1]
if not os.path.exists(profan_path):
    print(f"path {profan_path} does not exist")
    exit(1)

CC      = "gcc"
LD      = "ld"
AR      = "ar"

CC_FLAGS = f"-m32 -O2 -fno-omit-frame-pointer -fno-asynchronous-unwind-tables -ffreestanding -fno-exceptions -nostdinc -fno-stack-protector -I {profan_path}/include/zlibs -I {profan_path}/include/addons -D__profanOS__ -DONE_SOURCE=0"
SO_FLAGS = f"-m elf_i386 -L {profan_path}/out/zlibs -nostdlib -shared"
LD_FLAGS = f"-nostdlib -L {profan_path}/out/zlibs -T link.ld -lc -lm"

OBJDIR  = "tmp"
OUTDIR  = "build"

SRCDIR  = "src"
LIB1DIR = "libtcc1"

TCC_SRC     = [e for e in os.listdir(SRCDIR) if e.endswith(".c") and e != "tcc.c"]

LIBTCC1_SRC = ["libtcc1.c", "alloca.S", "alloca-bt.S", "stdatomic.c", "atomic.S", "builtin.c", "tcov.c", "va_list.c", "dsohandle.c"]
EXTRA_SRC   = ["runmain.c", "bt-exe.c", "bt-log.c", "tccmem.c"]

def execute_command(cmd):
    rcode = os.system(cmd)
    if rcode == 0: return
    print(f"{cmd}\nfailed with exit code {rcode}")
    exit(rcode if rcode < 256 else 1)

def compile_file(src, dir = SRCDIR, out = OBJDIR, pic = False):
    print(f"GCC {'pic ' if pic else 4*' '}{src}")
    obj = os.path.join(out, f"{os.path.splitext(src)[0]}.o")
    cmd = f"{CC} -c {os.path.join(dir, src)} -o {obj} {CC_FLAGS}{f' -fPIC' if pic else ''}"
    execute_command(cmd)
    return obj

def link_to_exec(entry, objs, name):
    print(f"LD ==== {name}.elf")
    execute_command(f"{LD} {LD_FLAGS} -o {OUTDIR}/{name}.elf {entry} {' '.join(objs)}")

def link_to_lib(objs, name):
    print(f"LD ==== {name}.so")
    execute_command(f"{LD} {SO_FLAGS} -o {OUTDIR}/{name}.so {' '.join(objs)} -lc -lm")

def archive_objs(objs, name):
    print(f"AR ==== {name}.a")
    execute_command(f"{AR} rcs {OUTDIR}/{name}.a {' '.join(objs)} ")

def compile_tcc():
    print("\n-- COMPILING TCC")

    objs = [compile_file(src, pic = True) for src in TCC_SRC]
    link_to_lib(objs, "libtcc")

    objs = [compile_file(src) for src in TCC_SRC]
    archive_objs(objs, "libtcc")

    objs.append(compile_file("tcc.c"))
    link_to_exec(f"{profan_path}/out/make/entry_elf.o", objs, "tcc")

def compile_libtcc1():
    print("\n--- COMPILING LIBTCC1")

    objs = [compile_file(src, dir = LIB1DIR) for src in LIBTCC1_SRC]
    archive_objs(objs, "libtcc1")    

def compile_extra():
    print("\n--- COMPILING EXTRA FILES")

    [compile_file(src, dir = LIB1DIR, out = OUTDIR) for src in EXTRA_SRC]
    execute_command(f"objcopy --remove-section=.note.GNU-stack --remove-section=.comment {OUTDIR}/tccmem.o")

    print("GCC     tcc.c")
    execute_command(f"gcc -m32 src/tcc.c -o {OBJDIR}/tcc-i386")

    print("TCC -bt bcheck.c")
    execute_command(f"./{OBJDIR}/tcc-i386 -I {profan_path}/include/zlibs -I include -D__profanOS__ -nostdlib -B build -bt -c {LIB1DIR}/bcheck.c -o {OUTDIR}/bcheck.o")

    print("TAR === tccobjs.tar.gz")
    execute_command(f"cd {OUTDIR} && tar -czf tccobjs.tar.gz *.o")

if __name__ == "__main__":
    execute_command(f"rm -rf {OBJDIR} {OUTDIR}")
    execute_command(f"mkdir -p {OBJDIR} {OUTDIR}")
    compile_tcc()
    compile_libtcc1()
    compile_extra()
    execute_command(f"rm -rf {OBJDIR}")
    print("\nSuccess! use `sh install.sh` to install in profanOS\n")
