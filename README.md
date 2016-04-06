noungroups
=========

__Note that this is a preview of what is to come, I am currently on step 5__

*Use noungroups to categorize entities*

The world is full of unstructured text.  noungroups helps you identify what a text is talking about, allowing you to extract structured data from unstructured text.  noungroups is an extention of a named entity recognizer, such as [Stanford's NER](http://nlp.stanford.edu/software/CRF-NER.shtml).  For example, take the sentence "Barack Obama is the president of the United States".  

Read about sense2vec here:

https://spacy.io/blog/sense2vec-with-spacy

You can use an online demo of the technology here:

https://sense2vec.spacy.io

We're currently refining the API, to make this technology easy to use. Once we've completed that, you'll be able
to download the package on PyPi. For now, the code is available to clarify the blog post.

There are three relevant files in this repository:

#### bin/merge_text.py

This script pre-processes text using spaCy, so that the sense2vec model can be trained using Gensim.

#### bin/train_word2vec.py

This script reads a directory of text files, and then trains a word2vec model using Gensim. The script includes its own
vocabulary counting code, because Gensim's vocabulary count is a bit slow for our large, sparse vocabulary.

#### sense2vec/vectors.pyx

To serve the similarity queries, we wrote a small vector-store class in Cython. This made it easier to add an efficient
cache in front of the service. It also less memory than Gensim's Word2Vec class, as it doesn't hold the keys as Python
unicode strings.

Similarity queries could be faster, if we had made all vectors contiguous in memory, instead of holding them
as an array of pointers. However, we wanted to allow a `.borrow()` method, so that vectors can be added to the store
by reference, without copying the data.

Usage
-----

The easiest way to download and install the model is by calling ```python -m sense2vec.download``` after installing sense2vec, e.g., via ```pip install -e git+git://github.com/spacy-io/sense2vec.git#egg=sense2vec```:

```
>>> import sense2vec
>>> model = sense2vec.load()
>>> freq, query_vector = model["natural_language_processing|NOUN"]
>>> model.most_similar(query_vector, n=3)
(['natural_language_processing|NOUN', 'machine_learning|NOUN', 'computer_vision|NOUN'], <MemoryView of 'ndarray'>)
```

**IMPORTANT** The API is work-in-progress and is subject to change.

For additional performance experimental support for BLAS can be enabled by setting the `USE_BLAS` environment variable before installing (e.g. ```USE_BLAS=1 pip install ...```). This requires an up-to-date BLAS/OpenBlas/Atlas installation.

Support
-------

* CPython 2.6, 2.7, 3.3, 3.4, 3.5 (only 64 bit)
* OSX
* Linux
* Windows
