import plac
import logging

import pickle

import numpy as np
from sklearn.neighbors import KNeighborsClassifier

from os import path

logger = logging.getLogger(__name__)


@plac.annotations(
    noun_to_vect_dict_loc=('Location of noun_to_vect_dict file'),
    labels_loc=('Location of labels file'),
    centroids_loc=('Location of centroids file'),
    out_file_path=('Path to save output files')
)
def main(noun_to_vect_dict_loc, labels_loc, centroids_loc):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    # Load in pickled noun to vector dictionary
    logger.info('Loading pickled noun to vector dictionary')
    # Load noun to vector dictionary
    with open(noun_to_vect_dict_loc, 'rb') as f:
        noun_to_vect_dict = pickle.load(f)

    # Create nouns array
    nouns = np.array(noun_to_vect_dict.keys())
    # Create vectors array
    vectors = noun_to_vect_dict.values()

    # Create labels array
    labels = []
    # Load in labels
    logger.info('Loading in labels')
    with open(labels_loc, 'r') as f:
        for line in f:
            labels.append(int(line))
    labels = np.array(labels)

    # Load in pickled centroids
    logger.info('Loading pickled centroids')
    with open(centroids_loc, 'rb') as f:
        centroids = pickle.load(f)

    # Create empty dictionary for top nouns for a cluster
    top_nouns_dict = {}

    # Instantiate and fit kNN model
    knc = KNeighborsClassifier(n_jobs=-1)
    knc.fit(vectors, labels)

    # Get indices of top vectors
    for i, centroid in enumerate(centroids):
        # Determine number of representative vectors to get
        class_size = sum(labels == i)
        n_neighbors = 50 if class_size >= 50 else class_size
        # Get indices of n_neighbors vectors nearest to centroid
        indices = knc.kneighbors(X=centroid, n_neighbors=n_neighbors)
        # Add top nouns corresponding to those indices to dictionary
        top_nouns_dict[i] = nouns[indices]

if __name__ == '__main__':
    plac.call(main)
