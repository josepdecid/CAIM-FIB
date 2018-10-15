import argparse
from itertools import chain, combinations
from os import system

TOKENS = ['whitespace', 'classic', 'standard', 'letter']
FILTERS = ['lowercase', 'asciifolding', 'stop', 'snowball', 'porter_stem', 'kstem']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, default=None, help='Path to the files')
    parser.add_argument('--index', required=True, default=None, help='Index for the files')
    args = parser.parse_args()

    filters_powerset = list(chain.from_iterable(combinations(FILTERS, r) for r in range(len(FILTERS) + 1)))[1:]

    for token in TOKENS:
        for filters_subset in filters_powerset:
            filters = ' '.join(filters_subset)
            index = '{}_{}_[{}]'.format(args.index, token, '_'.join(filters_subset))
            new_args = '--path {} --index {} --token {} --filter {}'.format(args.path, index, token, filters)
            system('python S2/index_files_preprocess.py {}'.format(new_args))
