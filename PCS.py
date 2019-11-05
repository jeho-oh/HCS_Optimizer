from scipy.stats import beta
import matplotlib.pyplot as plt
import os

from Smarch.smarch_opt import master, read_dimacs
from evalutation import Kconfig, SPLConqueror
from search import sample

root = os.path.dirname(os.path.abspath(__file__))


def extimate_x(n_, c_):

    _xmin = list()
    _xmean = list()
    _xmax = list()

    for k in range(1, n_ + 1):
        a = k
        b = n_ + 1 - k

        _xmin.append(beta.ppf(c_, a, b))
        _xmean.append(beta.mean(a, b))
        _xmax.append(beta.ppf(1 - c_, a, b))

    return _xmin, _xmean, _xmax


def fig1():
    x = range(1, 11)
    x = [i/(len(x)+1) for i in x]
    xmin, xmean, xmax = extimate_x(len(x), 0.025)
    yh = [xmax[i] - xmean[i] for i in range(0, len(x))]
    yl = [xmin[i] - xmean[i] for i in range(0, len(x))]
    plt.plot(x, yh, color='navy', marker='o', linestyle='dashed', linewidth=0.7, markersize=2, label='N=10')
    plt.plot(x, yl, color='navy', marker='o', linestyle='dashed', linewidth=0.7, markersize=2)

    x = range(1, 51)
    x = [i/(len(x)+1) for i in x]
    xmin, xmean, xmax = extimate_x(len(x), 0.025)
    yh = [xmax[i] - xmean[i] for i in range(0, len(x))]
    yl = [xmin[i] - xmean[i] for i in range(0, len(x))]
    plt.plot(x, yl, color='blue', marker='o', linestyle='dashed', linewidth=0.7, markersize=2, label='N=50')
    plt.plot(x, yh, color='blue', marker='o', linestyle='dashed', linewidth=0.7, markersize=2)

    x = range(1, 101)
    x = [i/(len(x)+1) for i in x]
    xmin, xmean, xmax = extimate_x(len(x), 0.025)
    yh = [xmax[i] - xmean[i] for i in range(0, len(x))]
    yl = [xmin[i] - xmean[i] for i in range(0, len(x))]
    plt.plot(x, yl, color='cyan', marker='o', linestyle='dashed', linewidth=0.7, markersize=2, label='N=100')
    plt.plot(x, yh, color='cyan', marker='o', linestyle='dashed', linewidth=0.7, markersize=2)

    x = range(1, 1001)
    x = [i/(len(x)+1) for i in x]
    xmin, xmean, xmax = extimate_x(len(x), 0.025)
    yh = [xmax[i] - xmean[i] for i in range(0, len(x))]
    yl = [xmin[i] - xmean[i] for i in range(0, len(x))]
    plt.plot(x, yl, color='lightblue', marker='o', linestyle='dashed', linewidth=0.7, markersize=2, label='N=1000')
    plt.plot(x, yh, color='lightblue', marker='o', linestyle='dashed', linewidth=0.7, markersize=2)
    #plt.plot(xmean, y, color='red', linewidth=1, label='Actual')

    #plt.title('95% prediction interval for different N')
    plt.xlabel('Normalized rank')
    plt.ylabel('95% prediction interval around mean (y=0)')
    plt.legend()
    plt.grid()

    plt.savefig("/home/jeho-lab/Dropbox/PCS/fig1.png", bbox_inches='tight')


def fig2(target_, obj_, goal_=()):
    def plot_n(ax_, n_):
        # samples = master(vcount, clauses, n_, wdir, const, 6, True)
        samples = sample(vcount, clauses, n_, const)
        data = eval.evaluate(samples)

        if obj_ < 0:
            sy = [d[2] for d in data]
        else:
            sy = [d[1][obj_] for d in data]
        sy.sort()

        sxmin, sxmean, sxmax = extimate_x(len(sy), 0.025)

        ax_.plot(sxmin, sy, color='blue', marker='', linestyle='dashed', linewidth=0.5, markersize=2,
                    label='95% interval')
        ax_.plot(sxmax, sy, color='blue', marker='', linestyle='dashed', linewidth=0.5, markersize=2)
        ax_.plot(sxmean, sy, color='blue', marker='x', linestyle='None', markersize=4, label='estimation mean')

        # plot acutal PCS graph
        # ax_.plot(tx, ty, color='red', marker='.', linestyle='None', markersize=1, label='actual')

        ax_.set_xlabel('Normalized Rank', fontsize=11)
        ax_.grid()

    dimacs = root + "/FM/" + target_ + ".dimacs"
    wdir = os.path.dirname(dimacs) + "/smarch"
    if not os.path.exists(wdir):
        os.makedirs(wdir)
    data = root + "/BM/" + target_ + ".csv"

    features, clauses, vcount = read_dimacs(dimacs)
    eval = SPLConqueror(target_, features, data, goal_)
    const = []

    # get true PCS graph
    # ty = eval.get_values(obj_, True)
    # tx = range(0,len(ty))
    # tx = [x / len(ty) for x in tx]

    fig, axs = plt.subplots(1, 6, sharey=True, sharex=True, constrained_layout=True, figsize=(20, 4))

    plot_n(axs[0], 100)
    plot_n(axs[1], 200)
    plot_n(axs[2], 500)
    plot_n(axs[3], 1000)
    plot_n(axs[4], 2000)
    plot_n(axs[5], 5000)

    axs[0].set_title('a) N=10', fontsize=12, y=-0.3)
    axs[1].set_title('b) N=20', fontsize=12, y=-0.3)
    axs[2].set_title('c) N=50', fontsize=12, y=-0.3)
    axs[3].set_title('d) N=100', fontsize=12, y=-0.3)
    axs[4].set_title('e) N=200', fontsize=12, y=-0.3)
    axs[5].set_title('f) N=500', fontsize=12, y=-0.3)

    axs[0].legend(fontsize='9')
    axs[0].set_ylabel('Performance', fontsize=11)

    fig.savefig("/home/jeho-lab/Dropbox/PCS/" + target_ + "_" + str(obj_) + ".png", bbox_inches='tight')


goal = (2500, 7000, 5)
# fig1()
fig2('Trimesh', 0, goal)
