from functools import reduce

import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.client import CatClient

from .search_index_weights import execute_query


class Rocchio:
    def __init__(self):
        self.alpha = 1
        self.beta = 1
        self.gamma = 1
        self.nrounds = 10
        self.k = 5

    @staticmethod
    def __add_term_vectors(x, y):
        i, j = 0, 0
        terms_x, weights_x = zip(*x)
        terms_y, weights_y = zip(*y)
        new_terms, new_weights = [], []
        while i < len(x) and j < len(y):
            if terms_x[i] < terms_y[j]:
                new_terms.append(terms_x[i])
                new_weights.append(weights_x[i])
                i += 1
            elif terms_x[i] > terms_y[j]:
                new_terms.append(terms_y[j])
                new_weights.append(weights_y[j])
                j += 1
            else:
                new_terms.append(terms_x[i])
                new_weights.append(weights_x[i] + weights_y[j])
                i += 1
                j += 1

        if i < len(x):
            new_terms.extend(terms_x[i:])
            new_weights.extend(weights_x[i:])
        if j < len(y):
            new_terms.extend(terms_y[j:])
            new_weights.extend(weights_y[j:])

        return list(zip(new_terms, new_weights))

    @staticmethod
    def __query_to_term_vector(query):
        def set_term_weights(word):
            s = word.split('^')
            return (word, 1) if len(s) == 1 else (s[0], float(s[1]))

        query = list(map(set_term_weights, query.split()))
        return Rocchio.__normalize(query)

    @staticmethod
    def __term_vector_to_query(tw):
        return reduce(lambda acc, x:
                      acc + ' ' + x[0] + '^' + str(round(x[1])) if round(x[1]) != 0 else acc, tw, '')[1:]

    @staticmethod
    def __normalize(tw):
        terms, weights = zip(*tw)
        normalized_weights = weights / np.linalg.norm(weights)
        return list(zip(terms, normalized_weights))

    @staticmethod
    def __to_tf_idf(client, index, file_id):
        def tf_idf(params):
            (term, freq), (_, doc_freq) = params
            tf = freq / max_freq
            idf = np.log2(document_count / doc_freq)
            return term, tf * idf

        def document_term_vector():
            tv = client.termvectors(index=index, doc_type='document', id=file_id, fields=['text'],
                                    positions=False, term_statistics=True)
            file_td, file_df = {}, {}
            if 'text' in tv['term_vectors']:
                for t in tv['term_vectors']['text']['terms']:
                    file_td[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
                    file_df[t] = tv['term_vectors']['text']['terms'][t]['doc_freq']
            return sorted(file_td.items()), sorted(file_df.items())

        term_frequency, document_appearances = document_term_vector()
        max_freq = max([f for _, f in term_frequency])
        document_count = int(CatClient(client).count(index=[index], format='json')[0]['count'])

        vector = list(map(tf_idf, zip(term_frequency, document_appearances)))
        return Rocchio.__normalize(vector)

    def update_parameters(self, alpha, beta, gamma, nrounds, k):
        self.alpha = self.alpha if alpha is None else alpha
        self.beta = self.beta if beta is None else beta
        self.gamma = self.gamma if gamma is None else gamma
        self.nrounds = self.nrounds if nrounds is None else nrounds
        self.k = self.k if k is None else k

    def query(self, index, query):
        q = Rocchio.__query_to_term_vector(query)
        client = Elasticsearch()

        for it in range(self.nrounds):
            print('Round #{}: {}'.format(it, query))

            documents = execute_query(index, query, self.k)
            relevant_term_vectors = list(map(lambda doc: Rocchio.__to_tf_idf(client, index, doc.meta.id), documents))

            terms, weights = zip(*q)
            weights = (self.alpha * np.array(weights)).tolist()
            old = list(zip(terms, weights))

            sum_relevant_documents = reduce(Rocchio.__add_term_vectors, relevant_term_vectors)
            terms, weights = zip(*sum_relevant_documents)
            weights = (self.beta * np.array(weights) / len(sum_relevant_documents)).tolist()
            relevant = list(zip(terms, weights))

            q = Rocchio.__add_term_vectors(old, relevant)
            query = Rocchio.__term_vector_to_query(q)

        documents = execute_query(index, query, self.k)
