from functools import reduce
import matplotlib.pyplot as plt
import numpy as np

from lsh import LSH, brute_force_search

FIRST_TEST_IMAGE_INDEX = 1500


def search_lsh(params):
    for k, m in params:
        lsh = LSH(k, m)
        for i in range(FIRST_TEST_IMAGE_INDEX, FIRST_TEST_IMAGE_INDEX + 10):
            image = lsh.data[i]
            candidates = lsh.candidates(image)
            dist, j = lsh.search(image, candidates)
            if j is not None:
                plot_image_by_index(j, title=f'nearest_lsh_{i}_k{k}_m{m}')
            yield (i, (dist, j))


def search_brute_force():
    for i in range(FIRST_TEST_IMAGE_INDEX, FIRST_TEST_IMAGE_INDEX + 10):
        dist, j = brute_force_search(i)
        plot_image_by_index(j, title=f'nearest_bf_{i}')
        yield (i, (dist, j))


def plot_image_by_index(i, title=None):
    if title is None:
        title = f'test_{i}'
    data = np.load('images.npy')
    plt.imshow(data[i], interpolation='nearest', cmap='Greys')
    plt.title(f'{i}')
    plt.axis('off')
    plt.savefig(f'images/{title}.png')


def display_results(r):
    for k, v in r.items():
        lsh_results = reduce(lambda acc, x: f'{acc}{x["result"]:>4} {x["distance"]:>2} ', v['lsh'], '')
        print(f'{k} {v["bf"]["result"]:>4} {v["bf"]["distance"]:>2} {lsh_results}')

    for i in range(FIRST_TEST_IMAGE_INDEX, FIRST_TEST_IMAGE_INDEX + 10):
        plot_image_by_index(i)


def text(t):
    return '-' if t is None else t


if __name__ == '__main__':
    results = {}

    for idx, res in search_lsh([(1, 1), (20, 5), (50, 5), (100, 5)]):
        if idx not in results:
            results[idx] = {'lsh': []}
        results[idx]['lsh'].append({'result': text(res[1]), 'distance': text(res[0])})

    for idx, res in search_brute_force():
        results[idx]['bf'] = {'result': text(res[1]), 'distance': text(res[0])}

    display_results(results)
