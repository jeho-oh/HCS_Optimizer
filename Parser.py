



def read_dimacs(dimacsfile_):
    """parse variables and clauses from a dimacs file"""

    _bf = list()
    _nfr = list()
    _clauses = list()
    _vcount = '-1'  # required for variables without names

    with open(dimacsfile_) as f:
        for line in f:
            # read variables in comments
            if line.startswith("c"):
                line = line[0:len(line) - 1]
                _feature = line.split(" ", 4)
                del _feature[0]
                _feature[0] = int(_feature[0])
                if _feature[2] == 'bool':
                    _bf.append(tuple(_feature))
                elif _feature[2] == 'numeric':
                    _nfr.append(tuple(_feature))

            # read dimacs properties
            elif line.startswith("p"):
                info = line.split()
                _vcount = info[2]
            # read clauses
            else:
                info = line.split()
                if len(info) != 0:
                    _clauses.append(list(map(int, info[:len(info)-1])))
                    #_clauses.append(line.strip('\n'))

    _nf = dict()

    for f in _nfr:
        data = f[1].split('_')
        if data[0] not in _nf:
            _nf[data[0]] = 0

    return _bf, _nfr, _nf, _clauses, _vcount




dimacs = "/home/jeho-lab/Dropbox/BitBlasting/Norbert/Trimesh.dimacs"
print(read_dimacs(dimacs))
