import os
import shutil

from Kclause_Smarch.Smarch.smarch import sample, read_dimacs
from kconfigIO import gen_configs, build_samples


class Kconfig:
    wdir = ""
    features = list()
    target = ""
    nfs = list()
    bfs = list()
    nfv = dict()
    fcount = 0

    def __init__(self, target_, features_, wdir_):
        self.target = target_
        self.wdir = "/home/jeho-lab/git/kconfig_case_studies/cases/" + target_ + "/nbuild/configs"
        self.features = features_

        # check vagrant is up

    def evaluate(self, samples_):

        for file in os.listdir(self.wdir):
            path = os.path.join(self.wdir, file)
            try:
                if os.path.isfile(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception as e:
                print(e)

        # create .config files
        gen_configs(self.target, self.features, samples_, self.wdir)

        # build samples
        build_samples(self.target, 'nbuild/configs')

        # check build errors
        i = 0
        file = self.wdir + "/return_codes.txt"
        with open(file) as f:
            for line in f:
                if '0' not in line:
                    i += 1

        print("Number of failed configs: " + str(i))

        # read build size reports
        file = self.wdir + "/binary_sizes.txt"
        buildsizes = list()
        with open(file, 'r') as f:
            for line in f:
                data = line.split(' ')

                if data[0] == 'binary':
                    buildsizes.append(int(data[4]))

        # create measurement set
        _measurements = list()
        i = 0
        for s in samples_:
            _m = list()

            _m.append(s)
            _m.append(buildsizes[i])

            _measurements.append(_m)
            i += 1

        return _measurements

    def evaluate_existing(self, configs):
        # build samples
        build_samples(self.target, configs)

        # read build size reports
        file = self.wdir + "/binary_sizes.txt"
        buildsizes = list()
        with open(file, 'r') as f:
            for line in f:
                data = line.split(' ')

                if data[0] == 'binary':
                    buildsizes.append(int(data[4]))

        return buildsizes


class SPLConqueror:
    target = ""
    data = list()
    nfs = list()
    bfs = list()
    nfv = dict()
    #fcount = 0

    def __init__(self, target_, features_, datafile_):
        self.target = target_
        self.features = features_

        # parse boolean and numerical features
        for f in features_:
            if f[2] == 'bool':
                self.bfs.append(f)
            elif f[2] == 'numeric':
                self.nfs.append(f)

        for f in self.nfs:
            raw = f[1].split('_')
            if raw[0] not in self.nfv:
                self.nfv[raw[0]] = 0

        #self.fcount = len(self.bfs) + len(self.nfv)

        with open(datafile_) as f:
            for line in f:
                raw = line.split('\"')
                meas = list()

                meas.append(set(raw[1].split(',')))
                mraw = raw[2][1:len(raw[2])-1].split(',')
                meas.append(tuple(map(float, mraw)))
                self.data.append(meas)

    def evaluate(self, samples):
        # create measurement set
        measurements = list()
        i = 0
        for s in samples:
            config = set()
            m = list()

            fvars = [i[0] for i in self.bfs]
            for v in fvars:
                if v in s:
                    config.add(self.bfs[v-1][1])

            nvalues = self.nfv.copy()
            for nf in self.nfs:
                if nf[0] in s:
                    raw = nf[1].split('_')
                    nvalues[raw[0]] = nvalues[raw[0]] + 2**(int(raw[1]))

            for nf in nvalues:
                if self.target == 'Dune':
                    if nf == 'cells':
                        config.add(nf + ";" + str(50 + nvalues[nf]))
                    else:
                        config.add(nf + ";" + str(nvalues[nf]))
                elif self.target == 'HSMGP':
                    if nf == 'numCore':
                        actual = [64, 256, 1024, 4096]
                        config.add(nf + ";" + str(actual[nvalues[nf]]))
                    else:
                        config.add(nf + ";" + str(nvalues[nf]))
                elif self.target == 'HiPAcc':
                    if nf == 'Blocksize':
                        actual = ['bs_32x1','bs_32x2','bs_32x4','bs_32x8','bs_32x16','bs_32x32','bs_64x1','bs_64x2','bs_64x4','bs_64x8','bs_64x16','bs_128x1','bs_128x2','bs_128x4','bs_128x8','bs_256x1','bs_256x2','bs_256x4','bs_512x1','bs_512x2','bs_1024x1']
                        config.add(actual[nvalues[nf]])
                        config.add('Blocksize')
                    elif nf == 'padding':
                        config.add(nf + ";" + str(nvalues[nf] * 32))
                    elif nf == 'pixelPerThread':
                        config.add(nf + ";" + str(nvalues[nf] + 1))
                elif self.target == 'Trimesh':
                    if nf == 'alpha' or nf == 'beta':
                        config.add(nf + ";" + str(5 * (nvalues[nf] + 1)))
                    else:
                        config.add(nf + ";" + str(nvalues[nf]))

            for d in self.data:
                if config == d[0]:
                    m.append(s)
                    m.append(d[1])
                    break

            if len(m) == 0:
                print(s)
                print(config)

            measurements.append(m)
            i += 1

        return measurements

    def get_rank(self, sample_, obj):
        sv = sample_[1][obj]
        pvs = [i[1][obj] for i in self.data]
        rank = -1

        pvs.sort()

        for i in range(0, len(pvs)):
            if sv == pvs[i]:
                rank = i / (len(pvs) - 1)
                break

        return rank

    def get_ranks(self, samples_, obj):
        svs = [i[1][obj] for i in samples_]
        pvs = [i[1][obj] for i in self.data]
        ranks = list()

        svs.sort()
        pvs.sort()

        curr = 0
        for sv in svs:
            for i in range(curr, len(pvs)):
                if sv == pvs[i]:
                    curr = i
                    ranks.append(i / (len(pvs) - 1))
                    break

        return ranks

# run script
if __name__ == "__main__":
    target = 'Dune'
    n = 100
    dimacs = "/home/jeho-lab/Dropbox/BitBlasting/Norbert/" + target + ".dimacs"
    data = "/home/jeho-lab/Dropbox/BitBlasting/Norbert/" + target + ".csv"
    wdir = os.path.dirname(dimacs) + "/smarch"

    features, clauses, vcount = read_dimacs(dimacs)
    samples = sample(vcount, clauses, n, wdir, [], False, 1, True)

    eval = SPLConqueror(target, features, data)
    measurements = eval.evaluate(samples)

    for m in measurements:
        print(m)

    ranks = eval.get_ranks(measurements, 0)

    for r in ranks:
        print(r)

