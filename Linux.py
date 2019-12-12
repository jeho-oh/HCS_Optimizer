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
