import time

import numpy as np

from Edge import Edge
from Airport import Airport

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes.txt'

MAX_ITERATIONS = 100
EPSILON = 1e-3
LAMBDA = 0.9


def calculate_weight(p, edges):
    weight = 0.0
    for edge in edges:
        origin_airport = airports_hash[edge.origin]
        value = p[origin_airport.index]
        value *= edge.weight
        value /= origin_airport.out_weight
        weight += value
    return weight


def compute_page_ranks():
    n = len(airports_hash)
    p = np.ones(n, dtype=float)
    p /= n  # Initial 1/n vector
    i, diff = 0, 1
    while i < MAX_ITERATIONS and diff >= EPSILON:
        i += 1
        q = np.zeros(n)
        for _, airport in airports_hash.items():
            q[airport.index] = LAMBDA * calculate_weight(p, airport.routes) + (1 - LAMBDA) / n
        diff = np.sum(abs(p - q))
        p = q
        print(np.sum(p))
    return p, i


def output_page_ranks(ranks):
    results = []
    for _, airport in airports_hash.items():
        results.append((airport.name, airport.code, ranks[airport.index]))
    results.sort(key=lambda res: res[2], reverse=True)
    for name, code, rank in results:
        print('{} ({}): {}'.format(name, code, rank))


if __name__ == '__main__':
    airports_hash = Airport.read_airports(AIRPORTS_FILE)
    Edge.read_routes(ROUTES_FILE, airports_hash)
    time1 = time.time()
    page_ranks, iterations = compute_page_ranks()
    time2 = time.time()
    output_page_ranks(page_ranks)
    print('#Iterations: ', iterations)
    print('Time of computePageRanks(): ', time2 - time1)
