import codecs
import os
import random
import sys
from functools import reduce

import matplotlib.pyplot as plt
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index
from scipy.optimize import curve_fit

sys.path.append('..')
from count_words import count_words


def heaps_fun(n, k, beta):
    return k * (n ** beta)


def generate_files_list(path):
    return reduce(lambda acc, walk: acc + [walk[0] + '/' + file for file in walk[2]], os.walk(path), [])


def bulk_insert_indices(list_docs):
    print('Inserting {} documents...'.format(len(list_docs)))
    client = Elasticsearch()
    for doc in list_docs:
        idx = Index(doc['_index'], using=client)
        if idx.exists():
            idx.delete()
        idx.settings(number_of_shards=1)
        idx.create()
    bulk(client, list_docs, request_timeout=120)


class HeapsLaw:
    k = 0
    beta = 0

    words = []
    distinct_words = []

    def __init__(self, index, path, num_subsets):
        self.index = index
        self.path = path
        self.num_subsets = num_subsets

    def generate_random_indices(self):
        list_files = generate_files_list(self.path)

        for i in range(self.num_subsets):
            list_docs = []
            selected_documents = random.sample(range(0, len(list_files)), random.randint(1, len(list_files) - 1))
            for index in selected_documents:
                list_docs.append({
                    '_op_type': 'index',
                    '_index': '{}_{}'.format(self.index, str(i)),
                    '_type': 'document',
                    'text': reduce(lambda x, y: x + y, codecs.open(list_files[index], 'r', encoding='iso-8859-1'), '')
                })

            bulk_insert_indices(list_docs)
            print('Created {}/{}'.format(i + 1, self.num_subsets))

    def count_words_and_distincts(self):
        self.words = []
        self.distinct_words = []
        for i in range(self.num_subsets):
            data = count_words('novels_{}'.format(str(i)), False, False)
            self.distinct_words.append(len(data))
            self.words.append(sum(list(zip(*data))[0]))
        words = zip(self.words, self.distinct_words)
        words = sorted(words, key=lambda x: x[0])
        self.words, self.distinct_words = zip(*words)

    def interpolate_parameters(self):
        p_opt, _ = curve_fit(heaps_fun, xdata=self.words, ydata=self.distinct_words, maxfev=5000)
        self.k, self.beta = p_opt

    def get_params(self):
        return self.k, self.beta

    def plot_results(self, left=None, right=None, bottom=None, top=None, extra='', log=False):
        x_grid = np.linspace(min(self.words), max(self.words), num=100)
        y_grid = list(map(lambda word: heaps_fun(word, self.k, self.beta), x_grid))

        if not log:
            plt.plot(self.words, self.distinct_words, 'o', label='Real values')
            plt.plot(x_grid, y_grid, '-', label='Prediction')
        else:
            plt.loglog(self.words, self.distinct_words, 'o', label='Real values')
            plt.loglog(x_grid, y_grid, '-', label='Prediction')

        plt.title('Heaps Analysis {}'.format(extra))
        plt.xlabel('Words')
        plt.ylabel('Distinct Words')

        plt.xlim(left, right)
        plt.ylim(bottom, top)

        plt.legend()
        plt.show()
