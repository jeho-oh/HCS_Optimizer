import random
import os
import shutil
from subprocess import check_call, DEVNULL
from pathlib import Path


root = os.path.dirname(os.path.abspath(__file__))

home = str(Path.home())
KCONFIG = " "
BUILD = " "
LINUX_DIR = "/media/space/linuxnext/linux-next/"
WORK_DIR = "/media/space/HC2/work/"


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def gen_configs(target_, features_, samples_, cdir_):
    # remove existing contents on the folder
    for f in os.listdir(cdir_):
        file_path = os.path.join(cdir_, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    # generate .config files from samples
    i = 0
    for s in samples_:
        config = ""
        for sel in s:
            feature = features_[abs(sel) - 1]

            if sel > 0:
                if feature[2] == 'nonbool':
                    config = config + feature[1] + "=" + feature[3] + "\n"
                else:
                    config = config + feature[1] + "=y\n"

            elif sel < 0:
                if feature[2] == 'nonbool':
                    if is_int(feature[3]):
                        config = config + feature[1] + "=0\n"
                    else:
                        config = config + feature[1] + "=\"\"\n"
                else:
                    config = config + "# " + feature[1] + " is not set\n"

        with open(cdir_ + "/" + str(i) + ".config", 'w') as outfile:
            outfile.write(config)
            outfile.close()

        i += 1

    #print("Configs generated")


    nfs = list()
    bfs = list()
    lfs = list()
    nfv = dict()
    fcount = 0

    # remove existing contents on the folder
    for f in os.listdir(cdir_):
        file_path = os.path.join(cdir_, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    # parse boolean and numerical features
    for f in features_:
        if f[2] == 'bool' or f[2] == 'hidden_bool' or f[2] == 'choice_bool':
            bfs.append(f)
        elif f[2] == 'numeric':
            nfs.append(f)
        elif f[2] == 'nonbool':
            lfs.append(f)

    for nf in nfs:
        _i = nf[1].rfind('_')
        name = nf[1][:_i]

        if name not in nfv:
            nfv[name] = 0

    #fcount = len(bfs) + len(nfv)

    # generate .config files from samples
    i = 0
    for s in samples_:
        config = ""

        # add boolean features
        for bf in bfs:
            if bf[0] in s:
                config = config + bf[1] + "=y\n"
            else:
                config = config + "# " + bf[1] + " is not set\n"

        # add numeric features
        nvalues = nfv.copy()
        for nf in nfs:
            if nf[0] in s:
                _i = nf[1].rfind('_')
                name = nf[1][:_i]
                bit = nf[1][_i+1:]

                raw = nf[1].split('_')
                nvalues[name] = nvalues[name] + 2**(int(bit))

        for nf in nvalues:
            if target_ == 'axtls_2_1_4':
                config = config + nf + "=" + str(nvalues[nf] * (2 ** 21)) + "\n"
            elif target_ == 'fiasco_17_10':
                if nf == 'CONFIG_MP_MAX_CPUS':
                    config = config + nf + "=" + str(nvalues[nf] + 1) + "\n"
                elif nf == 'CONFIG_MIPS_CPU_FREQUENCY':
                    config = config + nf + "=" + str(nvalues[nf] * (2 ** 21)) + "\n"
                else:
                    config = config + nf + "=" + str(nvalues[nf]) + "\n"
            elif target_ == 'uClibc-ng_1_0_29':
                if nf == 'CONFIG_UCLIBC_PWD_BUFFER_SIZE' or nf == 'CONFIG_UCLIBC_GRP_BUFFER_SIZE':
                    config = config + nf + "=" + str(nvalues[nf] + 1) + "\n"
                else:
                    config = config + nf + "=" + str(nvalues[nf] * (2 ** 21)) + "\n"

        # add literal features
        for lf in lfs:
            if lf[0] in s:
                config = config + lf[1] + "=" + lf[3] + "\n"
            else:
                config = config + lf[1] + "=\"\"\n"

        with open(cdir_ + "/" + str(i) + ".config", 'w') as outfile:
            outfile.write(config)
            outfile.close()

        i += 1

    print("Configs generated")


def read_config(features_, config_):
    sol = list()
    _existing = set()
    _names = [i[1] for i in features_]

    with open(config_, 'r') as f:
        for line in f:
            # line: # FEATURE is not set
            if line.startswith('#'):
                line = line[0:len(line) - 1]
                data = line.split()
                if len(data) > 4:
                    if data[1] in _names:
                        i = _names.index(data[1])
                        _existing.add(data[1])
                        if i != -1:
                            sol.append(-1 * features_[i][0])
                    # else:
                    #     print(line)
            # line: FEATURE=y or FEATURE="nonbool value"
            else:
                line = line[0:len(line) - 1]
                data = line.split('=')
                if len(data) > 1:
                    if data[0] in _names:
                        i = _names.index(data[0])
                        _existing.add(data[0])
                        if data[1] == 'y':
                            sol.append(features_[i][0])
                        elif data[1] == '\"\"' or data[1] == '0':
                            if features_[i][3] != '\"\"' and features_[i][3] != '0':
                                sol.append(-1 * features_[i][0])
                            else:
                                sol.append(features_[i][0])
                                # r = random.random()
                                # sol.append('-' + features_[i][0])
                                # if r < 0.5:
                                #     sol.append(features_[i][0])
                                # else:
                                #     sol.append('-' + features_[i][0])
                        else:
                            sol.append(features_[i][0])
                    # else:
                    #     print(line)

    # set all nonexistent variables to false
    for f in features_:
        if f[1] not in _existing:
            sol.append(-1 * f[0])

    return sol


def read_configs_kmax(features_, cdir_):
    samples = list()

    for file in os.listdir(cdir_):
        if file.endswith('.config'):
            # convert config file into variable list
            sol = read_config(features_, cdir_ + "/" + file)
            samples.append(sol)

    return samples


def build_samples(target_, configs_):
    import dobuild
    build_sizes = list()
    properties = dobuild.get_props('linux')
    configs = [f for f in os.listdir(configs_) if os.path.isfile(os.path.join(configs_, f)) and f.endswith(".config")]
    configs.sort(key=lambda s: int(s[:s.find('.')]))
    for file_ in configs:
        if file_.endswith(".config"):   
            dobuild.clean( target_, properties)
            dobuild.copy_config(target_, properties, configs_ + file_)
            ret_code = dobuild.run_make(target_, properties, file_)
            build_size = dobuild.size(target_, properties)
            build_sizes.append([build_size,ret_code])

    with open(configs_ + "binary_sizes.txt", "w") as b, open(configs_ + "return_codes.txt","w") as r:
        for bs in build_sizes:
            b.write('binary size (in bytes): ' + str(bs[0]) + '\n')
            r.write('return code ' + str(bs[1]) + '\n')



        # check_call("cd /media/space/linuxnext/linux-next &&  /media/space/HC2/HCS_Optimizer/driver.sh build linux_4_17_6 nbuild/configs", shell=True, stdout=DEVNULL, stderr=DEVNULL)
        # check_call(BUILD + " " + target_ + " " + configs_ + " " + target_ + " " + KCONFIG, shell=True, stdout=DEVNULL, stderr=DEVNULL)
        #pass
# def build_samples(target_, configs_, makefile_):
#     # run vagrant for build
#     if target_ == 'fiasco_17_10':
#         check_call(BUILD + " " + target_ + " " + configs_ + " " + makefile_ + "/src/kernel/fiasco" + " " + KCONFIG, shell=True, stdout=DEVNULL, stderr=DEVNULL)
#     else:
#         #  from fakebuild import gen
#         #  import glob
#          #print("building")
#          #count = len(glob.glob1(configs_dir,"*.config"))
#          #gen(count, configs_dir)
#         check_call("cd /media/space/linuxnext/linux-next &&  /media/space/HC2/HCS_Optimizer/driver.sh build linux_4_17_6 nbuild/configs", shell=True, stdout=DEVNULL, stderr=DEVNULL)
