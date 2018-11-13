import re


class Airport:
    def __init__(self, iata=None, name=None):
        self.code = iata
        self.name = name
        self.routes = {}  # edges: dict key origin, value weight
        self.out_weight = 0  # weight of outgoing edges
        self.rank = 0.0  # actuall rank
        self.new_rank = -1.0  # new rank

    def __repr__(self):
        return "{0}\t{1}".format(self.code, self.name)
        # return "{0}\t{2}\t{1}".format(self.code, self.name, self.pageIndex)

    def update_ranks(self):
        self.rank = self.new_rank

    @staticmethod
    def read_airports(path):
        airports_hash = {}  # hash key IATA code -> Airport

        print('Reading Airport file from {0}'.format(path))
        with open(path, mode='r', encoding='utf8') as f:
            cont = 0
            for line in f.readlines():
                s = line.split(',')
                if not re.match('"[A-Z]{3}"', s[4]):
                    continue  # Invalid or missing IATA code
                a = Airport(iata=s[4][1:-1],
                            name=s[1][1:-1] + ", " + s[3][1:-1])
                airports_hash[a.code] = a
                cont += 1
        print('There were {} Airports with IATA code'.format(cont))
        return airports_hash

    @staticmethod
    def read_routes(path, airports_hash={}):
        # airports_hash map with hash key IATA code -> Airport
        print('Reading Routes file from {0}'.format(path))
        with open(path, mode='r', encoding='utf8') as f:
            cont = 0
            for line in f.readlines():
                s = line.split(',')
                if not (re.match('[A-Z]{3}', s[2]) and re.match('[A-Z]{3}', s[4])):
                    continue  # Invalid or missing IATA code
                origin = s[2]
                destination = s[4]
                if not (origin in airports_hash and destination in airports_hash):
                    continue
                # If not existing route, init
                if origin not in airports_hash[destination].routes:
                    airports_hash[destination].routes[origin] = 0
                # Add weight to edge and outgoing
                airports_hash[destination].routes[origin] += 1
                airports_hash[origin].out_weight += 1
                cont += 1

            airports_sink = []
            for k in airports_hash:
                if len(airports_hash[k].routes) == 0:
                    airports_sink.append(k)
        print('There were {} valid Routes'.format(cont))
        return airports_sink
