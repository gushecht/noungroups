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
    noun_to_vect_dict_file_loc=('Path to pickled noun to vector dictionary'),
    n_trials=('Number of ks to try'),
    out_files_loc=('Path to save centroids')
)
def main(noun_file_loc, model_file_loc, percent, n_trials, out_files_loc):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    logger.info('Loading pickled noun to vector dictionary')
    # Load noun to vector dictionary
    noun_to_vect_dict = pickle.load(noun_to_vect_dict_file_loc)
    # Create vector array from mapping
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
