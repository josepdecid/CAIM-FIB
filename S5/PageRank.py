import time
import sys
import numpy as np
from math import sqrt
from Airport import Airport

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes_filtered.txt'
RESULTS_FILE = 'results.txt'

# EPSILON = 1e-8
# PRECISION = 5e-2
# MAX_ITERATIONS = 1000
# LAMBDA = 0.9


def clear_ranks(airports_hash):
    for k in airports_hash:
        airports_hash[k].rank = 0.0
        airports_hash[k].new_rank = -1.0


def init_ranks_1_div_n(airports_hash):
    clear_ranks(airports_hash)
    n = len(airports_hash)
    for k in airports_hash:
        airports_hash[k].rank = 1.0/n


def init_ranks_1_zeros(airports_hash):
    clear_ranks(airports_hash)
    # get "first" element key (there aren't really any first elements in a dict object, but we don't care which one we get).
    if len(airports_hash) > 0:
        key = next(iter(airports_hash))
        airports_hash[key].rank = 1.0


def init_ranks_sqrt_n(airports_hash):
    clear_ranks(airports_hash)
    n = len(airports_hash)
    sqrt_n = int(sqrt(n))
    count = 1
    for k in airports_hash:
        airports_hash[k].rank = 1.0/sqrt_n
        if count == sqrt_n:
            break
        count += 1


def init_ranks_random(airports_hash):
    clear_ranks(airports_hash)
    x = np.random.rand(len(airports_hash))
    x /= sum(x)
    count = 0
    for k in airports_hash:
        airports_hash[k].rank = x[count]
        count += 1


def update_ranks(airports_hash):
    for k in airports_hash:
        airports_hash[k].update_rank()


def check_similarity_ranks(airports_hash, epsilon):
    for airport in airports_hash.values():
        if abs(airport.rank - airport.new_rank) > epsilon:
            return False
    return True


def check_sum(airports_hash, precision=5e-2):
    sum_ranks = 0
    for airport in airports_hash.values():
        sum_ranks += airport.rank
    return abs(1 - sum_ranks) < precision


def calculate_sink_sum(airports_hash, airports_sink):
    return sum([airports_hash[k].rank for k in airports_sink])


def calculate_weight(airport, airports_hash):
    weight = 0.0
    for origin, edge_weight in airport.routes.items():
        origin_airport = airports_hash[origin]
        value = origin_airport.rank
        value *= edge_weight
        value /= origin_airport.out_weight
        weight += value
    return weight


def compute_page_ranks(airports_hash={}, airports_sink={}, lambda_value=0.8, epsilon=1e-8, precision=5e-2, max_iterations=1000, init_ranks=init_ranks_1_div_n):
    init_ranks(airports_hash)
    n = len(airports_hash)
    # print('sum == 1? ', check_sum(airports_hash))
    iterations = 0
    while iterations < max_iterations:
        iterations += 1
        sink_value = calculate_sink_sum(airports_hash, airports_sink)
        for k, airport in airports_hash.items():
            airports_hash[k].new_rank = lambda_value
            airports_hash[k].new_rank *= calculate_weight(
                airport, airports_hash)
            airports_hash[k].new_rank += (1 -
                                          lambda_value + lambda_value*sink_value)/n
        if check_similarity_ranks(airports_hash, epsilon):
            break
        update_ranks(airports_hash)
        # print('sum == 1? ', check_sum(airports_hash))
    return iterations


def output_page_ranks(airports_hash):
    results = list(airports_hash.values())
    results.sort(key=lambda res: res.rank, reverse=True)
    for elem in results:
        print('{} ({}): {}\n'.format(elem.name, elem.code, elem.rank))


def output_page_ranks_file(path, airports_hash):
    with open(path, mode='w', encoding='utf8') as f:
        results = list(airports_hash.values())
        results.sort(key=lambda res: res.rank, reverse=True)
        for elem in results:
            f.write('{} ({}): {}\n'.format(elem.name, elem.code, elem.rank))


if __name__ == '__main__':
    airports_hash = Airport.read_airports(AIRPORTS_FILE)
    airports_sink = Airport.read_routes(
        ROUTES_FILE, airports_hash=airports_hash)
    time1 = time.time()
    iterations = compute_page_ranks(
        airports_hash=airports_hash, airports_sink=airports_sink)
    time2 = time.time()
    output_page_ranks_file(RESULTS_FILE, airports_hash=airports_hash)
    print("#Iterations:", iterations)
    print("Time of compute_page_ranks():", time2 - time1)
