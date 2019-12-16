from scipy.stats import ttest_ind, mannwhitneyu, tmean
import math


def get_distance(p1, p2):
    dist = 0
    for i in range(0, len(p1)):
        dist += (p1[i] - p2[i]) ** 2
    dist = math.sqrt(dist)

    return dist


# perform bootstrapping to check noteworthiness
def bootstrap(pos, neg, pval):
    better = 0

    for pv in pos:
        for nv in neg:
            if pv < nv:
                better += 1

    ratio = better / (len(pos) * len(neg))

    if ratio >= pval:
        return True
    else:
        return False


# perform Welch's t-test to check noteworthiness
def welch_t(pos, neg, cl):
    stat, pvalue = ttest_ind(pos, neg, equal_var=False)

    if stat < 0 and pvalue < (1 - cl):
        return True
    else:
        return False


# perform Mann-Whitney U test to check noteworthiness
def u_test(pos, neg, cl):
    stat, pvalue = mannwhitneyu(pos, neg, alternative='less')

    if pvalue < (1 - cl):
        return True
    else:
        return False


# find noteworthy features from benchmarked samples
def get_noteworthy(features_, measurements_, obj_, goal=()):
    _noteworthy = list()
    common = list()

    if len(measurements_) > 1:
        print("Len measurements > 1")
        if len(goal) != 0:
            print("sorting by goal distance")
            # sort by goal distance
            sortedlist = sorted(measurements_, key=lambda x: x[2], reverse=False)

            mindist = 0
            second = list()
            for i in range(1, len(sortedlist)):
                dist = get_distance(sortedlist[0][1], sortedlist[i][1])
                if i == 1:
                    mindist = dist
                    second = sortedlist[i][0]
                elif dist < mindist:
                    mindist = dist
                    second = sortedlist[i][0]

            # find common features from best two measurements
            common = list(set(sortedlist[0][0]).intersection(second))
            print("lenght of common..",end=" ")
            print(len(common))

        else:
            print("sorting by objective")
            # sort by objective
            sortedlist = sorted(measurements_, key=lambda x: x[1][obj_], reverse=False)

            # find common features from best two measurements
            common = list(set(sortedlist[0][0]).intersection(sortedlist[1][0]))
            print("lenght of common..",end=" ")
            print(len(common))
            common_on = 0
            for c in common:
                if c > 0:
                    common_on += 1
            print("Number of common features that arent off " + str(common_on))

        # print("printing common: ",end='')
        # for c in common:
        #     if c > 0:
        #         print(features_[abs(c)-1][1], end=",")
        #     else:
        #         print('-' + features_[abs(c) - 1][1], end=",")
        # print()

        # check noteworthiness of common features
        for c in common:
            in_measure = list()
            ex_measure = list()
            for m in measurements_:
                if len(goal) != 0:
                    if c in m[0]:
                        in_measure.append(m[2])
                    else:
                        ex_measure.append(m[2])
                else:
                    if c in m[0]:
                        #print("c in m[0]")
                        in_measure.append(m[1][obj_])
                    else:
                        ex_measure.append(m[1][obj_])

            if len(in_measure) > 1 and len(ex_measure) > 1:
                if tmean(in_measure) < tmean(ex_measure):
                    res_w = welch_t(in_measure, ex_measure, 0.3)
                    res_bs = bootstrap(in_measure, ex_measure, 0.3)
                    res_u = u_test(in_measure, ex_measure, 0.3)

                    if res_w or res_bs or res_u:
                        found = list()
                        found.append(c)
                        _noteworthy.append(found)
    # for c in _noteworthy:
    #     if c[0] > 0:
    #         print(features_[abs(c[0])-1][1], end=",")
    #     else:
    #         print('-' + features_[abs(c[0]) - 1][1], end=",")
    # print()

    # filter selection of alternative features
    filtered = list()
    # print("len ntw after filtered")
    # print(len(_noteworthy))
    for ntw in _noteworthy:
        if len(ntw) == 1:
            if len(features_[abs(ntw[0])-1]) > 2:
                if features_[abs(ntw[0])-1][2] == 'choice_bool' or features_[abs(ntw[0])-1][2] == 'alt':
                    if ntw[0] < 0:
                        filtered.append(ntw)
                else:
                    filtered.append(ntw)
            else:
                if ntw[0] < 0 and not features_[abs(ntw[0])-1][1].startswith('_X'):
                    filtered.append(ntw)

    # print(noteworthy, end=';')

    return filtered


if __name__ == "__main__":
    file = ""
