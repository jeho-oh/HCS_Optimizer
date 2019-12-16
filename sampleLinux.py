import os
import sys
import filecmp
import subprocess
import random
import string
from Smarch.smarch_opt import master, read_dimacs
DEBUG = False
import os

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def validate_config(_linux, _config):
    cmd = "cd " + _linux + "&& make mrproper"
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_, stderr_ = sp.communicate()
    if DEBUG:
        print_all_output(stdout_, stderr_)
    cmd = "cp " +  _config + " "  + _linux + "/.config"

    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_, stderr_ = sp.communicate()
    if DEBUG:
        print_all_output(stdout_, stderr_)
    cmd = "cd " + _linux + "&& make olddefconfig"
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_, stderr_ = sp.communicate()
    if(stderr_):
        print("error")
    if DEBUG:
        print_all_output(stdout_, stderr_)
    return filecmp.cmp(_config, _linux + "/.config")

def print_all_output(stdout_, stderr_):
    print(str(stdout_, sys.stdout.encoding))
    print(str(stderr_, sys.stdout.encoding))




# def randconfig(_linux, _configs, name):
#     cmd = "cd " + _linux + "&& make randconfig"
#     sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     stdout_, stderr_ = sp.communicate()
#     if DEBUG:
#         print_all_output(stdout_, stderr_)

#     cmd = "cd " + _linux + "&& cp .config " + _configs + "/" + name + ".config"
#     sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     stdout_, stderr_ = sp.communicate()
#     # valid = validate_config(_linux, _configs + "/" + name + ".config" )
#     print(_configs)

#     if DEBUG:
#         print_all_output(stdout_, stderr_)
    
def sample_linux(_linux, _outdir, constraints, features_, num):
    write_constraints(constraints, "/tmp/apple", features_)   
    for i in range(num):
        return_code = gen_constrained_config(_linux, _outdir, "/tmp/apple", str(i))
    if DEBUG:
        print("generating sample in " + _outdir)
    return read_configs_kmax(features_,_outdir)

def gen_constrained_config(_linux, _outdir, _constraintsfile, name):
    """Call klocalizer with constraints, and save the config to _outdir"""
    with cd(_linux):
        import random
        seed = str(random.randint(300,799999))
       # cmd = "export KCONFIG_SEED=0xE5B8749E && klocalizer -a x86_64 --constraints-file " + _constraintsfile
        cmd = "klocalizer -a x86_64 --random-seed " + seed + " --constraints-file " + _constraintsfile
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_, stderr_ = sp.communicate()
        return_code = sp.returncode
        if return_code != 0:
            print("klocalizer errror")
            print_all_output(stdout_, stderr_)   
        
        if DEBUG:
            print_all_output(stdout_, stderr_)
        cmd = "cp .config " + _outdir + "/" + name + ".config"
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_, stderr_ = sp.communicate()
        return return_code

def write_constraints(constraints, constfile_, features_):
    """write out constraint file"""
    constraintsf = [item for sublist in constraints for item in sublist]

    indices = [i[0] for i in features_]
    with open(constfile_, "w") as out:
        for constraint in constraintsf:
            if constraint < 0:
                i = indices.index(-constraint)
                out.write("!" + features_[i][1] + "\n")
            else:
                i =  indices.index(constraint)
                out.write(features_[i][1] + "\n")

def read_constraints(constfile_, features_):
    """read constraint file. - means negation"""

    _const = list()

    if os.path.exists(constfile_):
        names = [i[1] for i in features_]
        with open(constfile_) as file:
            for _line in file:
                _line = _line.rstrip()
                data = _line.split()
                if len(data) != 0:
                    clause = list()

                    error = False
                    for name in data:
                        prefix = 1
                        if name.startswith('!'):
                            name = name[1:len(name)]
                            prefix = -1

                        if name in names:
                            i = names.index(name)
                            clause.append(features_[i][0] * prefix)
                        else:
                            error = True
                            clause.append(name)

                    if not error:
                        _const.append(clause)
                        print("Added constraint: " + _line + " " + str(clause))
                    else:
                        print("Feature not found" + str(clause))
    else:
        print("Constraint file not found")
        print(constfile_)

    return _const




# def find_replace(_file, constraints):
#     if os.path.exists(_file):
#         os.rename(_file, _file + ".bak")
#         infile = open(_file + ".bak", "r")
#         out = open(_file, "w")
#         for line in infile:
#             s = line
#             for c in constraints:
#                 if c[0] in line:
#                    s = (c[0] + "=" + c[1] + "\n")
#             out.write(s)
#     else:
#         print(_file)
#         raise FileNotFoundError

def encode_samples(cdir_, dimacs_):
    ##returns an array of the samples in Smarch format
	features = read_dimacs_features(dimacs_)
	return read_configs_kmax(features, cdir_)
    # sample_bit_arrays = []
	# for sample in samples:
	# 	bit_array = [0]*len(sample)
	# 	for s in sample:
	# 		if s > -1:
	# 			bit_array[s - 1] = 1
	# 	sample_bit_arrays.append(bit_array)
	# configs = [f for f in os.listdir(cdir_) if os.path.isfile(os.path.join(cdir_, f))]
	# configs.sort(key=lambda s: int(s[:s.find('.')]))
	# return sample_bit_arrays, configs

def read_configs_kmax(features_, cdir_):
    samples = list()

    for file in os.listdir(cdir_):
        if file.endswith('.config'):
            # convert config file into variable list
            sol = read_config(features_, cdir_ + "/" + file)
            samples.append(sol)
    return samples


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
                #print(data)
                if len(data) > 1:
                    if data[0] in _names:
                        i = _names.index(data[0])
                        _existing.add(data[0])
                        if data[1] == 'y':
                            sol.append(features_[i][0])
                        elif data[1] == '\"\"' or data[1] == '0':
                            sol.append(-1 * features_[i][0])

                        else:
                            sol.append(features_[i][0])
                    # else:
                    #     print(line)

    # set all nonexistent variables to false
    for f in features_:
        if f[1] not in _existing:
            sol.append(-1 * f[0])

    return sol


def read_dimacs_features(dimacsfile_):
    """parse features from a dimacs file"""
    _features = list()
    with open(dimacsfile_) as df:
        for _line in df:
            # read variables in comments
            if _line.startswith("c"):
                _line = _line[0:len(_line) - 1]
                _feature = _line.split(" ", 4)
                del _feature[0]
                _feature[0] = int(_feature[0])
                _features.append(tuple(_feature))
    return _features

def read_kconfig_extract(linux_):
    features = list()
    kconfig_extract_file = linux_ + ".kmax/kclause/x86_64/kconfig_extract"
    kconfig_extract = get_kconfig_extract(kconfig_extract_file)
    if kconfig_extract == None:
        print("Error, kconfig extract not found or invalid at " + kconfig_extract_file)
        sys.exit(1)
    else:
        i = 1
        numbering = {}
        for kconfig_line in kconfig_extract:
        # see docs/kconfig_extract_format.md for more info
            if kconfig_line[0] == "config":
                numbering[kconfig_line[1]] = i
                features.append([i, kconfig_line[1], kconfig_line[2]])
                i = i + 1
    return numbering, features






    
def get_kconfig_extract(kconfig_extract_file):
  """Return a list of lists, where each list is a line from the kconfig_extract, currently only the config lines.  See docs/kconfig_extract_format.md.  Returns None if no file is found."""
  # kconfig_extract_file = get_arch_kconfig_extract_file(formulas, arch)
  
  if not os.path.exists(kconfig_extract_file):
    # warning("no kconfig_extract file found: %s", kconfig_extract_file)
    return None
  else:
    lists = []
    with open(kconfig_extract_file, 'r') as fp:
      for line in fp:
        line = line.strip()
        lists.append(line.split())
      return lists
  
