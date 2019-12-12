class Lsearcher:
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

       # remaining = count(self.dimacs, constraints_)
        remaining = 100
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

