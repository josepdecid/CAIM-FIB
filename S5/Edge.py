import re


class Edge:
    def __init__(self, origin):
        self.origin = origin  # write appropriate value
        self.weight = 1  # write appropriate value

    def __repr__(self):
        return 'edge: {0} {1}'.format(self.origin, self.weight)

    # write rest of code that you need for this class

    @staticmethod
    def read_routes(path, airports_hash):
        print('Reading Route file from {}'.format(path))
        with open(path, mode='r', encoding='utf8') as f:
            count = 0
            for line in f.readlines():
                s = line.split(',')
                origin = s[2]
                destination = s[4]
                if not (re.match('[A-Z]{3}', origin) and re.match('[A-Z]{3}', destination)):
                    continue  # Invalid or missing IATA code
                elif origin not in airports_hash or destination not in airports_hash:
                    continue  # Route between non-registered airports

                e = Edge(origin)
                a = airports_hash[destination]
                a.routes.append(e)

                count += 1
        print('There were {} Routes'.format(count))