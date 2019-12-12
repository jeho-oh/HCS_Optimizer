import random

return_code_template = "return code 0"

def gen(Num, _dir):
    binary_sizes = list()
    return_codes = list()

    for i in range(Num):
        r = random.randint(772680,14615592)
        binary_sizes.append(r)
    with open(_dir + "binary_sizes.txt", "w") as f:
        for bs in binary_sizes:
            f.write('binary size (in bytes): ' + str(bs) + '\n')
    with open(_dir + "return_codes.txt", "w") as f:
        for i in range(Num):
            f.write('return code 0\n')

