import os
import sys
import time
import subprocess


config_file = 0
kconfig_root = 1
binaries = 2
check_dep_extra_args = 3
dimacs_extra_args = 4
make_extra_args = 6
preprocess_args_opt = 7
makeclean = 8
makecmd = 9


def get_props(target):
    properties = [None] * 10
    ##idices into array

    if target == "busybox":
        properties[config_file] = ".config"
        properties[kconfig_root] = "Config.in"
        properties[binaries] = "busybox"
        properties[preprocess_args_opt] = ""
        properties[makeclean] = "make clean"
        properties[makecmd] = "make"
        properties[make_extra_args] = ''
    elif target == "linux":
        properties[config_file] = ".config"
        properties[kconfig_root] = "Config.in"
        properties[binaries] = "arch/x86/boot/bzImage"
        properties[preprocess_args_opt] = ""
        properties[makeclean] = "make mrproper"
        properties[makecmd] = "make olddefconfig && make"
        properties[make_extra_args] = ''

    elif target == "fiasco":
        print(target)
        properties[makecmd] = "make"
        properties[config_file] = "build/globalconfig.out"
        properties[kconfig_root] = "build/Kconfig"
        properties[preprocess_args_opt] = "V=1"
        properties[makeclean] = "make -C build/ clean"
        properties[make_extra_args] = ''
        # perhaps just use "*.{o,a}"
        properties[binaries] = "build"
    elif target == "toybox":
        properties[config_file] = ".config"
        properties[kconfig_root] = "Config.in"
        properties[binaries] = "toybox"
        properties[preprocess_args_opt] = "V=1 CC=gcc"
        properties[make_extra_args] = ''
        properties[makeclean] = "make clean"
    elif target == "uClibc-ng":
        print(target)
    elif target == "buildroot":
        print("WARNING  TODO IN HERE")
        print(target)
        properties[config_file] = ".config"
        properties[kconfig_root] = "Config.in"
        properties[binaries] = "*"  # TODO: set arr[binaries]
        # don't add CONFIG_ prefix, already uses BR2 itself.  must set a build path.
        properties[check_dep_extra_args] = "-e BUILD_DIR=."
        properties[makeclean] = "make clean"
        properties[make_extra_args] = ''

    ##TODO: touch .br2-external.in  # this file is necessary in order to process the Config.in
    elif target == "axtls":
        print("WARNING  TODO IN HERE")
        print(target)
        properties[config_file] = "config/.config"
        properties[kconfig_root] = "config/Config.in"
        properties[binaries] = "_stage/"
        properties[check_dep_extra_args] = "-p"
        properties[preprocess_args_opt] = "CC=gcc"
        properties[makeclean] = "make clean"
        properties[make_extra_args] = ''
    ##                  mkdir -p /tmp/local
    ##  time make ${preprocess_args_opt} ${make_extra_args} PREFIX="/tmp/local"

    return properties
return_code_template = "return code 0"

class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def run_make(bscource, properties, config_file):
    with cd(bscource):
        cmd = properties[makecmd] + " " + properties[make_extra_args] + " >/tmp/sampling/stdout_" + config_file + " 2>&1"
        # print(bscource)
        # print(cmd)
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_, stderr_ = sp.communicate()
        return_code = sp.returncode
        # print("return code: " + return_code)
        if stderr_:
            print("Build error at " + config_file)
            print(str(stderr_, sys.stdout.encoding))
        # print(str(stdout_, sys.stdout.encoding))
        return return_code


def clean(bscource, properties):
    # print("size before clean: ",end=" ")
    # print(size(bscource, properties))

    with cd(bscource):
        cmd = properties[makeclean] + " >/tmp/sampling/CLEANOUT 2>&1"

        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_, stderr_ = sp.communicate()
        if stderr_:
            print(stderr_)
        print(str(stdout_, sys.stdout.encoding))
    # print("size after", end= " ")
    # print(size(bscource, properties))

def copy_config(bscource, properties, _config_file):
    cmd = "cp " + _config_file + " " + bscource + properties[config_file]
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_, stderr_ = sp.communicate()
    if stderr_:
        print(stderr_)
    # print(str(stdout_, sys.stdout.encoding))
    return sp.returncode


def size(bscource, properties):
    with cd(bscource):
        cmd = "du -bc " + properties[binaries] +  " + | tail -n1 | cut -f1"
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout_, stderr_ = sp.communicate()
        if sp.returncode != 0:
            print("Error measuring build size")

        return (str(stdout_, sys.stdout.encoding))

