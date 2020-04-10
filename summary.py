import os
from scipy.stats import tmean, tstd, pearsonr, mannwhitneyu

quiet = True


def parse_info(infofile, codefile):
    data = list()
    codes = list()

    with open(codefile, 'r') as f:
        for line in f:
            if len(line) > 2:
                raw = line[:len(line)-2].split(" ")
                codes.append(int(raw[2]))

    with open(infofile, 'r') as f:
        for line in f:
            if len(line) > 2:
                if codes.pop(0) == 0:
                    config = list()
                    raw = line[:len(line)-2].split(" ")

                    config.append(float(raw[4]))  # build size
                    config.append(float(raw[14]))  # unset
                    config.append(float(raw[6]))  # cve_count
                    config.append(float(raw[8]))  # dirs count
                    config.append(float(raw[10]))  # files count
                    config.append(float(raw[12]))  # set
                    config.append(float(raw[20]))  # build time

                    data.append(config)
    return data


def parse_const(constfile):
    const = set()

    with open(constfile, 'r') as f:
        for line in f:
            const.add(line[:len(line)-1])

    return const


def analyze_rec(recdir, norm):
    data = parse_info(recdir + "/info.txt", recdir + "/return_codes.txt")
    const = parse_const(recdir + "/const.txt")

    # analysis of a recursion comes here
    dataT = list(map(list, zip(*data)))

    if norm:
        bmin = 666880
        bmax = 130029952

        stotal = 14323
        smin = 248
        smax = 11059

        umax = stotal - smin
        umin = stotal - smax

        normb = [((d - bmin)/(bmax - bmin)) for d in dataT[0]]
        #normu = [((d - umin)/(umax - umin)) for d in dataT[1]]
        normu = [((d - smin) / (smax - smin)) for d in dataT[5]]

        dataT[0] = normb.copy()
        dataT[1] = normu.copy()

    avgs = [tmean(d) for d in dataT]
    stds = [tstd(d) for d in dataT]
    mins = [min(d) for d in dataT]
    maxs = [max(d) for d in dataT]

    corr = pearsonr(dataT[0], dataT[1])

    return avgs + stds + mins + maxs + list(corr), dataT, const


def analyze_rep(repdir, outdir='', norm=False):
    rec = list()
    for root, dirs, filenames in os.walk(repdir):
        rec = dirs.copy()
        break

    repStats = list()
    repData = list()
    repConst = list()

    prevConst = set()
    for r in range(len(rec)):
        stats, data, const = analyze_rec(repdir + "/rec" + str(r), norm)
        new = const - prevConst
        prevConst = const.copy()

        repStats.append(stats)
        repData.append(data)
        repConst.append(new)

        if not quiet:
            print(">> rec"+str(r)+": ", end="")
            print(stats)
            print("new const: " + str(len(new)))

    # analysis of an experiment comes here

    # output files
    # with open(outdir + "/repStats.csv", 'w') as f:
    #     f.write("")
    #
    #     for st in repStats:
    #         f.write(str(st)[1:-1] + '\n')
    #     f.close()

    return repStats, repData, repConst


def analyze_exp(expdir, rep, goal, norm=False):
    expStats = list()
    expData = list()
    expConst = list()

    # get data
    for i, g in enumerate(goal):
        outfile = ""
        repdir = expdir + g + "/rep" + str(rep)
        repStats, repData, repConst = analyze_rep(repdir, outfile, norm)

        statsT = list(map(list, zip(*repStats)))
        expStats.append(statsT)
        expData.append(repData)
        expConst.append(repConst)

    # # initial sample consistency analysis
    # initialData = list()
    # for rep in expData:
    #     initialData.append(rep[0])#list(map(list, zip(*rep[0]))))
    #
    # for i in range(len(initialData)):
    #     for j in range(i, len(initialData)):
    #         print(goal[i] + ' vs ' + goal[j])
    #         print(mannwhitneyu(initialData[i][0], initialData[j][0]))
    #         print(mannwhitneyu(initialData[i][1], initialData[j][1]))
    #
    # allbuild = list()
    # allunset = list()
    # for i in range(len(initialData)):
    #     print(pearsonr(initialData[i][0], initialData[i][1]))
    #     allbuild += initialData[i][0]
    #     allunset += initialData[i][1]
    # print(pearsonr(allbuild, allunset))

    return expStats, expData, expConst


