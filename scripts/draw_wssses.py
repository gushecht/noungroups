import plac

import matplotlib.pyplot as plt

from os import path


@plac.annotations(
    in_loc=('Location of input file'),
    out_loc=('Location to save output file')
)
def main(in_loc, out_loc):
    # Empty lists for values of k and corresponding WSSSEs
    ks = []
    WSSSEs = []

    with open(in_loc, 'r') as f:
        # Iterate through lines in file, adding k and WSSSE values to lists
        for line in f:
            line = line.split()
            ks.append(int(line[0]))
            WSSSEs.append(float(line[1]))

    # Plot and save figure
    plt.plot(ks, WSSSEs)
    plt.savefig(path.join(out_loc, 'WSSSEs.png'),
                bbox_inches='tight')

if __name__ == '__main__':
    plac.call(main)
