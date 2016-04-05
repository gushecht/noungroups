# TO DO
# Use my own data instead of Reddit
# Optimize KMeans
# Try ANNOY with different numbers of trees, different distance metrics
# Slim down ANNOY implementation (i.e. reduce number of mapping dictionaries)
#   by using get_nns_by_vector and get_item_vector functions

import sense2vec
import numpy as np
from sklearn.cluster import KMeans, MiniBatchKMeans
from annoy import AnnoyIndex
from itertools import izip
import pickle

# For now, let's just use the data that comes with it

model = sense2vec.load()

# All lables for nouns
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

# Create dictionary to map words to vectors
word_to_vect_dict = {}
# Create dictionary to map words to AnnoyIndex's integer identifiers
word_to_identifier_dict = {}
identifier = 0
for i, string in enumerate(model.strings):
    # If the string is a noun, add it and its vector to the dictionary
    if any(label in string for label in LABELS):
        word_to_vect_dict[string] = model[string][1]
        word_to_identifier_dict[string] = identifier
        identifier += 1
    # Just to track progress
    if i % 10000 == 0:
        print 'String #%s of %s --> %s' % \
              (i, len(model.strings), (i / float(len(model.strings))))

# Create an array of the vectors
word_vectors = np.array(word_to_vect_dict.values())

NUM_WORDS = len(word_vectors)

# Create and fit a KMeans clustering model
kmeans = KMeans(n_clusters=100,
                n_jobs=-1)
kmeans.fit(word_vectors)

mini_kmeans = MiniBatchKMeans(n_clusters=20, verbose=True)
mini_kmeans.fit(word_vectors)

# Get the centroids of each cluster
centroids = kmeans.cluster_centers_
mini_centroids = mini_kmeans.cluster_centers_

# F is this number of dimensions of the vectors, in this case 128 since that's
# what sense2vec works with
f = 128

# Create an AnnoyIndex
t = AnnoyIndex(f, metric='euclidean')

# Add the word vectors to the AnnoyIndex
for i, vector in izip(word_to_identifier_dict.values(),
                      word_to_vect_dict.values()):
    t.add_item(i, vector)

# Create dictionary to map integer identifiers to centroid vectors
identifier_to_centroid_vect_dict = {}
for i in xrange(len(centroids)):
    identifer = NUM_WORDS + i
    identifier_to_centroid_vect_dict[identifer] = centroids[i]

for i, vector in izip(identifier_to_centroid_vect_dict.keys(),
                      identifier_to_centroid_vect_dict.values()):
    t.add_item(i, vector)

t.build(10)

for i in xrange(8):
    closest = t.get_nns_by_item(identifier_to_centroid_vect_dict.keys()[i], 20)

    for key, value in word_to_identifier_dict.iteritems():
        if value in closest:
            print key

    print '\n'


##########

# F is this number of dimensions of the vectors, in this case 128 since that's
# what sense2vec works with
f = 128

# Create an AnnoyIndex
t = AnnoyIndex(f, metric='euclidean')

# Add the word vectors to the AnnoyIndex
for i, vector in izip(word_to_identifier_dict.values(),
                      word_to_vect_dict.values()):
    t.add_item(i, vector)

# Create dictionary to map integer identifiers to centroid vectors
identifier_to_centroid_vect_dict = {}
for i in xrange(len(mini_centroids)):
    identifer = NUM_WORDS + i
    identifier_to_centroid_vect_dict[identifer] = mini_centroids[i]

for i, vector in izip(identifier_to_centroid_vect_dict.keys(),
                      identifier_to_centroid_vect_dict.values()):
    t.add_item(i, vector)

t.build(10)

for i in xrange(len(mini_centroids)):
    closest = t.get_nns_by_item(identifier_to_centroid_vect_dict.keys()[i], 20)

    for key, value in word_to_identifier_dict.iteritems():
        if value in closest:
            print key

    print '\n'

t.save('test.ann')

with open('kmeans.pkl', 'wb') as f:
    pickle.dump(kmeans, f)

with open('mini_kmeans.pkl', 'wb') as f:
    pickle.dump(mini_kmeans, f)