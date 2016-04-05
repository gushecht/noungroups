import plac
import logging

from gensim.models import Word2Vec
from ast import literal_eval as make_tuple

import pickle
from os import path

logger = logging.getLogger(__name__)


@plac.annotations(
    nouns_loc=('Path to sorted list of nouns'),
    word2vec_loc=('Path to word2vec model'),
    n_nouns=('Number of nouns to keep'),
    out_loc=('Location to save output file')
)
def main(nouns_loc, word2vec_loc, n_nouns, out_loc):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    # Load trained Word2Vec model
    model = Word2Vec.load(word2vec_loc)
    logger.info('Word2Vec object loaded')

    logger.info('Keeping %s nouns', n_nouns)
    # Empty dictionary for noun to vector mapping
    noun_to_vect_dict = {}
    # Counter to know when to stop
    counter = 0
    with open(nouns_loc, 'r') as f:
        while counter < int(n_nouns):
            line = make_tuple(f.readline())
            # Add noun and vector to mapping dictionary
            noun = line[0]
            noun_to_vect_dict[noun] = model[noun]
            # Increment counter
            counter += 1

    logger.info('Pickling noun to vector dictionary')
    # Pickle dictionary
    with open(path.join(out_loc, 'noun_to_vect_dict.pkl'), 'w') as f:
        pickle.dump(noun_to_vect_dict, f)

if __name__ == '__main__':
    plac.call(main)
