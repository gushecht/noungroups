import plac
import logging

from gensim.models import Word2Vec

logger = logging.getLogger(__name__)

@plac.annotations(
    noun_file_loc=('Path to list of nouns'),
    model_file_loc=('Path to saved Word2Vec model'),
    percent=('Percent of nouns to cluster')
)
def main(noun_file_loc, model_file_loc, percent, n_trials, out_files_loc):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    logger.info('Loading Word2Vec model')
    # Load trained Word2Vec model
    model = Word2Vec.load(model_file_loc)

    logger.info('Reading in list of nouns')
    # Read in list of sorted nouns
    sorted_nouns = []
    with open(noun_file_loc, 'r') as f:
        for line in f:
            sorted_nouns += line
    # Count number of nouns
    n_nouns = len(sorted_nouns)

    # Create dictionary to map nouns to vectors
    noun_to_vect_dict = {}
    # Calculate index to stop slice as percentage of total nouns
    n_nouns_to_keep = int(n_nouns * percent / 100.)
    logger.info('Keeping %i nouns, %i percent of %i',
                n_nouns_to_keep, percent, n_nouns)
    # Add nouns and vectors to dictionary
    for noun in sorted_nouns[0:n_nouns_to_keep]:
        noun_to_vect_dict[noun] = model[noun]

    vectors = np.array(noun_to_vect_dict.values())

if __name__ == '__main__':
    plac.call(main)
