#noungroups

__Note that this is a preview of what is to come, I am currently on step 6__

*Use noungroups to precisely recognize entities in text*

noungroups is an extension of a named entity recognizer (NER). Most NERs take text and can broadly categorize entities, for example as people or locations. noungroups is much more precise, making it easy for you to input your text and find out what it's talking about.

For example, whereas [Stanford's NER](http://nlp.stanford.edu/software/CRF-NER.shtml) takes the sentence: 'Barack Obama is the president of the United States' and identifies a person and a location, noungroups identifies a national leader and a country.

noungroups is the simple result of a long process that had the following steps:

1. Download [English language Wikipedia dump](https://archive.org/details/enwiki-20080103)
2. Extract plain text articles from  XML with the handy [wikiextractor](https://github.com/attardi/wikiextractor/wiki)
3. Tag each word with its part of speech with the powerful [spaCy](https://github.com/spacy-io/spaCy)
4. Vectorize each tagged word (à la [sense2vec](http://arxiv.org/abs/1511.06388)) with the speedy [Gensim port](https://github.com/piskvorky/gensim/) of [Google's word2vec](https://code.google.com/archive/p/word2vec/)
5. Filter out just the nouns/entities and sort them by frequency of appearance in English language Wikipedia
6. Find the optimal number of clusters of the 100,000 most frequent nouns/entities with the smoothly parallelized [Spark implementation](http://spark.apache.org/docs/latest/mllib-clustering.html) of [k-means ||](http://theory.stanford.edu/~sergei/papers/vldb12-kmpar.pdf)
7. Label those clusters
8. Create a web service with an API that takes your textblobs, part of speech tags the words, and returns the corresponding categorization for each noun/entity based on the labeled clusters.

## Details on the above

### Part of speech tagging
Every word has a part of speech.  For example, in the sentence 'the bird ate seeds' the four words are a determiner, a noun, a verb, and a noun, respectively.

### word2vec
word2vec is an algorithm for converting words into vectors.  Excitingly, it was found that the vector representation of a word encodes some of the semantic meaning of the word.  For example, if you take the vector for 'king', subtract the vector for 'man', and add the vector for 'woman', you get the vector for 'queen'.

Additionally, it was found that the same could be done for other conceptually-related words, such as nations and capitals.
<img src="http://deeplearning4j.org/img/countries_capitals.png" width="500px">

From this image of word vectors projected down to two dimensions, it's clear that conceptually-related words occupy regions together.  That was the motivation for this project.

### sense2vec
One limitation of word2vec is that it treats words with multiple meanings as though they only have one.  For example, the word 'duck' is both a noun and a verb, but word2vec gives 'duck' just one vector representation, instead of two.  sense2vec is a proposed improvement that consists the pre-processing step of part of speech tagging the words before they go into word2vec.  Thus, instead of 'She had to duck when the duck flew by' we have 'She|NOUN had|VERB to|PART duck|VERB when|ADV the|DET duck|NOUN flew|VERB by|ADP'.  'duck' and 'duck' become 'duck|VERB' and 'duck|NOUN', two unique words that get two unique vectors.

### Filtering nouns/entities
After the part of speech tagging and vectorizing were finished, I had just over 27 million unique nouns/entities (27,137,917) and their vector representations.  I decided to filter that down to the top 100,000 most frequently used in order to reduce the time required for the clustering step.  Additionally, my intuition told me that ignoring less frequent nouns/entities would reduce noise in the clustering step.

Here's a chart of the cumulative frequency of nouns/entities that validated my choice to set aside the vast majority of the nouns/entities.  The x-axis is in 1000s of nouns/entities, the y axis is total percent frequency.

<img src="images/cumulative_frequencies.png" width="500px">


### Clustering
Clustering is an interesting problem when you don't know how many clusters there should be, which was the case with noungroups.  The only option was the brute force method: trying a range of numbers of clusters and seeing which was the best.  I went with two for the minimum and (n / 2) ^ 0.5, in this case ~ 223, for the maximum.  To compare clusterings, I calculated the within set sum of squared errors (WSSSE) for each one.  The WSSSE measures how dispersed each cluster is.  Plotting them in a chart reveals an 'elbow' in the curve where the rate of decrease in WSSSE decreases significantly.  That elbow was at k clusters, which I took to be the optimal number.

### Labeling
Both because it was necessary and as a form of validation, I manually labeled each cluster.  To do so, I looked at the 50 most representative nouns/entities in each cluster, chosen by their distance from the center of the cluster.  Based on the words, I came up with an appropriate categorization.

### Web service
Rather than require developers to include spaCy as a dependency in their projects, I set up a web service with an API.
