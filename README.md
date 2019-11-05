# HCS_Optimizer
Uniform sampling based optimization of highly configurable systems

## Prerequisites
* Smarch (https://github.com/jeho-oh/Smarch): required for sampling configurations
* kconfig_case_study (https://github.com/paulgazz/kconfig_case_studies): required for optimizing Kconfig based systems

Smarch python script uses following additional package: scipy.stats

## How to run
To run the optimizer, modify following vairables in the main method of search.py and run

    target = "axtls_2_1_4"  # system name (dimacs file should be in FM folder)
    type = "Kconfig"        # system type (SPLConqueror, LVAT, or Kconfig)
    n = 30                  # number of samples per recursion
    n1 = 30                 # number of samples for initial recursion
    nrec = -1               # number of recursions (-1 for unbounded)
    obj = 0                 # objective index to optimize
    goal = (0, 0)           # goal point to optimize for multi objective optimization (check evaluation.py for setup)
                              setting this value to () leads to single objective optimization
    rep = 1                 # number of repetitions to get statistics on results

Following systems are currently available:
* SPLConqueror: HSMGP, BerkeleyDBC, Trimesh (no MOO)
* LVAT: fiasco, uClinux, ecos-icse11, freebsd-icse11
* Kconfig: axtls_2_1_4, toybox_0_7_5, fiasco_17_10, busybox_1_28_0, uClibc-ng_1_0_29

To optimize Kconfig based systems, check kconfig_case_study repository path in kconfigIO.py (variable KCONFIG)

The FM folder contains the dimacs files to sample configurations
The BM folder contains the benchmark data for SPLConqueror and LVAT systems

evaluation.py manages how configurations are benchmarked
analysis.py manages how noteworthy features are found for recursion

## Output
The search result will be printed on the console (there is a code to output to a file, commented)
