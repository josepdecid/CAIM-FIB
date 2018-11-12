import re

from Airport import Airport


class Edge:
    def __init__(self, origin: Airport = None):
        self.origin = origin  # write appropriate value
        self.weight = 1  # write appropriate value

    def __repr__(self):
        return 'edge: {0} {1}'.format(self.origin, self.weight)

    # write rest of code that you need for this class

    @staticmethod
    def read_routes(path, airports_hash):
        edge_list = []  # list of Edge
        edge_hash = {}  # hash of edge to ease the match

        print('Reading Route file from {0}'.format(path))
        with open(path, mode='r', encoding='utf8') as f:
            cont = 0
            for line in f.readlines():
                s = line.split(',')
                origin = s[2]
                destination = s[4]
                if not (re.match('[A-Z]{3}', origin) and re.match('[A-Z]{3}', destination)):
                    continue  # Invalid or missing IATA code

                e = Edge(origin)
                if destination not in airports_hash:
                    continue  # Route with non-registered airports
                a = airports_hash[destination]

                a.routes.append(e)
                a.route_hash['{}_{}'.format(origin, destination)] = e

                edge_list.append(e)
                edge_hash['{}_{}'.format(origin, destination)] = e

                cont += 1
        print('There were {0} Routes'.format(cont))
        return edge_list, edge_hash
