from preprocessing import Preprocessor
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.decomposition import NMF, PCA, TruncatedSVD
from code_tokenizer import code_tokenizer


class Featurizer(object):

    def __init__(self, n_features = 100, start_column = 7):
        self.s = start_column
        self.n_features = n_features
        self.nmf_ncode = None
        self.nmf_code = None
        self.topics = []

    def make_feature_matrix(self, X, is_code = False):
        if is_code:
            tfidf = TfidfVectorizer(tokenizer = code_tokenizer, stop_words = 'english',
                                    sublinear_tf=True, use_idf=True)
        else:
            tfidf = TfidfVectorizer(stop_words = 'english', sublinear_tf=True,
                                    use_idf=True)

        features = tfidf.get_feature_names()

        full_matrix = tfidf.fit_transform(X)

        print "Made tfidf"

        svd = TruncatedSVD(n_components = self.n_features)



        reduced_matrix = svd.fit_transform(full_matrix.toarray())

        print "Finished SVD"

        num_words = 20
        top_words = []
        for topic in svd.components_:
            top_words.append([features[i] for i in topic.argsort()[:-num_words - 1:-1]])

        self.topics.append(top_words)

        return reduced_matrix


    def fit_transform(self, X):

        non_code_texts = np.concatenate((X[:,self.s], X[:, self.s+2]), axis = 0)
        code_texts = np.concatenate((X[:,self.s+1], X[:,self.s+3]), axis = 0)

        non_code_matrix = self.make_feature_matrix(non_code_texts, is_code = False)

        code_matrix = self.make_feature_matrix(code_texts, is_code = True)

        rejoined_ncode = np.split(non_code_matrix, 2, axis = 0)

        rejoined_code = np.split(code_matrix, 2, axis = 0)

        full_matrix = np.concatenate([rejoined_ncode[0].reshape(-1,1),
                                      rejoined_code[0].reshape(-1,1),
                                      rejoined_ncode[1].reshape(-1,1),
                                      rejoined_code[1]].reshape(-1,1), axis = 1)

        return full_matrix
