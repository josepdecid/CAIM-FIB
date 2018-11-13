import time
import sys
from Airport import Airport

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes_filtered.txt'

EPSILON = 1e-8
PRECISION = 5e-2
MAX_ITERATIONS = 1000
LAMBDA = 0.8


def init_ranks():
    for k in airports_hash:
        airports_hash[k].rank = 1/n


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
    init_ranks()
    # print('sum == 1? ', check_sum())
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
        # print('sum == 1? ', check_sum())
    return iterations


def output_page_ranks():
    results = list(airports_hash.values())
    results.sort(key=lambda res: res.rank, reverse=True)
    for elem in results:
        print('{} ({}): {}\n'.format(elem.name, elem.code, elem.rank))


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
    time1 = time.time()
    iterations = compute_page_ranks()
    time2 = time.time()
    output_page_ranks_file('results.txt')
    print("#Iterations:", iterations)
    print("Time of compute_page_ranks():", time2-time1)
