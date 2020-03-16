import os
import sys
import getopt
from scipy.stats import tmean, tstd


def parse_info(infofile):
    data = list()

    with open(infofile, 'r') as f:
        for line in f:
            config = list()
            raw = line[:len(line)-2].split(" ")

            config.append(int(raw[4]))  # build size
            config.append(int(raw[6]))  # cve_count
            config.append(int(raw[8]))  # dirs count
            config.append(int(raw[10]))  # files count
            config.append(float(raw[16]))  # build time

            data.append(config)

    return data


def parse_const(constfile):
    const = set()

    with open(constfile, 'r') as f:
        for line in f:
            const.add(line[:len(line)-1])

    return const


def analyze_rec(recdir):
    data = parse_info(recdir + "/info.txt")
    const = parse_const(recdir + "/const.txt")

    # analysis of a recursion comes here
    dataT = list(map(list, zip(*data)))

    avgs = [tmean(d) for d in dataT]
    stds = [tstd(d) for d in dataT]
    mins = [min(d) for d in dataT]
    maxs = [max(d) for d in dataT]

    if not quiet:
        print("average: " + str(avgs))
        print("stdev: " + str(stds))
        print("max: " + str(maxs))
        print("min: " + str(mins))

    return [avgs, stds, mins, maxs, const]


def analyze_rep(repdir):
    rec = list()
    const = set()

    for root, dirs, filenames in os.walk(repdir):
        rec = dirs.copy()
        break

    #sorted(rec)

    recData = list()
    for r in range(len(rec)):
        if not quiet:
            print(">> rec"+str(r))

        res = analyze_rec(repdir + "/rec" + str(r))
        new = res[-1] - const
        print("new const: " + str(len(new)))
        const = res[-1].copy()

    # analysis of an experiment comes here


# run script
if __name__ == "__main__":
    test = False
    quiet = False

    if test:
        repdir = "/home/jeho-lab/Test/rep0"
        analyze_rep(repdir)
    else:
        # get parameters from console
        try:
            opts, args = getopt.getopt(sys.argv[1:], "ho:q", ['help', "odir=", 'quiet'])
        except getopt.GetoptError:
            print('summary.py -o <outputdir> -q | <repdir>')
            sys.exit(2)

        if len(args) < 1:
            print('summary.py -o <outputdir> -q | <repdir>')
            sys.exit(2)

        repdir = args[0]

        #  process parameters
        for opt, arg in opts:
            if opt == '-h':
                print('summary.py -o <outputdir> -q | <repdir>')
                sys.exit()
            elif opt in ("-o", "--odir"):
                wdir = arg
                out = True
                if not os.path.exists(wdir):
                    os.makedirs(wdir)
                print("File output not yet implemented")
                #print("Output directory: " + wdir)
            elif opt in ("-q", "--quiet"):
                quiet = True
            else:
                print("Invalid option: " + opt)

        analyze_rep(repdir)

