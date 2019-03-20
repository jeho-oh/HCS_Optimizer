import os
import time
from operator import itemgetter

from scipy.stats import ttest_ind, pearsonr

from Kclause_Smarch.Smarch.smarch import sample, read_dimacs, read_constraints
from evalutation import Kconfig, SPLConqueror


# find noteworthy features from benchmarked samples
def get_noteworthy(measurements, obj_):
    noteworthy = list()

    # sort by objective
    sortedlist = sorted(measurements, key=itemgetter(obj_), reverse=False)

    # find common features from best two measurements
    common = list(set(sortedlist[0][0]).intersection(sortedlist[1][0]))

    # check noteworthiness of common features
    for c in common:
        in_measure = list()
        ex_measure = list()

        for m in measurements:
            if c in m[0]:
                in_measure.append(m[obj_])
            else:
                ex_measure.append(m[obj_])

        if len(in_measure) > 1 and len(ex_measure) > 1:
            stat, pvalue = ttest_ind(in_measure, ex_measure, equal_var=False)

            if stat < 0 and pvalue < 0.05:
                found = list()
                found.append(c)
                noteworthy.append(found)

    return noteworthy


class Searcher:
    features = list()
    clauses = list()
    vcount = list()
    const = list()
    eval = list()
    wdir = ''

    def __init__(self, dimacs_, constfile_, eval_):
        self.wdir = os.path.dirname(dimacs_) + "/smarch"

        self.features, self.clauses, self.vcount = read_dimacs(dimacs_)
        if constfile_ != '':
            self.const = read_constraints(constfile_, self.features)

        self.eval = eval_

    # one recursion of sampling, benchmarking, and finding noteworthy features
    def _recurse(self, n_, obj_, constraints, added=(), verbose=False):
        # sample configurations with constraints
        _samples = sample(self.vcount, self.clauses, n_, self.wdir, constraints, False, 1, not verbose)

        # evaluate configurations
        eval_time = time.time()
        _measurements = self.eval.evaluate(_samples)
        _measurements += added
        #print("Evaluation time: " + str(time.time() - eval_time))

        # deduce noteworthy features
        _noteworthy = get_noteworthy(_measurements, obj_)

        for n in _noteworthy:
            if -1*n in _noteworthy:
                print("WTF")
            if n in constraints:
                print("WTF")

        # determine termination
        if len(_noteworthy) != 0:
            return True, _noteworthy, _measurements
        else:
            return False, _noteworthy, _measurements

    # filter reusable samples
    def _filter_reusable(self, measurements_, ntwf_):
        filtered = list()
        m = set()
        for m in measurements_:
            if ntwf_ in m[0]:
                filtered.append(m)
        return m

    # recursive search
    def srs(self, n_, objs, rmax=-1, verbose_=False, nlimit_=-1):
        popl = set()

        if len(objs) > 1:
            # sample initial configurations with constraints
            initsamples = sample(self.vcount, self.clauses, n_, self.wdir, self.const, False, 1, not verbose_)

            # benchmark configurations
            measurements = self.eval.evaluate(initsamples)

            # collect measurements
            for m in measurements:
                m[0] = tuple(m[0])
                # t = tuple(tuple(v) for v in m)
                popl.add(tuple(m))

            tobj = objs.copy()
            # check correlation between objectives for grouping
            for i in range(0, len(objs)):
                for j in range(i+1, len(objs)):
                    x = [j[i] for j in measurements]
                    y = [k[j] for k in measurements]
                    corr, pvalue = pearsonr(x, y)

                    # group objectives if correlation is larger than 0.8
                    if corr > 0.8:
                        tobj.remove(y)
            objs = tobj.copy()

        for o in objs:
            rec = True
            ntwf = self.const.copy()
            r = 0
            init = True
            reusable = list()

            while rec and (rmax == -1 or r < rmax):
                if nlimit_ < 0 or len(popl) < nlimit_:
                    if nlimit_ > 0 and nlimit_ - len(popl) < n_:
                        n_ = nlimit_ - len(popl)

                    rec, ntw, measurements = self._recurse(n_, o, ntwf, reusable, verbose_)
                    ntwf = ntwf + ntw

                    # do another recursion when first recursion finds nothing
                    if init:
                        if rec is False:
                            rec = True
                            reusable = measurements.copy()
                        init = False
                    else:
                        reusable.clear()

                    if verbose_:
                        print(">> Recursion: " + str(r))
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
                        print(str(sortedlist[0][0]))

                    r += 1
                else:
                    break

        return popl


# run script
if __name__ == "__main__":
    target = "fiasco_17_10"
    n = 100
    obj = [1]
    rep = 1

    #dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
    #dimacs = "/home/jeho-lab/BitBlasting/Norbert/" + target + ".dimacs"
    dimacs = "/home/jeho-lab/BitBlasting/Kconfig_numerical/" + target + ".dimacs"
    const = os.path.dirname(dimacs) + "/" + target + ".const"
    wdir = os.path.dirname(dimacs) + "/smarch"
    data = "/home/jeho-lab/Dropbox/BitBlasting/Norbert/" + target + ".csv"

    features, clauses, vcount = read_dimacs(dimacs)
    #eval = SPLConqueror(target, features, data)
    eval = Kconfig(target, features, wdir)

    for i in range(0, rep):

        searcher = Searcher(dimacs, const, eval)

        result = searcher.srs(n, obj, 1, True, 100)

        #print()
        #print("<<Search results>>")
        #print("N: " + str(len(result)))
        print(str(len(result)), end=',')
        result = sorted(result, key=itemgetter(1), reverse=False)
        print("Best: " + str(result[0][1:]))
        #print(str(result[0][0]))
        #print(eval.get_rank(result[0], 0))

