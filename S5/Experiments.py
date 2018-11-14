import time
import sys
import numpy as np
from math import sqrt
from Airport import Airport
from Result import Result

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes_filtered.txt'
RESULTS_FILE = 'results.txt'

EPSILON = 1e-8
PRECISION = 5e-2
MAX_ITERATIONS = 1000
LAMBDA = 0.9


def clear_ranks():
    for k in airports_hash:
        airports_hash[k].rank = 0.0        
        airports_hash[k].new_rank = -1.0


def init_ranks_1_div_n():
    clear_ranks()
    for k in airports_hash:
        airports_hash[k].rank = 1.0/n


def init_ranks_1_zeros():
    clear_ranks()
    # get "first" element key (there aren't really any first elements in a dict object, but we don't care which one we get).
    if len(airports_hash) > 0:
        key = next(iter(airports_hash))
        airports_hash[key].rank = 1.0


def init_ranks_sqrt_n():
    clear_ranks()
    sqrt_n = int(sqrt(n))
    count = 1
    for k in airports_hash:
        airports_hash[k].rank = 1.0/sqrt_n
        if count == sqrt_n:
            break
        count += 1


def init_ranks_random():
    clear_ranks()
    x = np.random.rand(n)
    x /= sum(x)
    count = 0
    for k in airports_hash:
        airports_hash[k].rank = x[count]
        count += 1


def update_ranks():
    for k in airports_hash:
        airports_hash[k].update_ranks()


def check_similarity_ranks():
    for airport in airports_hash.values():
        if abs(airport.rank - airport.new_rank) > EPSILON:
            return False
    return True


def check_sum():
    sum = 0
    for airport in airports_hash.values():
        sum += airport.rank
    return abs(1 - sum) < PRECISION


def calculate_sink_sum():
    return sum([airports_hash[k].rank for k in airports_sink])


def calculate_weight(airport):
    weight = 0.0
    for origin, edge_weight in airport.routes.items():
        origin_airport = airports_hash[origin]
        value = origin_airport.rank
        value *= edge_weight
        value /= origin_airport.out_weight
        weight += value
    return weight


def compute_page_ranks():
    print('sum == 1? ', check_sum())
    iterations = 0
    while iterations < MAX_ITERATIONS:
        iterations += 1
        sink_value = calculate_sink_sum()
        for k, airport in airports_hash.items():
            airports_hash[k].new_rank = LAMBDA
            airports_hash[k].new_rank *= calculate_weight(airport)
            airports_hash[k].new_rank += (1 - LAMBDA + LAMBDA*sink_value)/n
        if check_similarity_ranks():
            break
        update_ranks()
        # TODO: treure checkSum
        csum = check_sum()
        if csum != 1:
            print('sum == 1? ', csum)
    return iterations


def extract_results_airports():
    res = {}
    for k, airport in airports_hash.items():
        res[k] = airport.rank
    return res


def experiment_lambda_rounds(init_function, init_type):
    for i in range(5, 10):
        LAMBDA = i*0.1
        time1 = time.time()
        init_function()
        iterations = compute_page_ranks()
        time2 = time.time()
        t = time2 - time1
        r = Result(t, iterations, extract_results_airports())
        if init_type not in results:
            results[init_type] = {}
        lambda_str = '{:.1f}'.format(LAMBDA)
        results[init_type][lambda_str] = r
        print(init_type, lambda_str)
        print("#Iterations:", iterations)
        print("Time of compute_page_ranks():", time2-time1)
        # output_page_ranks_file('results' + init_type + lambda_str + '.txt')


def fmse(xdata, ydata, popt, func):
    x = np.array(list(map(lambda x: func(x, *popt), xdata)))
    y = np.array(ydata)
    return ((x - y)**2).mean(axis=None)


def output_page_ranks_file(path):
    with open(path, mode='w', encoding='utf8') as f:
        results = list(airports_hash.values())
        results.sort(key=lambda res: res.rank, reverse=True)
        for elem in results:
            f.write('{} ({}): {}\n'.format(elem.name, elem.code, elem.rank))


if __name__ == '__main__':
    airports_hash = Airport.read_airports(AIRPORTS_FILE)
    n = len(airports_hash)
    airports_sink = Airport.read_routes(ROUTES_FILE, airports_hash)

    results = {}

    # 1/n key: 1Dn
    experiment_lambda_rounds(init_ranks_1_div_n, "1Dn")

    # One 1 key: oneOne
    experiment_lambda_rounds(init_ranks_1_zeros, "oneOne")

    # sqrt n key: sqrtN
    experiment_lambda_rounds(init_ranks_sqrt_n, "sqrtN")

    # random key: random
    experiment_lambda_rounds(init_ranks_random, "random")