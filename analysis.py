from scipy.stats import ttest_ind


# find noteworthy features from benchmarked samples
def get_noteworthy(measurements, obj_):
    noteworthy = list()

    if len(measurements) > 1:
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
                res = welch_t(in_measure, ex_measure, 0.95)

                if res:
                    found = list()
                    found.append(c)
                    noteworthy.append(found)

    return noteworthy


# perform Welch's t-test to check noteworthiness
def welch_t(pos, neg, pval):
    stat, pvalue = ttest_ind(pos, neg, equal_var=False)

    if stat < 0 and pvalue < (1-pval):
        return True
    else:
        return False


# perform bootstrapping to check noteworthiness
def bootstrap(pos, neg, pval):
    better = 0

    for pv in pos:
        for nv in neg:
            if pv < nv:
                better += 1

    ratio = better / len(pos) * len(neg)

    if ratio >= pval:
        return True
    else:
        return False


file = ""

data0 = list()
data1 = list()
with open(file, 'r') as f:
    for line in f:
        raw = line.split(",")
        data0.append(float(raw[0]))
        data1.append(float(raw[1]))

bootstrap()