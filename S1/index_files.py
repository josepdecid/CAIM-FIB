"""
:Description: IndexFiles
    Indexes a set of files under the directory passed as a parameter (--path).
    in the index name passed as a parameter (--index).
    If the index exists it is dropped and created new.
    The documents are created with a 'path' and a 'text' fields.
"""

import argparse
import codecs
import os
from functools import reduce

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index


def generate_files_list(path):
    """
    Generates a list of all the files inside a path (recursively)
    :param path: Where files are located
    :return: list of files inside a path
    """
    return reduce(lambda acc, walk: acc + [walk[0] + '/' + file for file in walk[2]], os.walk(path), [])


def generate_documents_list(files, index):
    print('Indexing %d files' % len(files))
    print('Reading files...')

    documents = []
    for file in files:
        documents.append({
            '_op_type': 'index',
            '_index': index,
            '_type': 'document',
            'path': file[0],
            'text': reduce(lambda x, y: x + y, codecs.open(file, 'r', encoding='iso-8859-1'), '')
        })
    return documents


def insert_document_to_index(documents, index, keep):
    client = Elasticsearch()

    idx = Index(index, using=client)

    if idx.exists() and not keep:
        print('Removing existing index...')
        idx.delete()

    if not idx.exists():
        print('Creating index')
        idx.settings(number_of_shards=1)
        idx.create()

    print('Indexing ...')
    bulk(client, documents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, default=None, help='Path to the files')
    parser.add_argument('--index', required=True, default=None, help='Index for the files')
    parser.add_argument('--keep', required=False, default=False, help='Remove index if already exists')
    args = parser.parse_args()

    list_files = generate_files_list(args.path)
    list_documents = generate_documents_list(list_files, args.index)
    insert_document_to_index(list_documents, args.index, args.keep)
