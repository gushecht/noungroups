import plac
import logging

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
    out_files_loc=('Path to save centroids')
)
def main(noun_to_vect_dict_file_loc, out_files_loc):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    logger.info('Loading pickled noun to vector dictionary')
    # Load noun to vector dictionary
    with open(noun_to_vect_dict_file_loc, 'rb') as pickled:
        noun_to_vect_dict = pickle.load(pickled)
    # Create vector array from mapping
    vectors = np.array(noun_to_vect_dict.values())
    max_k = int(sqrt(len(vectors) / 2.0))

    # Initialize Spark Context
    sc = ps.SparkContext('local[3]')
    # Load data
    data = sc.parallelize(vectors, 1024)

    # Define search space for k
    numbers_of_clusters = xrange(9, max_k)
    # For each k
    for i, k in enumerate(numbers_of_clusters):
        logger.info('Trial %i of %i, %i clusters', (i + 8), max_k - 1, k)
        # Calculate cluster
        kmeans_model = KMeans.train(data, k, maxIterations=10, runs=10,
                                    initializationMode='k-means||')
        # Calculate WSSSE
        WSSSE = data.map(lambda point: error(kmeans_model, point)) \
                    .reduce(lambda x, y: x + y)
        # Save centroids
        with open(path.join(out_files_loc, str(k) + '.pkl'), 'w') as f:
            pickle.dump(kmeans_model.clusterCenters, f)
        # Write k and WSSSE
        with open(path.join(out_files_loc, 'elbow_data.txt'), 'a') as elbow_data:
            elbow_data.write(str(k) + '\t' + str(WSSSE) + '\n')

if __name__ == '__main__':
    plac.call(main)
