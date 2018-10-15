"""
:Description: IndexFilesPreprocess
    Indexes a set of files under the directory passed as a parameter (--path)
    in the index name passed as a parameter (--index)
    Add configuration of the default analyzer: tokenizer  (--token) and filter (--filter)
    --filter must be always the last flag
    If the index exists it is dropped and created new
"""

from __future__ import print_function

import argparse
import codecs
import os
from functools import reduce

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index, analyzer, tokenizer

TOKENIZER_CHOICES = ['standard', 'whitespace', 'classic', 'letter']
FILTER_CHOICES = ['lowercase', 'asciifolding', 'stop', 'stemmer', 'porter_stem', 'kstem', 'snowball']


def generate_files_list(path):
    """
    Generates a list of all the files inside a path (recursively)
    :param path: Where files are located
    :return: list of files inside a path
    """
    return reduce(lambda acc, walk: acc + [walk[0] + '/' + file for file in walk[2]], os.walk(path), [])


def validate_filters(filters):
    for text_filter in filters:
        if text_filter not in FILTER_CHOICES:
            raise NameError('invalid filter, must be a subset of {}'.format(', '.join(FILTER_CHOICES)))


def generate_documents_list(files, index):
    print('Indexing %d files' % len(files))
    print('Reading files...')

    documents = []
    for file in files:
        documents.append({
            '_op_type': 'index',
            '_index': index,
            '_type': 'document',
            'path': file,
            'text': reduce(lambda x, y: x + y, codecs.open(file, 'r', encoding='iso-8859-1'), '')
        })
    return documents


def insert_document_to_index(documents, text_an, index, keep):
    client = Elasticsearch()

    idx = Index(index, using=client)

    if idx.exists() and not keep:
        print('Removing existing index...')
        idx.delete()

    if not idx.exists():
        print('Creating index')
        idx.create()

    idx.close()
    idx.analyzer(text_an)

    client.indices.put_mapping(doc_type='document', index=index,
                               body={'document': {'properties': {'path': {'type': 'keyword'}}}})

    idx.save()
    idx.open()

    print("Index settings=", idx.get_settings())
    print('Indexing ...')
    bulk(client, documents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, default=None, help='Path to the files')
    parser.add_argument('--index', required=True, default=None, help='Index for the files')
    parser.add_argument('--token', default='standard', choices=TOKENIZER_CHOICES, help='Text tokenizer')
    parser.add_argument('--filter', default=['lowercase'], nargs=argparse.REMAINDER, help='Text filters')
    parser.add_argument('--keep', required=False, default=False, help='Remove index if already exists')
    args = parser.parse_args()

    validate_filters(args.filter)
    list_files = generate_files_list(args.path)
    list_documents = generate_documents_list(list_files, args.index)
    text_analyzer = analyzer('default', type='custom', tokenizer=tokenizer(args.token), filter=args.filter)
    insert_document_to_index(list_documents, text_analyzer, args.index, args.keep)
