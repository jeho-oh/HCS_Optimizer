# HCS_Optimizer
Uniform sampling based optimization of highly configurable systems

## Prerequisites
* Smarch (https://github.com/jeho-oh/Smarch): required for sampling configurations
* kconfig_case_study (https://github.com/paulgazz/kconfig_case_studies): required for optimizing Kconfig based systems

Smarch python script uses following additional package: scipy.stats

## How to run
To optimize Kconfig based systems, check kconfig_case_study repository path in kconfigIO.py (variable KCONFIG)

To run the optimizer, modify following vairables in the main method of search.py and run

    target = "axtls_2_1_4"  # system name (dimacs file should be in FM folder)
    type = "Kconfig"        # system type (SPLConqueror, LVAT, or Kconfig)
    n = 30                  # number of samples per recursion
    n1 = 30                 # number of samples for initial recursion
    nrec = -1               # number of recursions (-1 for unbounded)
    obj = 0                 # objective index to optimize
    goal = (0, 0)           # goal point to optimize for MOO (check evaluation.py for setup)
    rep = 1                 # numer of repetitions to get statistics on results

## Output
The search result will be printed on the console (there is a code to output to a file, commented)
