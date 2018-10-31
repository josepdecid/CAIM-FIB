"""
:Description: SearchIndexWeight
Performs a AND query for a list of words (--query) in the documents of an index (--index)
You can use word^number to change the importance of a word in the match
--nhits changes the number of documents to retrieve
"""

import argparse
from functools import reduce

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
from elasticsearch_dsl.query import Q


def execute_query(index, query, nhits):
    client = Elasticsearch()
    if not Index(index, using=client).exists():
        print('Index "{}" does not exist'.format(index))
        exit(1)

    q = reduce(lambda queryset, current_query: queryset & Q('query_string', query=current_query), query, Q())
    s = Search(using=client, index=index).query(q)

    return s[0:nhits].execute()


def print_results(results):
    for res in results:
        print('ID= %s SCORE=%s' % (res.meta.id, res.meta.score))
        print('PATH= %s' % res.path)
        print('TEXT: %s' % res.text[:50])
        print('-' * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', required=True, help='Index to search')
    parser.add_argument('--nhits', default=10, type=int, help='Number of hits to return')
    parser.add_argument('--query', required=True, nargs=argparse.REMAINDER, help='List of words to search')
    args = parser.parse_args()

    print_results(execute_query(args.index, args.query, args.nhits))
