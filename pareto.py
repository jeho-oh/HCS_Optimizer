from scipy.stats import beta
import matplotlib.pyplot as plt
import os

from Smarch.smarch_opt import master, read_dimacs, read_constraints
from evalutation import Kconfig, SPLConqueror

root = os.path.dirname(os.path.abspath(__file__))


def fig2(target_, obj_, goal_=()):
    def plot_n(ax_, n_):
        samples = master(vcount, clauses, n_, wdir, const, 6, True)
        data = eval.evaluate(samples)

        s1 = [d[1][1] for d in data]
        s2 = [d[1][2] for d in data]

        t1 = eval.get_values(1, False)
        t2 = eval.get_values(2, False)

        ax_.plot(t1, t2, color='gray', marker='o', linestyle='None', markersize=0.5, label='actual')
        ax_.plot(s1, s2, color='blue', marker='o', linestyle='None', linewidth=0.5, markersize=0.5,
                    label='Samples')

        ax_.set_xlabel('O1', fontsize=11)
        ax_.grid()

    dimacs = root + "/FM/" + target_ + ".dimacs"
    wdir = os.path.dirname(dimacs) + "/smarch"
    if not os.path.exists(wdir):
        os.makedirs(wdir)
    data = root + "/BM/" + target_ + ".csv"

    features, clauses, vcount = read_dimacs(dimacs)
    eval = SPLConqueror(target_, features, data, goal_)
    const = []

    fig, axs = plt.subplots(1, 6, sharey=True, sharex=True, constrained_layout=True, figsize=(20, 4))

    plot_n(axs[0], 10)
    plot_n(axs[1], 20)
    plot_n(axs[2], 50)
    plot_n(axs[3], 100)
    plot_n(axs[4], 200)
    plot_n(axs[5], 500)

    axs[0].set_title('a) N=10', fontsize=12, y=-0.3)
    axs[1].set_title('b) N=20', fontsize=12, y=-0.3)
    axs[2].set_title('c) N=50', fontsize=12, y=-0.3)
    axs[3].set_title('d) N=100', fontsize=12, y=-0.3)
    axs[4].set_title('e) N=200', fontsize=12, y=-0.3)
    axs[5].set_title('f) N=500', fontsize=12, y=-0.3)

    axs[0].legend(fontsize='9')
    axs[0].set_ylabel('O2', fontsize=11)

    fig.savefig("/home/jeho-lab/Dropbox/PCS/" + target_ + "_" +"pareto.png", bbox_inches='tight')


goal = (2500, 7000, 5)
# fig1()
fig2('HSMGP', 0, goal)
