import plac
import pyspark as ps
from operator import add
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
    out_dir=('Location to write output file'),
)
def main(in_dir, out_dir):
    sc = ps.SparkContext()
    text_files = sc.textFile(in_dir)
    counts = text_files.flatMap(lambda line: line.split(' ')) \
                       .filter(lambda word: any(label in word for label in LABELS)) \
                       .map(lambda word: (word, 1)) \
                       .reduceByKey(add) \
                       .persist(storageLevel=ps.StorageLevel.MEMORY_AND_DISK)
    total_nouns = counts.values() \
                        .reduce(add)
    sorted_nouns = counts.map(lambda (word, count): (word, count / float(total_nouns))) \
                         .sortBy(lambda (word, count): count, ascending=False) \
                         .collect()
    with open(path.join(out_dir, 'sorted_nouns.txt'), 'w+') as f:
        for word in sorted_nouns:
            f.write(str(word) + '\n')

if __name__ == '__main__':
    plac.call(main)
