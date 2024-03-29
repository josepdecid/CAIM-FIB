import os
from numpy.random import choice

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='documents.txt', help='Data with the examples')
    parser.add_argument('--nclust', default=2, type=int, help='Number of clusters')
    parser.add_argument('--folder', default='', help='Experiments folder')

    args = parser.parse_args()
    previous_folder = args.folder.split('/')[0]
    args.data = f'{previous_folder}/{args.data}'

    f = open(args.data, 'r')

    ldocs = []
    for line in f:
        doc, words = line.split(':')
        ldocs.append(words)

    # Generate nclust prototypes with nclust random documents
    doc = choice(range(len(ldocs)), args.nclust)
    if not os.path.exists(args.folder):
        os.mkdir(args.folder)
    f = open(f'{args.folder}/prototypes.txt', 'w')
    for i, d in enumerate(doc):
        docvec = ''
        for v in ldocs[d].split():
            docvec += (v + '+1.0 ')
        f.write('CLASS' + str(i) + ':' + docvec.encode('ascii', 'replace').decode() + '\n')
    f.flush()
    f.close()
