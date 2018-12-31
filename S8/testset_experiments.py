import time

import matplotlib.pyplot as plt

from lsh import LSH, brute_force_search

FIRST_TEST_IMAGE_INDEX = 1500
MAX_INDEX = 1797

K = 20
M = 5


def time_lsh(ub):
    ts = time.time()

    lsh = LSH(K, M)

    test_images = range(FIRST_TEST_IMAGE_INDEX, FIRST_TEST_IMAGE_INDEX + ub)
    for i in test_images:
        image = lsh.data[i]
        candidates = lsh.candidates(image)
        _ = lsh.search(image, candidates)

    te = time.time()
    return te - ts


def time_brute_force(ub):
    ts = time.time()

    test_images = range(FIRST_TEST_IMAGE_INDEX, FIRST_TEST_IMAGE_INDEX + ub)
    for i in test_images:
        _ = brute_force_search(i)

    te = time.time()
    return te - ts


if __name__ == '__main__':
    test_sizes = list(range(10, MAX_INDEX - FIRST_TEST_IMAGE_INDEX, 5))
    lsh_times = []
    bf_times = []

    for upper_bound in test_sizes:
        t_lsh = time_lsh(upper_bound)
        lsh_times.append(t_lsh)

        t_bf = time_brute_force(upper_bound)
        bf_times.append(t_bf)

        print(f'test size: {upper_bound:>3}, time (lsh): {t_lsh:.8f}, time (bf): {t_bf:.8f}')

    plt.plot(test_sizes, lsh_times, label='LSH')
    plt.plot(test_sizes, bf_times, label='Brute-force')
    plt.xlabel('Test set size')
    plt.ylabel('Execution time (s)')
    plt.legend()
    plt.savefig('images/ts_time.png', dpi=300)
    plt.show()
