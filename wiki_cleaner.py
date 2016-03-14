import re
import plac
from os import path, listdir, makedirs
import time

empty_doc_pattern = re.compile('<doc.*>\s.+\s\s\s<\/doc>')
doc_tag_pattern = re.compile('<\/?doc.*?>')


# Remove empty documents from transformed Wikipedia dump
def clean_string(string):
    string = empty_doc_pattern.sub('', string)
    string = doc_tag_pattern.sub('', string)
    if string:
        return string


# Creates a generator that returns the path to each file in a directory.
# Note that it does not work for nested directories.
def iter_dir(loc):
    # If the provided path is to a file, not a directory, return the path
    if not path.isdir(loc):
        yield loc
    # Otherwise, return the path iterator
    else:
        for fn in listdir(loc):
            yield path.join(loc, fn)


@plac.annotations(
    in_dir=('Location of input file'),
    out_dir=('Directory to save output')
)
def main(in_dir, out_dir):
    # Create the output directory, if it doesn't exist
    if not path.exists(out_dir):
        makedirs(out_dir)
    # Get total number of input files for tracking progress
    total_files = len(listdir(in_dir))
    # For each input file
    for i, file in enumerate(iter_dir(in_dir)):
        print('Cleaning file %s of %s' % (i, total_files))
        # Create the output file
        out_loc = str(i) + '.txt'
        with open(path.join(out_dir, out_loc), 'w') as target:
            # Open the input file
            with open(file, 'r') as infile:
                # Read and clean the file and save to new file
                string = infile.read()
                string = clean_string(string)
                if string:
                    target.write(string)

if __name__ == '__main__':
    plac.call(main)
