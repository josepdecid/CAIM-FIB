"""
:Description: CountWords
    Generates a list with the counts and the words in the 'text' field of the documents in an index.
"""

import argparse
from functools import reduce

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch_dsl import Index


def count_words(index, alpha, reverse):
    client = Elasticsearch()
    if not Index(name=index, using=client).exists():
        print('Index {} does not exists'.format(index))

    counter = {}
    sc = scan(client=client, index=index, doc_type='document', query={'query': {'match_all': {}}})
    for s in sc:
        tv = client.termvectors(index=index, doc_type='document', id=s['_id'], fields=['text'])
        if 'text' in tv['term_vectors']:
            for term in tv['term_vectors']['text']['terms']:
                if term in counter:
                    counter[term] += tv['term_vectors']['text']['terms'][term]['term_freq']
                else:
                    counter[term] = tv['term_vectors']['text']['terms'][term]['term_freq']

    counted_words = list(map(lambda el: (counter[el], el.encode('utf8', 'ignore')), counter))
    return sorted(counted_words, key=lambda x: x[1 if alpha else 0], reverse=reverse)


def store_in_file(path, counted_words):
    store_data = reduce(lambda x, y: '{}{}: {}\n'.format(x, y[0], y[1].decode('utf8')), counted_words, '')
    store_data = store_data + 'Total words {}'.format(len(counted_words))
    with open(path, mode='w') as f:
        f.write(store_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    parser.add_argument('--reverse', action='store_true', default=False, help='Reverse order for being descendant')
    parser.add_argument('--file', default=False, help='Store data in a file in this path')
    args = parser.parse_args()

    data = count_words(args.index, args.alpha, args.reverse)
    if args.file:
        store_in_file(args.file, data)
