from os import path, listdir
import plac


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


@plac.annotations(
    in_dir=('Path to input directory'),
    out_loc=('Path to output file')
)
def main(in_dir, out_loc):
    # Get total number of input files for tracking progress
    total_files = len(list(iter_dir(in_dir)))
    with open(out_loc, 'w') as target:
        # For each input file
        for i, file in enumerate(iter_dir(in_dir)):
            if i % 100 == 0:
                print('Combining file %s of %s' % (i, total_files))
            with open(file, 'r') as f:
                for line in f:
                    if line != '\n':
                        target.write(line)

if __name__ == '__main__':
    plac.call(main)
