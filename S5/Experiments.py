import time
import sys
import numpy as np
import PageRank as pr
from Airport import Airport
from Result import Result

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes_filtered.txt'
RESULTS_FILE = 'results.txt'


def extract_results_airports(airports_hash):
    res = {}
    for k, airport in airports_hash.items():
        res[k] = airport.rank
    return res


def experiment_lambda_rounds(airports_hash, airports_sink, results, init_function, init_type):
    for i in range(5, 10):
        lambda_value = i*0.1
        time1 = time.time()
        init_function(airports_hash)
        iterations = pr.compute_page_ranks(
            airports_hash=airports_hash, airports_sink=airports_sink, lambda_value=lambda_value, init_ranks=init_function)
        time2 = time.time()
        t = time2 - time1
        r = Result(t, iterations, extract_results_airports(airports_hash))
        if init_type not in results:
            results[init_type] = {}
        lambda_str = '{:.1f}'.format(lambda_value)
        results[init_type][lambda_str] = r
        print(init_type, lambda_str)
        print("#Iterations:", iterations)
        print("Time of compute_page_ranks():", time2-time1)
        pr.output_page_ranks_file(
            'results/results_' + init_type + lambda_str + '.txt', airports_hash)


def fmse(xdata, ydata, popt, func):
    x = np.array(xdata)
    y = np.array(ydata)
    return ((x - y)**2).mean(axis=None)




def compute_output_results(path, results):
    for k, v in results.items():
        print(k, v)
    # time_its = time_iterations(path=path, init='1Dn', results)
    


if __name__ == '__main__':
    airports_hash = Airport.read_airports(AIRPORTS_FILE)
    airports_sink = Airport.read_routes(ROUTES_FILE, airports_hash)

    results = {}

    # 1/n key: 1Dn
    experiment_lambda_rounds(airports_hash, airports_sink,
                             results, pr.init_ranks_1_div_n, '1Dn')

#     # One 1 key: oneOne
#     experiment_lambda_rounds(airports_hash, airports_sink,
#                              results, pr.init_ranks_1_zeros, 'oneOne')

#     # sqrt n key: sqrtN
#     experiment_lambda_rounds(airports_hash, airports_sink,
#                              results, pr.init_ranks_sqrt_n, 'sqrtN')

#     # random key: random
#     experiment_lambda_rounds(airports_hash, airports_sink,
#                              results, pr.init_ranks_random, 'random')

    compute_output_results('results/report.txt', results)
