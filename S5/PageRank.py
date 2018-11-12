import numpy as np

from Edge import Edge
from Airport import Airport

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes.txt'

MAX_ITERATIONS = 100
EPSILON = 1e-3
LAMBDA = 0.9


def calculate_weight(p, edges):
    weights = np.zeros(len(edges))
    out_weights = np.zeros(len(edges))
    for index, edge in enumerate(edges):
        weights[index] = edge.weight
        out_weights[index] = airports_hash[edge.origin].out_weight


def compute_page_ranks(airports_list, edge_list, edge_hash):
    n = len(airports_hash)
    airports_list[0].rank = 1
    i, diff = 0, 1
    while i < MAX_ITERATIONS and diff < EPSILON:
        q = np.zeros(n)
        for j in range(n):
            edges = airports_list[j].routes
            edges_weights = np.array(list(map(lambda e: e.weight, edges)))
            out_weights = np.array(list(map(lambda e: airports_hash[e.origin].out_weight, edges)))
            q[j] = LAMBDA * (p[j] * edges_weights / out_weights) + (1 - LAMBDA)/n


def output_page_ranks():
    airports_list = list(airports_hash.items())
    airports_list.sort(key=lambda kv: kv[1].rank, reverse=True)
    for _, airport in airports_list:
        print('{} ({}): {}'.format(airport.name, airport.code, airport.rank))


if __name__ == '__main__':
    airports_hash = Airport.read_airports(AIRPORTS_FILE)
    edge_list, edge_hash = Edge.read_routes(ROUTES_FILE, airports_hash)
    # time1 = time.time()
    # iterations = computePageRanks()
    # time2 = time.time()
    output_page_ranks()
    # print("#Iterations:", iterations)
    # print("Time of computePageRanks():", time2-time1)
