import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def zipf_fun(rank, a, b, c):
    return c / (rank + b) ** a


class ZipfLaw:
    a = 0
    b = 0
    c = 0

    words = []
    indices = []
    appearances = []

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.dictionary = {}

    def create_dictionary_map(self, path):
        with open(path, mode='r') as f:
            for line in f.readlines():
                self.dictionary[line.lower()] = True

    def filter_proper_words_dictionary(self, path, behead=0):
        self.words = []
        self.create_dictionary_map(path)

        ith = 1
        with open(self.path, mode='r') as f:
            lines = f.readlines()
            for line in lines:
                if ':' not in line:
                    continue
                target_appearances, target_text = line.split(': ', maxsplit=1)
                if target_text.lower() in self.dictionary:
                    self.words.append((ith, int(target_appearances), target_text))
                    ith = ith + 1
        self.words = self.words[behead:]

    def filter_proper_words_regex(self):
        pass

    def interpolate_parameters(self):
        self.indices, self.appearances, _ = zip(*self.words)
        p_opt, _ = curve_fit(zipf_fun, xdata=self.indices, ydata=self.appearances, maxfev=5000)
        self.a, self.b, self.c = p_opt

    def get_params(self):
        return self.a, self.b, self.c

    def get_mse(self):
        y_hat = list(map(lambda index: zipf_fun(index, self.a, self.b, self.c), self.indices))
        return ((np.array(self.appearances) - np.array(y_hat)) ** 2).mean()

    def plot_results(self, left=None, right=None, bottom=None, top=None, markersize=5, extra='', log=False):
        x_grid = np.linspace(min(self.indices), max(self.indices), num=100)
        y_grid = list(map(lambda word: zipf_fun(word, self.a, self.b, self.c), x_grid))

        if not log:
            plt.plot(self.indices, self.appearances, 'o', label='Real values', markersize=markersize)
            plt.plot(x_grid, y_grid, '-', label='Prediction')
        else:
            plt.loglog(self.indices, self.appearances, 'o', label='Real values', markersize=markersize)
            plt.loglog(x_grid, y_grid, '-', label='Prediction')

        plt.title('{} Analysis {}'.format(self.name, extra))
        plt.xlabel('Indices')
        plt.ylabel('Appearances')

        plt.xlim(left, right)
        plt.ylim(bottom, top)

        plt.legend()
        plt.show()
