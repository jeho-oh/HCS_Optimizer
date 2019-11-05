import os
import time
from operator import itemgetter
import datetime
from subprocess import getoutput
from scipy.stats import tmean, tstd

from Smarch.smarch_opt import master, read_dimacs, read_constraints, gen_dimacs, checksat, count
from evalutation import Kconfig, SPLConqueror, LVAT
from analysis import get_noteworthy

root = os.path.dirname(os.path.abspath(__file__))
KUS = os.path.dirname(os.path.abspath(__file__)) + "/KUS"


def sample(vcount_, clauses_, n_, constraints_):
    """ Sample configurations using KUS (unstable) """
    _samples = list()
    _tempdimacs = KUS + "/temp.cnf"

    if os.path.isfile(_tempdimacs):
        os.remove(_tempdimacs)

    if os.path.isfile(_tempdimacs + '.nnf'):
        os.remove(_tempdimacs + '.nnf')

    if os.path.isfile(KUS + "/samples.txt"):
        os.remove(KUS + "/samples.txt")

    gen_dimacs(vcount_, clauses_, constraints_, _tempdimacs)

    remaining = count(_tempdimacs, [])
    if remaining < n_:
        n_ = remaining

    res = getoutput('python ' + KUS + '/KUS.py --samples ' + str(n_) + ' ' + _tempdimacs)
    #print(res)

    with open(KUS + "/samples.txt") as f:
        for line in f:
            raw = line.split(',')[1].split(' ')
            sol = {int(v) for v in raw[1:len(raw)-1]}
            if not checksat(_tempdimacs, [[s] for s in sol]):
                print("Samplie invalid")
                return False
            _samples.append(sol)

    return _samples


class Searcher:
    dimacs = ''
    features = list()
    clauses = list()
    vcount = list()
    const = list()
    eval = list()
    wdir = ''
    method = ''

    def __init__(self, dimacs_, const_, eval_, method_='ff'):
        self.wdir = os.path.dirname(dimacs_) + "/smarch"

        self.features, self.clauses, self.vcount = read_dimacs(dimacs_)
        self.const = const_

        self.eval = eval_
        self.dimacs = dimacs_
        self.method = method_

    # one recursion of sampling, benchmarking, and finding noteworthy features
    def _recurse(self, n_, obj_, constraints_, added=(), goal_=(), verbose=False):
        _exhaust = False

        remaining = count(self.dimacs, constraints_)
        if remaining < n_:
            n_ = remaining
            _exhaust = True

        # sample configurations with constraints
        _samples = master(self.vcount, self.clauses, n_, self.wdir, constraints_, 6, not verbose)

        # sample configurations using KUS
        # _samples = sample(self.vcount, self.clauses, n_, constraints_)
        # if not _samples:
        #     _samples = sample(self.vcount, self.clauses, n_, constraints_)

        if not _samples:
            return False, False, False

        # evaluate configurations
        eval_time = time.time()
        _measurements = self.eval.evaluate(_samples, goal_)
        _measurements += added
        if verbose:
            print("Evaluation time: " + str(time.time() - eval_time))

        if not _exhaust:
            # deduce noteworthy features (dynamic objective selection)
            if len(goal) != 0 and self.method == 'dr':
                data = [m[1] for m in _measurements]
                dist = list()
                for i in range(0, len(data[0])):
                    dist.append(tmean([[d[i]] for d in data]) - goal[i])
                opt = dist.index(max(dist))

                # deduce noteworthy features
                _noteworthy = get_noteworthy(self.features, _measurements, opt)
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
    def srs(self, n_, obj_, rmax=-1, verbose_=False, nlimit_=-1, n1_=0, goal_=()):
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

                    # print("Accumulated noteworthy features: ", end='')# + str(ntw))
                    # for ntc in ntwf:
                    #     for f in ntc:
                    #         if f < 0:
                    #             print('-' + self.features[abs(f)-1][1], end=' ')
                    #         if f > 0:
                    #             print(self.features[abs(f)-1][1], end=' ')
                    #     print(',', end='')
                    # print()

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
    target = "axtls_2_1_4"  # system name (dimacs file should be in FM folder)
    type = "Kconfig"        # system type (SPLConqueror, LVAT, or Kconfig)
    n = 30                  # number of samples per recursion
    n1 = 30                 # number of samples for initial recursion
    nrec = -1               # number of recursions (-1 for unbounded)
    obj = 0                 # objective index to optimize
    goal = (0, 0)           # goal point to optimize for MOO (check evaluation.py for setup)
    rep = 1                 # numer of repetitions to get statistics on results


    dimacs = root + "/FM/" + target + ".dimacs"
    constfile = root + "/FM/" + target + ".const"
    wdir = os.path.dirname(dimacs) + "/smarch"
    if not os.path.exists(wdir):
        os.makedirs(wdir)

    features, clauses, vcount = read_dimacs(dimacs)
    const = ()
    if constfile != '':
        const = read_constraints(constfile, features)

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
    else:
        print("ERROR: Invalid system type")
        exit(1)

    result = list()

    # perform search r times
    for r in range(0, rep):
        res = list()

        searcher = Searcher(dimacs, const, eval)
        found = searcher.srs(n, obj, nrec, verbose_=False, n1_=n1, goal_=goal)

        if not found:
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

    # dt = datetime.datetime.now()
    # outdir = root + "/Results/" + target + "/"
    # if not os.path.exists(outdir):
    #     os.makedirs(outdir)
    # outfile = str(n1) + "_" + str(n) + "_" + str(dt.hour) + str(dt.minute) + ".out"
    #
    # with open(outdir + outfile, 'w') as file:
    #     file.write("Stats: \n")
    #     file.write(str(avg) + "\n")
    #     file.write(str(std) + "\n\n")
    #
    #     for res in result:
    #         file.write(str(res) + "\n")
    #
    #     file.close()
