from Smarch.smarch_opt import master, read_dimacs
from kconfigIO import read_configs_kmax
# import kmaxtools.klocalizer

# def read_dimacs_features(dimacsfile_):
#     """parse features from a dimacs file"""
#     _features = list()
#     with open(dimacsfile_) as df:
#         for _line in df:
#             # read variables in comments
#             if _line.startswith("c"):
#                 _line = _line[0:len(_line) - 1]
#                 _feature = _line.split(" ", 4)
#                 del _feature[0]
#                 _feature[0] = int(_feature[0])
#                 _features.append(tuple(_feature))
#     return _features
# def encode_samples(cdir_, dimacs_):
#     ##returns an array of the samples in Smarch format
# 	features = read_dimacs_features(dimacs_)
# 	return read_configs_kmax(features, cdir_)

# s = encode_samples("trash", "FM/linux.dimacs")

# for elem in s:
#     print(elem)



import sampleLinux

numbering, features = sampleLinux.read_kconfig_extract()
# s = sampleLinux.gen_constrained_config("/media/space/elkdat/linux/", "/media/space/HC2/HCS_Optimizer/trash/", "/media/space/HC2/HCS_Optimizer/trash/test.const", "hi" )
linux = "/media/space/elkdat/linux/"
_outdir = "/media/space/HC2/HCS_Optimizer/trash/samplz"
constraints = sampleLinux.read_constraints("trash/test.const",features)
# print(constraints)
# for i in range(6):
#     print(features[i])
# sampleLinux.gen_constrained_config(linux, _outdir, "/media/space/HC2/HCS_Optimizer/trash/test.const", "fu")  
s = sampleLinux.sample_linux(linux, _outdir, constraints, features, 1)
