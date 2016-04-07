import logging

import pickle

import pyspark as ps
from pyspark.mllib.clustering import KMeans

from os import path

logger = logging.getLogger(__name__)

# Define N_CLUSTERS as determined earlier
N_CLUSTERS = 15
# Define NOUN_TO_VECT_DICT_FILE_LOC
NOUN_TO_VECT_DICT_FILE_LOC = 'saved_objects/noun_to_vect_dict_100000.pkl'
# Define OUT_FILE_LOC
OUT_FILE_LOC = '.'


def main():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    # Load in pickled noun to vector dictionary
    logger.info('Loading pickled noun to vector dictionary')
    # Load noun to vector dictionary
    with open(NOUN_TO_VECT_DICT_FILE_LOC, 'rb') as f:
        noun_to_vect_dict = pickle.load(f)

    # Create vectors array
    vectors = noun_to_vect_dict.values()

    # Initialize Spark Context
    sc = ps.SparkContext('local[*]')
    # Load data
    data = sc.parallelize(vectors, 1024)

    # Create and fit a KMeans model to the data
    logger.info('Fitting KMeans model')
    kmeans_model = KMeans.train(data, N_CLUSTERS, maxIterations=10, runs=10,
                                initializationMode='k-means||')

    # Create a list of labels corresponding to vectors
    logger.info('Labeling vectors')
    labels = [kmeans_model.predict(vector) for vector in vectors]
    # Write to text file
    logger.info('Writing labels to file')
    with open(path.join(OUT_FILE_LOC, 'labels.txt'), 'w') as f:
        for label in labels:
            f.write(str(label) + '\n')

if __name__ == '__main__':
    main()
