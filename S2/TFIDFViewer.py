"""
:Description: TFIDFViewer

    Receives two paths of files to compare (the paths have to be the ones used when indexing the files)
"""

import argparse

import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.client import CatClient
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from scipy.spatial.distance import cosine as cos_sim


def search_file_by_path(client, index, path):
    """
    Search for a file using its path

    :param path:
    :return:
    """
    s = Search(using=client, index=index)
    q = Q('match', path=path)  # exact search in the path field
    s = s.query(q)
    result = s.execute()

    lfiles = [r for r in result]
    if len(lfiles) == 0:
        raise NameError('File [%s] not found' % path)
    else:
        return lfiles[0].meta.id


def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, doc_type='document', id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())


def to_tf_idf(client, index, file_id):
    """
    Returns the term weights of a document
    :param client:
    :param index:
    :param file_id:
    :return:
    """

    # Get document terms frequency and overall terms document frequency
    term_frequency, document_appearances = document_term_vector(client, index, file_id)
    max_freq = max([f for _, f in term_frequency])
    document_count = doc_count(client, index)

    def tf_idf(params):
        (term, freq), (_, doc_freq) = params
        tf = freq / max_freq
        idf = np.log2(document_count / doc_freq)
        return term, tf * idf

    vector = list(map(tf_idf, zip(term_frequency, document_appearances)))
    return normalize(vector)


def print_term_weight_vector(twv):
    """
    Prints the term vector and the corresponding weights
    :param twv:
    :return:
    """
    for term, weight in twv:
        print('{}: {}'.format(term, weight))


def normalize(tw):
    """
    Normalizes the weights in tw so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw: Term words vector (not normalized)
    :return: Normalized tw
    """
    terms, weights = zip(*tw)
    normalized_weights = weights / np.linalg.norm(weights)
    return list(zip(terms, normalized_weights))


def cosine_similarity(tw1, tw2):
    """
    Computes the cosine similarity between two weight vectors, terms are alphabetically ordered
    :param tw1: Terms weight vector 1
    :param tw2: Terms weight vector 2
    :return: Similarity between two weight vectors.
    """

    def equalise():
        i, j = 0, 0
        terms1, weights1 = zip(*tw1)
        terms2, weights2 = zip(*tw2)
        new_weights1 = []
        new_weights2 = []
        while i < len(terms1) and j < len(terms2):
            if terms1[i] < terms2[j]:
                new_weights1.append(weights1[i])
                new_weights2.append(0)
                i = i + 1
            elif terms1[i] > terms2[j]:
                new_weights2.append(weights2[j])
                new_weights1.append(0)
                j = j + 1
            else:
                new_weights1.append(weights1[i])
                new_weights2.append(weights2[j])
                i = i + 1
                j = j + 1

        if i < len(terms1):
            new_weights1.extend(weights1[i:])
            new_weights2.extend([0] * (len(terms1) - i))
        if j < len(terms2):
            new_weights2.extend(weights2[j:])
            new_weights1.extend([0] * (len(terms2) - j))

        return new_weights1, new_weights2

    w1, w2 = equalise()
    return 1.0 - cos_sim(w1, w2)


def doc_count(client, index):
    """
    Returns the number of documents in an index
    :param client: ElasticSearch client
    :param index: Index to count documents from
    :return: number of documents for desired  index
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--files', default=None, required=True, nargs=2, help='Paths of the files to compare')
    parser.add_argument('--print', default=False, action='store_true', help='Print TF-IDF vectors')

    args = parser.parse_args()
    elastic_client = Elasticsearch()

    try:
        # Get the files ids
        file1_id = search_file_by_path(elastic_client, args.index, args.files[0])
        file2_id = search_file_by_path(elastic_client, args.index, args.files[1])

        # Compute the TF-IDF vectors
        file1_tw = to_tf_idf(elastic_client, args.index, file1_id)
        file2_tw = to_tf_idf(elastic_client, args.index, file2_id)

        if args.print:
            print('TF-IDF FILE %s' % args.files[0])
            print_term_weight_vector(file1_tw)
            print('---------------------')
            print('TF-IDF FILE %s' % args.files[1])
            print_term_weight_vector(file2_tw)
            print('---------------------')

        print("Similarity = %3.5f" % cosine_similarity(file1_tw, file2_tw))
    except NotFoundError:
        print('Index %s does not exists' % args.index)
