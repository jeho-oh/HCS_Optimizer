import os
import time
from operator import itemgetter
import datetime

from scipy.stats import pearsonr

from Kclause_Smarch.Smarch.smarch import sample, read_dimacs, read_constraints
from evalutation import Kconfig, SPLConqueror
from analysis import get_noteworthy

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
    target = "HiPAcc"
    n = 66
    rec = 1
    obj = [1]
    rep = 97

    #dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
    dimacs = "/home/jeho-lab/BitBlasting/Norbert/" + target + ".dimacs"
    #dimacs = "/home/jeho-lab/BitBlasting/Kconfig_numerical/" + target + ".dimacs"
    const = ''#os.path.dirname(dimacs) + "/" + target + ".const"
    wdir = os.path.dirname(dimacs) + "/smarch"
    data = "/home/jeho-lab/Dropbox/BitBlasting/Norbert/" + target + ".csv"

    features, clauses, vcount = read_dimacs(dimacs)
    eval = SPLConqueror(target, features, data)
    #eval = Kconfig(target, features, wdir)

    dt = datetime.datetime.now()
    out = os.path.dirname(dimacs) + "/" + target + "_" + str(rec) + "_" + str(dt.hour) + str(dt.minute) + ".out"
    with open(out, 'w') as file:
        for i in range(0, rep):
            searcher = Searcher(dimacs, const, eval)
            result = searcher.srs(n, obj, rec, False, 200)
            result = sorted(result, key=itemgetter(1), reverse=False)
            #print("Best: " + str(result[0][1]))


            srank = eval.get_rank(result[0], 0)
            urank = 1 / (len(result)+1)
            res = ""
            res += str(len(result)) + ","
            res += str(result[0][1][0]) + ","
            res += str(srank) + ","
            res += str(urank) + ","
            if srank < urank:
                res += "1"
            else:
                res += "0"

            print(res)
            file.write(res + "\n")

    file.close()

