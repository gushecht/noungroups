from __future__ import print_function, unicode_literals, division
from os import path, listdir, makedirs
import re
import time

import spacy.en

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


# Creates a generator that returns the path to each file in a directory.
# Note that this only works for one level of nesting, e.g. 
# dir/dir/file, not dir/dir/dir/file
def iter_dir(loc):
    # For each filename in the directory
    for fn in os.listdir(loc):
        # If the filename is actually a path to a directory
        if path.isdir(path.join(loc, fn)):
            # For each filename in that subdirectory
            for sub in os.listdir(path.join(loc, fn)):
                # Yield the filename
                yield path.join(loc, fn, sub)
        # Otherwise, if the filename is a path to a file
        else:
            # Yield the filename
            yield path.join(loc, fn)


# Creates a generator that returns one line of a file at a time
def line_iterator(in_file):
    with open(in_file, 'r') as file_:
        for line in file_:
            yield unicode(line)


# Takes a doc object, constructs entities and adds tags, returning a string
def transform_doc(doc):
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
    in_dir=('Location of input directory'),
    out_dir=('Location of output directory'),
    batch_size=(
        'Number of sequences of unicode objects to accumulate in buffer',
        'option', 'b', int),
    n_threads=(
        'Number of processes to use while operating on unicode objects',
        'option', 'p', int)
)
def main(in_dir, out_dir, batch_size=500, n_threads=2):
    # Create the output directory, if it doesn't exist
    if not path.exists(out_dir):
        makedirs(out_dir)
    # Get total number of input files for tracking progress
    total_files = len(listdir(in_dir))
    # Load nlp object
    print('Loading spacy.en.English, this may take a while....')
    nlp = spacy.en.English()
    print('spacy.en.English loaded!')
    # For each input file
    for i, file in enumerate(iter_dir(in_dir)):
        print('Tagging file %s of %s' % (i, total_files))
        # Create the first output file
        current_time = str(int(time.time()))
        out_loc = current_time + '.txt'
        target = open(path.join(out_dir, out_loc), 'w')
        # Create empty string to store tagged text
        tagged_text = ''
        for j, doc in enumerate(nlp.pipe(line_iterator(file), batch_size=batch_size,
                                         n_threads=n_threads)):
            tagged_text += transform_doc(doc)
            # Write to the output file occasionally and create a new one
            if j % batch_size == 0 and j != 0:
                target.write(tagged_text)
                target.close()
                current_time = str(int(time.time()))
                out_loc = current_time + '.txt'
                target = open(path.join(out_dir, out_loc), 'w')


if __name__ == '__main__':
    plac.call(main)
