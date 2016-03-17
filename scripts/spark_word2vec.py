import plac
import pyspark as ps
from pyspark.mllib.feature import Word2Vec
from os import path

LABELS = [
    'ENT',
    'PERSON',
    'NORP',
    'FAC',
    'ORG',
    'GPE',
    'LOC',
    'LAW',
    'PRODUCT',
    'EVENT',
    'WORK_OF_ART',
    'LANGUAGE',
    'NOUN'
]


@plac.annotations(
    in_dir=('Location of files to be read in'),
    out_dir=('Location to save word vectors and model')
)
def main(in_dir, out_dir):
    sc = ps.SparkContext('local[4]')
    docs = sc.textFile(in_dir) \
             .map(lambda line: line.split(' '))
    model = Word2Vec().setVectorSize(100).setSeed(42).fit(docs)
    all_vectors = dict(model.getVectors())
    noun_vectors = {}
    for key, value in all_vectors.iteritems():
        if any(label in key for label in LABELS):
            noun_vectors[key] = value


    model.save(sc, path.join(out_dir, 'spark_word2vec_model'))
    with open(path.join(out_dir, 'word_vector_map.txt'), 'w') as f:
        for word, vector in vectors:
            f.write(str(word) + '\n')

if __name__ == '__main__':
    plac.call(main)
