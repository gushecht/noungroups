import plac
import logging

import pyspark as ps
from pyspark.mllib.feature import Word2Vec

in_loc = 's3n://[AWS Key ID]:[AWS Key Secret]@gushecht/pos_tagged'

from os import path
import cPickle

logger = logging.getLogger(__name__)


@plac.annotations(
    in_loc=('Path to input files'),
    out_dir=('Location to store output file')
)
def main(in_loc, out_dir):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)

    sc = ps.SparkContext(appName='Word2Vec')
    logger.info('Distributing input data')
    raw_data = sc.textFile(in_loc).cache()
    data = raw_data.map(lambda line: line.split(' '))
    print(data.getNumPartitions())

    logger.info('Training Word2Vec model')
    model = Word2Vec().setVectorSize(128).setNumIterations(5).fit(data)

    w2v_dict = model.getVectors()
    logger.info('Saving word to vectors dictionary')
    with open(path.join(out_dir, 'w2v_dict.pkl'), 'wb') as f:
        cPickle.dump(w2v_dict, f, cPickle.HIGHEST_PROTOCOL)

    model.save(sc, out_dir)

if __name__ == '__main__':
    plac.call(main)
