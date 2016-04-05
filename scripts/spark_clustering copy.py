import plac
import logging

from gensim.models import Word2Vec
import numpy as np

import pyspark as ps
from pyspark.mllib.clustering import KMeans
from math import sqrt
from os import path
import pickle

logger = logging.getLogger(__name__)


def error(kmeans_model, point):
    center = kmeans_model.centers[kmeans_model.predict(point)]
    return sqrt(sum([x ** 2 for x in (point - center)]))


@plac.annotations(
    noun_file_loc=('Path to list of nouns'),
    model_file_loc=('Path to saved Word2Vec model'),
    percent=('Percent of nouns to cluster'),
    n_trials=('Number of ks to try'),
    out_files_loc=('Path to save centroids')
)
def main(noun_file_loc, model_file_loc, percent, n_trials, out_files_loc):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    logger.info('Loading Word2Vec model')
    # Load trained Word2Vec model
    model = Word2Vec.load('model_file_loc')

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

    # Initialize Spark Context
    sc = ps.SparkContext('local[4]')
    # Load data
    data = sc.parallelize(vectors)

    # Define search space for k
    ns_clusters = [int(x) for x in np.linspace(2, n_nouns, n_trials)]
    # Open WSSSEs output file
    with open(path.join(out_files_loc, 'elbow_data.txt'), 'w') as elbow_data:
        # For each k
        for i, k in enumerate(ns_clusters):
            logger.info('Trial %i of %i, %i clusters', (i + 1), n_trials, k)
            # Calculate cluster
            kmeans_model = KMeans.train(data, k, maxIterations=10, runs=10,
                                        initalizationMode='k-means||')
            # Calculate WSSSE
            WSSSE = data.map(lambda point: error(kmeans_model, point)) \
                        .reduce(lambda x, y: x + y)
            # Save centroids
            with open(path.join(out_files_loc, '_', k, '.pkl'), 'w') as f:
                pickle.dump(kmeans_model.clusterCenters(), f)
            # Write k and WSSSE
            elbow_data.write('%i, %f', k, WSSSE)

if __name__ == '__main__':
    plac.call(main)
