import argparse

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import scan

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')

    args = parser.parse_args()

    index = args.index
    try:
        client = Elasticsearch()
        sc = scan(client, index=index, doc_type='document', query={"query": {"match_all": {}}})
        for r in sc:
            print(r['_source']['path'], '\t', r['_source']['text'].encode('ascii', 'replace'))
    except NotFoundError:
        raise (NameError('Index %s does not exists' % index))
