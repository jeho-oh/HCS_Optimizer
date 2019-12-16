import os
from sys import path
import time
from operator import itemgetter
import datetime
from subprocess import getoutput
from scipy.stats import tmean, tstd
import sampleLinux
root = os.path.dirname(os.path.abspath(__file__))
KUS = os.path.dirname(os.path.abspath(__file__)) + "/KUS"
path.append(root + "/Smarch")

from kconfigIO import LINUX_DIR, WORK_DIR

# from Smarch.smarch_opt import master, read_dimacs, read_constraints, gen_dimacs, checksat, count
from evalutation import Kconfig, SPLConqueror, LVAT
from analysis import get_noteworthy

def parse():
	f = open("paths.txt", "r")
	s = f.read().splitlines()
	f.close()
	return s[0], s[1],s[2],s[3]


class Searcher:
    dimacs = ''
    features = list()
    linux = LINUX_DIR
    outdir = WORK_DIR

    # clauses = list()
    # vcount = list()
    numbering = {}
    const = list()
    eval = list()
    wdir = ''
    method = ''

    def __init__(self, dimacs_, const_, eval_, linux, outdir, method_='dr'):
        self.wdir = os.path.dirname(dimacs_) + "/smarch"
        self.linux = linux
        self.numbering, self.features, = sampleLinux.read_kconfig_extract(LINUX_DIR)
        self.const = const_
        self.outdir = outdir 
        self.eval = eval_
        self.dimacs = dimacs_
        self.method = method_

    # one recursion of sampling, benchmarking, and finding noteworthy features
    def _recurse(self, n_, obj_, constraints_, added=(), goal_=(), verbose=False):
        _exhaust = False
        remaining = n_ + 1
        # remaining = count(self.dimacs, constraints_)
        if remaining < n_:
            n_ = remaining
            print("EXAUST")
            _exhaust = True

        # sample configurations with constraints
        # _samples = master(self.vcount, self.clauses, n_, self.wdir, constraints_, 6, not verbose)
        _samples = sampleLinux.sample_linux(self.linux, self.outdir, self.const, self.features, n_)
        


        # sample configurations using KUS
        # _samples = sample(self.vcount, self.clauses, n_, constraints_)
        # if not _samples:
        #     _samples = sample(self.vcount, self.clauses, n_, constraints_)

        if not _samples:
            print("Not Samples")
            return False, False, False

        # evaluate configurations
        eval_time = time.time()
        _measurements = self.eval.evaluate(_samples, goal_)
        _measurements += added
        if verbose:
            print("Evaluation time: " + str(time.time() - eval_time))

        if not _exhaust:
            # deduce noteworthy features (dynamic objective selection)
            if len(goal) != 0 and self.method == 'ff':
                data = [m[1] for m in _measurements]
                dist = list()
                for i in range(0, len(data[0])):
                    dist.append(tmean([[d[i]] for d in data]) - goal[i])
                opt = dist.index(max(dist))

                # deduce noteworthy features
                _noteworthy = get_noteworthy(self.features, _measurements, opt)
                print("get_notwworthy:")
                print(_noteworthy)
            else:
                # deduce noteworthy features(distance based)
                _noteworthy = get_noteworthy(self.features, _measurements, obj_, goal_)

            for ntw in _noteworthy:
                if -1*ntw in _noteworthy:
                    print("Error: Conflicting noteworthy")
                if ntw in constraints_:
                    print("Error: Redundant noteworthy")

            # determine termination
            if len(_noteworthy) != 0:
                return True, _noteworthy, _measurements
            else:
                return False, _noteworthy, _measurements
        else:
             return False, [], _measurements

    # filter reusable samples
    def _filter_reusable(self, measurements_, ntwf_):
        filtered = list()
        for m in measurements_:
            fit = True
            for fc in ntwf_:
                if not set(fc).issubset(m[0]):
                    fit = False
                    break

            if fit:
                filtered.append(m)
        return filtered

    # recursive search
    def srs(self, n_, obj_, rmax=-1, verbose_=True, nlimit_=-1, n1_=0, goal_=()):
        popl = set()
        rec = True
        ntwf = self.const.copy()
        r = 0
        init = True
        reusable = list()

        while rec and (rmax == -1 or r < rmax):
            if nlimit_ < 0 or len(popl) < nlimit_:
                if verbose_:
                    print(">> Recursion: " + str(r))

                if nlimit_ > 0 and nlimit_ - len(popl) < n_:
                    n_ = nlimit_ - len(popl)

                if n1_ != 0 and init:
                    rec, ntw, measurements = self._recurse(n1_, obj_, ntwf, reusable, goal_, verbose_)
                else:
                    rec, ntw, measurements = self._recurse(n_, obj_, ntwf, reusable,  goal_, verbose_)

                if not measurements:
                    return False

                ntwf = ntwf + ntw
                reusable = self._filter_reusable(measurements, ntwf)

                if verbose_:
                    print("Added noteworthy features: ", end='')# + str(ntw))
                    for ntc in ntw:
                        for f in ntc:
                            if f < 0:
                                print('-' + self.features[abs(f)-1][1], end=' ')
                            if f > 0:
                                print(self.features[abs(f)-1][1], end=' ')
                        print(',', end='')
                    print()

                    print("Accumulated noteworthy features: ", end='')# + str(ntw))
                    for ntc in ntwf:
                        for f in ntc:
                            if f < 0:
                                print('-' + self.features[abs(f)-1][1], end=' ')
                            if f > 0:
                                print(self.features[abs(f)-1][1], end=' ')
                        print(',', end='')
                    print()

                # collect measurements
                for m in measurements:
                    m[0] = tuple(m[0])
                    # t = tuple(tuple(v) for v in m)
                    popl.add(tuple(m))

                sortedlist = sorted(popl, key=itemgetter(1), reverse=False)

                if verbose_:
                    print("Recursion " + str(r) + " best: " + str(sortedlist[0][1:]))
                    # print(str(sortedlist[0][0]))

                r += 1
            else:
                break

            if init:
                print(sortedlist[0][1], end=",")

            init = False

        return popl


# run script
if __name__ == "__main__":
    target = "linux_4_17_6"  # system name (dimacs file should be in FM folder)
    type = "Kconfig"        # system type (SPLConqueror, LVAT, or Kconfig)
    n = 1               # number of samples per recursion
    n1 = 1              # number of samples for initial recursion
    nrec = -1              # number of recursions (-1 for unbounded)
    obj = 0                 # objective index to optimize
    goal = ()           # goal point to optimize for MOO (check evaluation.py for setup)
    rep = 1                # numer of repetitions to get statistics on results
    linux = LINUX_DIR
    outdir = WORK_DIR
    dimacs = root + "/FM/" + target + ".dimacs"
    constfile = root + "/trash/test.const"
    wdir = os.path.dirname(dimacs) + "/smarch"
    if not os.path.exists(wdir):
        os.makedirs(wdir)

    # features, clauses, vcount = read_dimacs(dimacs)
    numbering, features = sampleLinux.read_kconfig_extract(LINUX_DIR)
    const = ()
    if constfile != '':
        const = sampleLinux.read_constraints(constfile,features)
        #const = read_constraints(constfile, features)

    eval = ''
    if type == 'SPLConqueror':
        # data setup for SPLConqueror systems
        data = root + "/BM/" + target + ".csv"
        eval = SPLConqueror(target, features, data, goal)
    elif type == "LVAT":
        # data setup for LVAT systems
        data = root + "/BM/" + target + ".dimacs.augment"
        eval = LVAT(target, features, data)
    elif type == "Kconfig":
        # data setup for Kconfig systems (check vagrant path in kconfigIO.py)
        eval = Kconfig(target, features)
    elif type == 'Linux':
        eval = Linux(target, features)
        print("Set eval")
        exit(1)
    else:
        print("ERROR: Invalid system type")
        exit(1)

    result = list()

    # perform search r times
    for r in range(0, rep):
        res = list()

        searcher = Searcher(dimacs, const, eval, linux, outdir)
        found = searcher.srs(n, obj, nrec, verbose_=True, n1_=n1, goal_=goal)

        if not found:
            print("not found")
            r -= 1
            continue

        if len(goal) != 0:
            # sort by goal distance
            found = sorted(found, key=lambda x: x[2], reverse=False)
        else:
            # sort by objective
            found = sorted(found, key=lambda x: x[1][obj], reverse=False)

        res.append(len(found))

        for i in range(0, len(found[0][1])):
            res.append(found[0][1][i])

        if len(goal) != 0:
            # sort by goal distance
            res.append(found[0][2])

        # srank = eval.get_rank(found[0], 0, goal)
        # res.append(srank)
        #
        # urank = 1 / (len(found) + 1)
        # res.append(urank)
        #
        # if srank < urank:
        #     res.append(1)
        # else:
        #     res.append(0)

        result.append(res)

        print(res)

    # print out statistics
    avg = list()
    std = list()

    print()
    print("Stats:")
    for i in range(0, len(result[0])):
        avg.append(tmean([d[i] for d in result]))
        if len(result) > 1:
            std.append(tstd([d[i] for d in result]))
    print(avg)
    print(std)

    dt = datetime.datetime.now()
    outdir = root + "/Results/" + target + "/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    outfile = str(n1) + "_" + str(n) + "_" + str(dt.hour) + str(dt.minute) + ".out"
    
    with open(outdir + outfile, 'w') as file:
        file.write("Stats: \n")
        file.write(str(avg) + "\n")
        file.write(str(std) + "\n\n")
    
        for res in result:
            file.write(str(res) + "\n")
    
        file.close()
