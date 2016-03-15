import plac
import pyspark as ps
from pyspark.mllib.feature import Word2Vec
from os import path


@plac.annotations(
    in_dir=('Location of files to be read in'),
    out_dir=('Location to save word vectors and model')
)
def main(in_dir, out_dir):
    sc = ps.SparkContext('local[4]')
    docs = sc.textFile(in_dir) \
             .flatMap(lambda line: line.split(' ')) \
             .take(100)
    print(docs)
    docs = sc.parallelize(docs)
    model = Word2Vec().setVectorSize(100).setSeed(42).fit(docs)
    vectors = model.getVectors()
    print(type(vectors))
    model.save(sc, path.join(out_dir, 'spark_word2vec_model'))
    with open(path.join(out_dir, 'word_vector_map.txt'), 'w') as f:
        for word in vectors:
            f.write(str(word) + '\n')

if __name__ == '__main__':
    plac.call(main)
