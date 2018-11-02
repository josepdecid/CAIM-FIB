from functools import reduce

import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.client import CatClient

from .search_index_weights import execute_query


class Rocchio:
    def __init__(self):
        self.alpha = 1
        self.beta = 10
        self.n_rounds = 10
        self.k = 5
        self.r = 5

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

        return list(map(set_term_weights, query))

    @staticmethod
    def __term_vector_to_query(tw):
        return list(map(lambda x: x[0] + '^' + str(x[1]), tw))

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

    def __prune_query(self, q):
        p = q[0:self.r]
        p.sort(key=lambda el: el[1])
        for i in range(self.r, len(q)):
            for j in range(0, self.r):
                if q[i][1] > p[j][1]:
                    p.insert(j, q[i])
                    break
        return p[0:self.r]

    @staticmethod
    def __store_results(query, documents):
        return {
            'query': query,
            'documents': list(map(lambda d: {
                'path': d.path.split('\\')[1],
                'score': d.meta.score
            }, documents))
        }

    def update_parameters(self, alpha, beta, n_rounds, k, r):
        self.alpha = self.alpha if alpha is None else alpha
        self.beta = self.beta if beta is None else beta
        self.n_rounds = self.n_rounds if n_rounds is None else n_rounds
        self.k = self.k if k is None else k
        self.r = self.r if k is None else r

    def query(self, index, query):
        result = []
        documents = None

        q = Rocchio.__query_to_term_vector(query)
        q.sort(key=lambda el: el[0])
        client = Elasticsearch()

        for it in range(self.n_rounds):
            docs = execute_query(index, query, self.k)
            if len(docs) == 0:
                if documents is None:
                    print('No documents found!')
                    return
                else:
                    break
            else:
                documents = docs

            result.append(Rocchio.__store_results(query, documents))
            relevant_term_vectors = list(map(lambda doc: Rocchio.__to_tf_idf(client, index, doc.meta.id), documents))

            # alpha * query
            terms, weights = zip(*q)
            weights = (self.alpha * np.array(weights)).tolist()
            old = list(zip(terms, weights))

            # beta * sum(docs)
            sum_relevant_documents = reduce(Rocchio.__add_term_vectors, relevant_term_vectors)
            terms, weights = zip(*sum_relevant_documents)
            weights = (self.beta * np.array(weights) / len(sum_relevant_documents)).tolist()
            relevant = list(zip(terms, weights))

            q = Rocchio.__add_term_vectors(old, relevant)
            q = self.__prune_query(q)
            q = Rocchio.__normalize(q)
            q.sort(key=lambda el: el[0])
            query = Rocchio.__term_vector_to_query(q)

        documents = execute_query(index, query, self.k)
        result.append(Rocchio.__store_results(query, documents))
        return result
