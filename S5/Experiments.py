import time
import sys
import numpy as np
import PageRank as pr
from Airport import Airport

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes_filtered.txt'


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
        if init_type not in results:
            results[init_type] = {}
        lambda_str = '{:.1f}'.format(lambda_value)
        results[init_type][lambda_str] = {}
        results[init_type][lambda_str]['iterations'] = iterations
        results[init_type][lambda_str]['time'] = t
        results[init_type][lambda_str]['ranks'] = extract_results_airports(airports_hash)
        # print(init_type, lambda_str)
        # print("#Iterations:", iterations)
        # print("Time of compute_page_ranks():", time2-time1)
        # pr.output_page_ranks_file(
        #     'results/results_' + init_type + lambda_str + '.txt', airports_hash)


def fmae(xdata, ydata):
    n = len(xdata)
    x = []
    y = []
    sum_diffs = 0.0
    for key, value in xdata.items():
        sum_diffs += abs(value - ydata[key])
    return sum_diffs/n


def compute_output_results(path, results):
    with open(path, mode='w', encoding='utf8') as f:
        # Time and iterations
        f.write('TIMES ITERATIONS:\n')
        for init, lambdas in results.items():
            for l, res in lambdas.items():
                f.write('{} and {} -> time: {}, iters: {}\n'.format(init, l, res['time'], res['iterations']))
            f.write('\n')

        f.write('LAMBDA VALUES:\n')
        lambs = ['0.9', '0.8', '0.7', '0.6', '0.5']
        for init in results:
            res_compare = lambs[0]
            xdata = results[init][res_compare]['ranks']
            for l in lambs[1:]:
                ydata = results[init][l]['ranks']
                f.write('MSE {} of {} with {}: {}\n'.format(init, res_compare, l, fmae(xdata, ydata)))
            f.write('\n')
        f.write('DIFF INITS:\n')
        linits = ['1Dn', 'oneOne', 'sqrtN', 'random']
        for l in lambs:
            res_compare = linits[0]
            xdata = results[res_compare][l]['ranks']
            for init in linits[1:]:
                ydata = results[init][l]['ranks']
                f.write('MSE {} of {} with {}: {}\n'.format(l, res_compare, init, fmae(xdata, ydata)))
            f.write('\n')


if __name__ == '__main__':
    airports_hash = Airport.read_airports(AIRPORTS_FILE)
    airports_sink = Airport.read_routes(ROUTES_FILE, airports_hash)

    results = {}

    # 1/n key: 1Dn
    experiment_lambda_rounds(airports_hash, airports_sink,
                             results, pr.init_ranks_1_div_n, '1Dn')

    # One 1 key: oneOne
    experiment_lambda_rounds(airports_hash, airports_sink,
                             results, pr.init_ranks_1_zeros, 'oneOne')

    # sqrt n key: sqrtN
    experiment_lambda_rounds(airports_hash, airports_sink,
                             results, pr.init_ranks_sqrt_n, 'sqrtN')

    # random key: random
    experiment_lambda_rounds(airports_hash, airports_sink,
                             results, pr.init_ranks_random, 'random')

    compute_output_results('results/report.txt', results)
