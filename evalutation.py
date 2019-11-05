import os
import shutil
import math

from Smarch.smarch_opt import master, read_dimacs
from kconfigIO import gen_configs, build_samples, KCONFIG

root = os.path.dirname(os.path.abspath(__file__))


def get_distance(p1, p2):
    dist = 0
    for i in range(0, len(p1)):
        dist += (p1[i] - p2[i]) ** 2
    dist = math.sqrt(dist)

    return dist


class Kconfig:
    wdir = ""
    features = list()
    target = ""
    nfs = list()
    bfs = list()
    nfv = dict()
    fcount = 0

    def __init__(self, target_, features_):
        self.target = target_
        self.wdir = KCONFIG + '/cases/' + target_ + "/nbuild/configs"
        self.features = features_

        if not os.path.exists(self.wdir):
            os.makedirs(self.wdir)

        # check vagrant is up

    def evaluate(self, samples_, goal_=()):

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
        failed = list()
        file = self.wdir + "/return_codes.txt"
        with open(file) as f:
            for line in f:
                if '0' not in line:
                    failed.append(i)
                i += 1

        # exit if failed build exists
        if len(failed) != 0:
            print("Failed configs: " + str(failed))
            exit(1)

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

            # configuration
            _m.append(s)

            # number of unselected features
            unset = 0
            for v in s:
                if v < 0:
                    unset += 1

            # build size
            data = (buildsizes[i] / 1000, unset / 2)
            _m.append(data)

            # goal distance
            if len(goal_) != 0:
                _m.append(get_distance(data, goal_))

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

    def __init__(self, target_, features_, datafile_, goal_=()):
        self.target = target_
        self.features = features_

        # parse boolean and numerical features
        for f in features_:
            if f[2] == 'bool' or f[2] == 'alt':
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

                # HSMGP scale
                # d1 = float(mraw[0]) / 10
                # d2 = float(mraw[1]) / 100
                # bm = (d1, d2, float(mraw[2]))

                # BerkeleyDBC scale
                # d1 = float(mraw[0]) * 50
                # d2 = float(mraw[1]) / 100
                # bm = (d1, d2)

                bm = tuple(map(float, mraw))

                meas.append(bm)

                if len(goal_) != 0:
                    dist = 0
                    for i in range(0, len(bm)):
                        dist += (goal_[i] - bm[i]) ** 2
                    dist = math.sqrt(dist)
                    meas.append(dist)

                self.data.append(meas)

    def evaluate(self, samples_, goal_=()):
        # create measurement set
        _measurements = list()

        for s in samples_:
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

                    if len(goal_) != 0:
                        dist = 0
                        for i in range(0, len(goal_)):
                            dist += (goal_[i] - d[1][i]) ** 2
                        dist = math.sqrt(dist)
                        m.append(dist)
                    break

            if len(m) == 0:
                print(s)
                print(config)

            _measurements.append(m)

        return _measurements

    def get_rank(self, sample_, obj, goal_=()):
        if len(goal_) != 0:
            sv = sample_[2]
            pvs = [i[2] for i in self.data]
        else:
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

    # def print_normalized(self):
    #     values = [i[1][0] for i in self.data]
    #
    #     values.sort()
    #
    #     with open(res, 'w') as file:
    #         for i in range(len(values)-1, len(values)):
    #             x = i / (len(values)-1)
    #             y = (values[i] - values[0]) / (values[len(values)-1] - values[0])
    #             #if i % 10 == 0:
    #             print(str(x) + "," + str(y) + "\n")
    #
    #         file.close()

    def get_values(self, obj_, sort):
        if obj_ < 0:
            values = [i[2] for i in self.data]
        else:
            values = [i[1][obj_] for i in self.data]

        if sort:
            values.sort()

        return values


class LVAT:
    attr = list()
    features = list()

    def __init__(self, target_, features_, datafile_):
        with open(datafile_, 'r') as f:
            for line in f:
                raw = line.split(' ')
                self.attr.append(tuple(map(float, raw)))

        self.features = features_

    def evaluate(self, samples_, goal=()):
        _measurements = list()

        for s in samples_:
            m = list()
            perf = [0, 0, 0, 0]

            for v in s:
                if not self.features[abs(v)-1][1].startswith('_X'):
                    if v > 0:
                        for i in range(0, 3):
                            perf[i] = perf[i] + self.attr[v-1][i]
                    else:
                        perf[3] = perf[3] + 1

            perf[0] /= 100
            perf[1] /= 10
            perf[3] /= 10

            m.append(s)
            m.append(tuple(perf))

            if len(goal) != 0:
                dist = 0
                for i in range(0, len(goal)):
                    dist += (goal[i] - perf[i]) ** 2
                dist = math.sqrt(dist)
                m.append(dist)

            _measurements.append(m)

        return _measurements


# run script
if __name__ == "__main__":
    target = 'fiasco'
    n = 5
    dimacs = root + "/FM/" + target + ".dimacs"
    data = root + "/BM/" + target + ".dimacs.augment" #root + "/BM/" + target + ".txt"
    wdir = os.path.dirname(dimacs) + "/smarch"
    const = list()

    features, clauses, vcount = read_dimacs(dimacs)
    samples = master(vcount, clauses, n, wdir, const, 6, False)

    eval = LVAT(target, features, data)
    measurements = eval.evaluate(samples, (0,0,0,0))

    #eval.print_normalized()
    #
    for m in measurements:
        print(m)

    # ranks = eval.get_ranks(measurements, 0)
    #
    # #eval.get_pURS(0.1)
    #
    # i = 1
    # for r in ranks:
    #     print(str(i/(n+1)) + " " + str(r))
    #     i += 1

