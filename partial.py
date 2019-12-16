import subprocess
from random import randint
def randconfig(linux_):
    cmd = "cd " + linux_ + "&& make randconfig"
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_, stderr_ = sp.communicate()
    if sp.returncode !=0:
        print("Error running make randconfig")
        exit(1)
    return linux_ + ".config"
    
def sample_constraints(config_, out_, prob):
    constraints = list()

    with open(config_, 'r') as f:
        for line in f:
            select = randint(1,prob)
            if select != 1:
                continue
            # line: # FEATURE is not set
            if line.startswith('#'):
                line = line[0:len(line) - 1]
                data = line.split()
                if len(data) > 4 and data[1].startswith('CONFIG'):
                    constraints.append('!' + data[1])
            else:
                line = line[0:len(line) - 1]
                data = line.split('=')
                if len(data) > 1:
                    if data[1] == 'y' and data[0].startswith('CONFIG'):
                        constraints.append(data[0])
    with open(out_, "w") as out:
            for constraint in constraints:
                    out.write(constraint + "\n")



if __name__ == "__main__":
    for i in range(1000):
        config_ = randconfig("/media/space/elkdat/linux/")
        prob = randint(1,1330)
        sample_constraints(config_, "/tmp/testrand/" + str(i) + ".const", prob )