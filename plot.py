import os
import sys
import getopt
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from summary import analyze_exp, analyze_rep


def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


def get_curve(p1, p2):
    c = 1
    exp = 2
    x = np.linspace(p1[0], p2[0], 100)
    py = p2[1] - p1[1]
    y = list()
    for e in x:
        dx =  1 - (e - p1[0])/(p2[0] - p1[0]) * c
        #dy = (1 / (1 + math.exp(dx))) * 2 - 1
        dy = py * ((1 - dx ** 2) ** 0.5)
        #dy = py * (dx ** 2)
        y.append(p1[1] + dy)

    # a = (p2[1] - p1[1]) / (np.cosh(p2[0]) - np.cosh(p1[0]))
    # b = p1[1] - a * np.cosh(p1[0])
    # x = np.linspace(p1[0], p2[0], 100)
    # y = a * np.cosh(x) + b

    return x, y


def plot_rep(repStats, repData, ax_, color, goal, filter=()):
    ax_.grid()

    if len(filter) == 0:
        filter = list(range(len(repStats[0])))

    # # plot all samples
    for i, recData in enumerate(repData):
        if i in filter:
            c = lighten_color(color, 0.07 * (i+1) + 0.2)
            ax_.plot(recData[0], recData[1],
                     color=c, marker='o', linestyle='None', markersize=0.4)  # , label=label)

    # plot average movement
    #statsT = list(map(list, zip(*repStats)))
    statsT = repStats
    avgc = lighten_color(color, 1.2)

    fax = list()
    fay = list()
    for i in range(len(statsT[0])):
        if i in filter:
            fax.append(statsT[0][i])
            fay.append(statsT[1][i])

    ax_.plot(fax, fay,
            color=avgc, marker='o', markersize=0.01, linewidth=0.5, label=goal)

    for r in range(len(fax) - 1):
        x = fax[r + 1]
        y = fay[r + 1]
        dx = fax[r]  # - statsT[0][r]
        dy = fay[r]  # - statsT[1][r]

        ax_.annotate('', xy=(x, y), xytext=(dx, dy),
                    arrowprops=dict(width=0.1, ec=avgc, fc=avgc, lw=0.5, headwidth=2.5, headlength=2.5),
                    )

    # plot standard deviation
    stdc = lighten_color(color, 0.8)
    fminx = statsT[14]
    fminy = statsT[15]
    fmaxx = statsT[21]
    fmaxy = statsT[22]

    for r in range(len(statsT[0])):
        if r in filter:

            # cx, cy = fax[r], fay[r]
            # wx, wy = fsx[r], fsy[r]
            # ax_.plot([cx, cx + wx], [cy, cy], color=stdc, lw=0.4, )
            # ax_.plot([cx, cx - wx], [cy, cy], color=stdc, lw=0.4, )
            # ax_.plot([cx, cx], [cy, cy + wy], color=stdc, lw=0.4, )
            # ax_.plot([cx, cx], [cy, cy - wy], color=stdc, lw=0.4, )

            c = lighten_color(color, 0.07 * (r + 1) + 0.2)

            cx, cy = statsT[0][r], statsT[1][r]

            x, y = get_curve([fmaxx[r], cy], [cx, fmaxy[r]])
            ax_.plot(x, y, color=c, lw=0.4, )
            x, y = get_curve([fminx[r], cy], [cx, fminy[r]])
            ax_.plot(x, y, color=c, lw=0.4, )
            x, y = get_curve([fminx[r], cy], [cx, fmaxy[r]])
            ax_.plot(x, y, color=c, lw=0.4, )
            x, y = get_curve([fmaxx[r], cy], [cx, fminy[r]])
            ax_.plot(x, y, color=c, lw=0.4, )

    if norm:
        ax_.axis([0, 1, 0, 1])


def plot_all():
    fig, ax = plt.subplots(figsize=[5, 5], dpi=1000)
    ax.grid()

    for i, g in enumerate(goal):
        plot_rep(expStats[i], expData[i], ax, colors[i], g, (0,3,9))

    ax.legend()
    ax.set_ylabel('Set', fontsize=11)
    ax.set_xlabel('Buildsize', fontsize=11)

    fig.savefig("/home/jeho-lab/Dropbox/all.png", bbox_inches='tight')


def plot_individual():
    fig, axs = plt.subplots(1, 3, constrained_layout=True, sharey='row', sharex='col', figsize=[12, 4], dpi=1000)

    for i, g in enumerate(goal):
        plot_rep(expStats[i], expData[i], axs[i%3], colors[i], g, ())
        axs[i%3].set_title(g, fontsize=12)

        if i%3 == 0:
            axs[i%3].set_ylabel('# Unset', fontsize=11)

        #if i//3 == 1:
        axs[i%3].set_xlabel('Buildsize', fontsize=11)

    fig.savefig("/home/jeho-lab/Dropbox/individual_full.png", bbox_inches='tight')


def plot_first(expdir):
    fig, ax = plt.subplots(figsize=[5, 5], dpi=1000)

    for i, g in enumerate(goal):
        repdir = expdir + g + "-march/rep0"
        outfile = ""
        repStats, repData, repConst = analyze_rep(repdir, outfile)

        statsT = list(map(list, zip(*repStats)))

        ax.plot(statsT[0][0:1], statsT[1][0:1],
                 color=colors[i], marker='x', linestyle='None', markersize=4, label=g)

        ax.plot(repData[0][0], repData[0][1],
                 color=colors[i], marker='o', linestyle='None', markersize=0.3)  # , label=label)

    # ax.axis([1e7, 9e7, 5500, 9500])
    ax.legend()
    ax.grid()
    ax.set_ylabel('# Unset', fontsize=11)
    ax.set_xlabel('Buildsize', fontsize=11)

    fig.savefig("/home/jeho-lab/Dropbox/first.png", bbox_inches='tight')


def plot_corr():
    fig, ax = plt.subplots(figsize=[8, 4], dpi=1000)

    for i, g in enumerate(goal):
        outfile = ""

        x = [e for e in range(len(expStats[i][0]))]
        ax.plot(x, expStats[i][-2],
                 color=colors[i], marker='o', linewidth=1, markersize=2, label=g)

    ax.set_ylabel('Correlation', fontsize=11)
    ax.set_xlabel('Recursion', fontsize=11)

    ax.legend()
    ax.grid()

    fig.savefig("/home/jeho-lab/Dropbox/corr.png", bbox_inches='tight')


def plot_ntw():
    fig, ax = plt.subplots(figsize=[8, 4], dpi=1000)

    for i, g in enumerate(goal):
        outfile = ""

        x = [e for e in range(len(expConst[i]))]
        y = [len(expConst[i][j]) for j in range(len(expConst[i]))]
        ax.plot(x, y,
                 color=colors[i], marker='o', linewidth=1, markersize=2, label=g)

    ax.set_ylabel('#Features', fontsize=11)
    ax.set_xlabel('Recursion', fontsize=11)

    ax.legend()
    ax.grid()

    fig.savefig("/home/jeho-lab/Dropbox/corr.png", bbox_inches='tight')


# run script
if __name__ == "__main__":
    test = True
    quiet = True

    goal = ['0-0', '0-0.5', '0-1', 'obj1-rev-0']
    colors = ['green', 'orange', 'red', 'blue', 'purple', 'navy']

    if test:
        expdir = "/home/jeho-lab/Test/5.5.5-boot.config-"
        rep = 0
        norm = True
        expStats, expData, expConst = analyze_exp(expdir, rep, goal, norm)

        plot_all()
        # plot_first(expdir)
        # plot_individual()
        # plot_corr()
        # analyze_exp(expdir)
        plot_ntw()

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

