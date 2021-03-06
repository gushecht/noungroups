import logging

import numpy as np

import pyspark as ps
from pyspark.mllib.clustering import KMeans
from math import sqrt

from os import path
import pickle

logger = logging.getLogger(__name__)


NOUN_TO_VECT_DICT_FILE_LOC = 'noun_to_vect_dict_100000.pkl'
OUT_FILES_LOC = 'centroids'
MIN_K = 2


def error(kmeans_model, point):
    center = kmeans_model.centers[kmeans_model.predict(point)]
    return sqrt(sum([x ** 2 for x in (point - center)]))


def main():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    logger.info('Loading pickled noun to vector dictionary')
    # Load noun to vector dictionary
    with open(NOUN_TO_VECT_DICT_FILE_LOC, 'rb') as pickled:
        noun_to_vect_dict = pickle.load(pickled)
    # Create vector array from mapping
    vectors = np.array(noun_to_vect_dict.values())
    max_k = int(sqrt(len(vectors) / 2.0))

    # Define search space for k
    numbers_of_clusters = reversed(range(MIN_K, max_k))

    # For each k
    for i, k in enumerate(numbers_of_clusters):
        # Initialize Spark Context
        sc = ps.SparkContext()
        # Load data
        data = sc.parallelize(vectors, 1024)

        logger.info('Trial %i of %i, %i clusters', (i + 1), max_k - 1, k)
        # Calculate cluster
        kmeans_model = KMeans.train(data, k, maxIterations=10, runs=10,
                                    initializationMode='k-means||')
        logger.info('Calculating WSSSE')
        # Calculate WSSSE
        WSSSE = data.map(lambda point: error(kmeans_model, point)) \
                    .reduce(lambda x, y: x + y)
        logger.info('Writing WSSSE')
        # Write k and WSSSE
        with open(path.join(OUT_FILES_LOC, 'elbow_data.txt'), 'a') as elbow_data:
            elbow_data.write(str(k) + '\t' + str(WSSSE) + '\n')

        sc.stop()

if __name__ == '__main__':
    main()
