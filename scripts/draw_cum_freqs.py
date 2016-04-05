import plac
import logging


from ast import literal_eval as make_tuple
import matplotlib.pyplot as plt

from os import path

stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
             'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
             'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
             'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
             'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
             'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
             'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
             'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
             'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
             'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
             'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
             'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

logger = logging.getLogger(__name__)

@plac.annotations(
    in_loc=('Location of input file'),
    out_loc=('Location to save output file')
)
def main(in_loc, out_loc):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    # Counter to count lines
    counter = 0
    # Array to store cumulative frequencies, start at 0 for no nouns
    cum_freqs_1000 = [0]
    # Empty array to store nouns
    nouns_1000 = []

    with open(in_loc, 'r') as f:
        # Use to sum frequencies
        cum_freq = 0.0
        for line in f:
            line = make_tuple(line)
            # Add frequency
            if line[0].split('|')[0].lower() not in stopwords:
                cum_freq += float(line[1])
                # If this is the 1000th word (also includes the 1st)
                if counter % 1000 == 0:
                    # Add cumulative frequency to array
                    cum_freqs_1000.append(cum_freq)
                    # Add word to array
                    nouns_1000.append(line[0])
                if counter % 10000 == 0:
                    logger.info('At word %i', counter)
            # Increment counter
            counter += 1
    print 'Total nouns:', str(counter)

    # Create x-axis array that counts 1000s of nouns
    x = xrange(len(cum_freqs_1000))
    # Plot and save figure
    plt.plot(x, cum_freqs_1000)
    plt.savefig(path.join(out_loc, 'cumulative_frequencies.png'),
                bbox_inches='tight')

    # Write nouns to file
    with open(path.join(out_loc, 'nouns_1000.txt'), 'w') as f:
        for noun in nouns_1000:
            f.write(noun + '\n')

if __name__ == '__main__':
    plac.call(main)
