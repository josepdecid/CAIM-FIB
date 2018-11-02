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
    def __add_term_vectors(source, addition):
        for k, v in addition.items():
            if k in source:
                source[k] += v
            else:
                source[k] = v

    @staticmethod
    def __query_to_term_vector(query):
        query_tw = {}
        for term in query:
            s = term.split('^')
            if len(s) == 1:
                query_tw[term] = 1
            else:
                query_tw[s[0]] = float(s[1])
        return query_tw

    @staticmethod
    def __term_vector_to_query(tw):
        return list(map(lambda x: x[0] + '^' + str(x[1]), tw.items()))

    @staticmethod
    def __normalize(tw):
        norm = np.linalg.norm(list(tw.values()))
        return {k: w / norm for k, w in tw.items()}

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

        vector = dict(map(tf_idf, zip(term_frequency, document_appearances)))
        return Rocchio.__normalize(vector)

    def __prune_query(self, q):
        q = list(q.items())
        p = q[0:self.r]
        p.sort(key=lambda el: el[1], reverse=True)
        for i in range(self.r, len(q)):
            for j in range(0, self.r):
                if q[i][1] > p[j][1]:
                    p.insert(j, q[i])
                    break
        return dict(p[0:self.r])

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

        q = Rocchio.__query_to_term_vector(query)
        client = Elasticsearch()

        for it in range(self.n_rounds):
            documents = execute_query(index, query, self.k)
            if len(documents) == 0:
                break

            result.append(Rocchio.__store_results(query, documents))
            relevant_term_vectors = list(map(lambda doc: Rocchio.__to_tf_idf(client, index, doc.meta.id), documents))

            # alpha * query
            q.update((k, v * self.alpha) for k, v in q.items())

            # beta * sum(docs)
            sum_relevant_documents = {}
            for rel in relevant_term_vectors:
                Rocchio.__add_term_vectors(source=sum_relevant_documents, addition=rel)
            sum_relevant_documents.update((k, self.beta * np.array(v) / len(sum_relevant_documents)) for k, v in
                                          sum_relevant_documents.items())

            Rocchio.__add_term_vectors(q, sum_relevant_documents)
            q = self.__prune_query(q)
            q = Rocchio.__normalize(q)
            query = Rocchio.__term_vector_to_query(q)

        documents = execute_query(index, query, self.k)
        result.append(Rocchio.__store_results(query, documents))
        return result
