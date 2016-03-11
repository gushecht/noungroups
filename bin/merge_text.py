from __future__ import print_function, unicode_literals, division
import io
from os import path
import re

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


# Creates an iterator that returns one line at a time to reduce memory use
def line_iterator(in_file):
    with open(in_file, 'r') as file_:
        for line in file_:
            yield unicode(line)


# Takes a doc object from the pipe, puts it into the transformation function
# and writes the output to file
def parse_and_transform(batch_id, input_, out_dir):
    out_loc = path.join(out_dir, '%d.txt' % batch_id)
    if path.exists(out_loc):
        return None
    with io.open(out_loc, 'w', encoding='utf8') as file_:
        file_.write(transform_doc(input_))


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
            strings.append(' '.join(represent_word(w) for w in sent if not w.is_space))
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
    in_file=('Location of input file'),
    out_dir=('Path to output directory'),
    batch_size=('Number of sequences of unicode objects to accumulate in buffer', 'option', 'b', int),
    n_threads=('Number of processes to use while operating on unicode objects', 'option', 'p', int)
)
def main(in_file, out_dir, batch_size=500, n_threads=2):
    if not path.exists(out_dir):
        path.join(out_dir)
    else:
        print('Loading spacy.en.English, this may take a while....')
        nlp = spacy.en.English()
        print('spacy.en.English loaded!')
        for i, doc in enumerate(nlp.pipe(line_iterator(in_file), batch_size, n_threads)):
            parse_and_transform(i, doc, out_dir)

if __name__ == '__main__':
    plac.call(main)
