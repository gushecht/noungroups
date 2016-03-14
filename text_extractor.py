from HTMLParser import HTMLParser
import re
import plac
import time

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

less_than_pattern = re.compile('&lt;')
greater_than_pattern = re.compile('&gt;')
ref_pattern = re.compile('<ref.*?<\/ref>')
math_pattern = re.compile('<math.*?<\/math>')
meta_comment_pattern = re.compile('({{[^}]*}})')
url_pattern = re.compile('(?:\@|https?\:\/\/)\S+', flags=re.MULTILINE)
many_quotes_pattern = re.compile('\'\'+')
pipe_pattern = re.compile('\|')
image_pattern = re.compile('\[\[Image.*?\|')
thumb_pattern = re.compile('thumb\|')
left_pattern = re.compile('left\|')
right_pattern = re.compile('right\|')
px_pattern = re.compile('\d*?px\|')
brackets_pattern = re.compile('\[|\]')
single_curly_braces_pattern = re.compile('{.*?}')
period_pattern = re.compile('\.')
punctuation_except_single_quote_pattern = re.compile('[%s]' % re.escape('!"#$%&().*+,-/:;<=>?@\[\\]^_`{|}~'))
possessive_pattern = re.compile('\'s')
many_equals_pattern = re.compile('==*')
non_unicode_pattern = re.compile('[^\x00-\x7F]+')


def clean_text(line):
    # Look for '==References=='
    end_point = line.find('==References==')
    # If that's not found, look for '==Notes and references'
    if end_point == -1:
        end_point = line.find('==Notes and references==')
    # If either of those was found, trim the string off at that point
    if end_point != -1:
        line = line[:end_point]
    # Remove non-unicode characters
    line = non_unicode_pattern.sub(' ', line)
    # Convert &lt; and &gt; to < and >
    line = less_than_pattern.sub('<', line)
    line = greater_than_pattern.sub('>', line)
    # Remove HTML tags
    line = strip_tags(line)
    # # Remove wiki markup image links
    line = image_pattern.sub(' ', line)
    line = thumb_pattern.sub(' ', line)
    line = left_pattern.sub(' ', line)
    line = right_pattern.sub(' ', line)
    line = px_pattern.sub(' ', line)
    # Remove wiki markup comments
    line = meta_comment_pattern.sub(' ', line)
    # Remove content within single braces
    line = single_curly_braces_pattern.sub(' ', line)
    # Remove URLs
    line = url_pattern.sub(' ', line)
    # Remove two or more consecutive ' characters
    line = many_quotes_pattern.sub(' ', line)
    # Replace pipes with spaces
    line = pipe_pattern.sub('| ', line)
    # Remove square brackets
    line = brackets_pattern.sub(' ', line)
    # Convert periods to newlines
    line = period_pattern.sub('.\n', line)
    # Remove all punctuation except single quotes
    line = punctuation_except_single_quote_pattern.sub(' ', line)
    # Remove possessive 's
    line = possessive_pattern.sub('', line)
    # Remove two or more consecutive = characters
    line = many_equals_pattern.sub(' ', line)
    # Remove remaining leading or trailing whitespace
    line = line.strip()
    # If the string isn't empty, return it
    if line != '':
        return line


@plac.annotations(
    in_loc=('Locaiton of input file'),
    out_loc=('Location of output file')
)
def main(in_loc, out_loc):
    line_count = 0
    article_count = 0
    accept_all = False

    target = open(out_loc, 'w')

    with open(in_loc, 'r') as infile:
        article = ''
        for line in infile:
            if not accept_all:
                if '<text xml:space' in line:
                    accept_all = True
                    article += line.strip() + ' '
                    line_count += 1
            if accept_all:
                article += line.strip() + ' '
                line_count += 1
                if '</text>' in line:
                    accept_all = False
                    if '#REDIRECT' not in article:
                        cleaned_article = clean_text(article)
                        try:
                            target.write(cleaned_article)
                        except TypeError:
                            time = int(time.time())
                            print('Failed attempt at: %s' % time)
                            with open(time, 'w') as failed_attempt:
                                failed_attempt.write(article)
                    article = ''
                    article_count += 1

        print 'Total lines written %s' % line_count
        print 'Total articles %s' % article_count

    target.close()

if __name__ == '__main__':
    plac.call(main)
