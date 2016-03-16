import bz2


def iter_lines(loc):
    count = 0
    with bz2.BZ2File(loc, 'r') as file_:
        for line in file_:
            count += 1
    print(count)

iter_lines('articles_combined.txt.bz2')
