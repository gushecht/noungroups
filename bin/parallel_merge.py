from __future__ import print_function, unicode_literals, division
import bz2
from toolz import partition_all
from os import path, listdir, makedirs
import re

import spacy.en

from joblib import Parallel, delayed
import plac

LABELS = {
    'ENT': 'ENT',
    'PERSON': 'ENT',
    'NORP': 'ENT',
    'FAC': 'ENT',
    'ORG': 'ENT',
    'GPE': 'ENT',
    'LOC': 'ENT',
    'LAW': 'ENT',
    'PRODUCT': 'ENT',
    'EVENT': 'ENT',
    'WORK_OF_ART': 'ENT',
    'LANGUAGE': 'ENT',
    'DATE': 'DATE',
    'TIME': 'TIME',
    'PERCENT': 'PERCENT',
    'MONEY': 'MONEY',
    'QUANTITY': 'QUANTITY',
    'ORDINAL': 'ORDINAL',
    'CARDINAL': 'CARDINAL'
}


def parallelize(func, iterator, n_jobs, extra, backend='multiprocessing'):
    extra = tuple(extra)
    return \
        Parallel(n_jobs=n_jobs, backend=backend)(delayed(func)(*(item + extra))
                                                 for item in iterator)


non_unicode_pattern = re.compile('[^\x00-\x7F]+')


# Creates a generator that returns the path to each file in a directory.
# Note that this only works for one level of nesting, e.g.
# dir/dir/file, not dir/dir/dir/file
def iter_dir(loc):
    # If the path is actually to a file, not a directory, yield filename
    if not path.isdir(path.join(loc)):
        yield loc
    else:
        # For each filename in the directory
        for fn in listdir(loc):
            # If the filename is actually a path to a directory
            if path.isdir(path.join(loc, fn)):
                # For each filename in that subdirectory
                for sub in listdir(path.join(loc, fn)):
                    # Yield the filename
                    yield path.join(loc, fn, sub)
            # Otherwise, if the filename is a path to a file
            else:
                # Yield the filename
                yield path.join(loc, fn)


# Creates a generator that returns the lines of a file.  Expects files to be
# a compressed bz2 file.
def iter_lines(loc):
    with bz2.BZ2File(loc, 'r') as file_:
        for line in file_:
            line = non_unicode_pattern.sub('', line)
            yield unicode(line)


# Takes a doc object, constructs entities and adds tags, returning a string
def transform_doc(doc):
    # print(type(doc))
    for ent in doc.ents:
        ent.merge(ent.root.tag_, ent.text, LABELS[ent.label_])
    for np in doc.noun_chunks:
        while len(np) > 1 and np[0].dep_ not in ('advmod', 'amod', 'compound'):
            np = np[1:]
        np.merge(np.root.tag_, np.text, np.root.ent_type_)
    strings = []
    for sent in doc.sents:
        if sent.text.strip():
            strings.append(' '.join(represent_word(w)
                                    for w in sent if not w.is_space))
    if strings:
        return '\n'.join(strings) + '\n'
    else:
        return ''


def save_parses(batch_id, input_, out_dir, n_threads, batch_size):
    out_loc = path.join(out_dir, '%d.txt' % batch_id)
    if path.exists(out_loc):
        return None
    print('Batch', batch_id)
    nlp = spacy.en.English()
    tagged_text = ''
    for i, doc in enumerate(nlp.pipe(input_,
                                     batch_size=batch_size,
                                     n_threads=n_threads)):
        tagged_text += transform_doc(doc)
    with open(out_loc, 'w') as f:
        f.write(tagged_text)


# Takes a token object returns a properly formatted string representation of it
def represent_word(word):
    if word.like_url:
        return '%%URL|X'
    text = re.sub(r'\s', '_', word.text)
    tag = LABELS.get(word.ent_type_, word.pos_)
    if not tag:
        tag = '?'
    return text + '|' + tag


@plac.annotations(
    in_dir=("Location of input file"),
    out_dir=("Location of output file"),
    n_process=("Number of processes", "option", "p", int),
    n_thread=("Number of threads per process", "option", "t", int),
    batch_size=(
        "Number of texts to accumulate in a buffer", "option", "b", int)
)
def main(in_dir, out_dir, n_process=1, n_thread=4, batch_size=100):
    # Create the output directory, if it doesn't exist
    if not path.exists(out_dir):
        makedirs(out_dir)
    # Get total number of input files for tracking progress
    total_files = len(list(iter_dir(in_dir)))
    # For each input file
    for i, file in enumerate(iter_dir(in_dir)):
        # Print progress
        print('Tagging file %s of %s' % (i + 1, total_files))
        # If multiprocessing
        if n_process >= 2:
            # Split up text in the input file
            texts = partition_all(100000, iter_lines(file))
            # Parallelize the job
            parallelize(save_parses, enumerate(texts),
                        n_process, [out_dir, n_thread, batch_size],
                        backend='multiprocessing')
        # If not multiprocessing
        else:
            save_parses(0, iter_lines(file), out_dir, n_thread, batch_size)


if __name__ == '__main__':
    plac.call(main)
