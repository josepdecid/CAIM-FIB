import re
from typing import Dict


class Airport:
    def __init__(self, index=0, iata=None, name=None):
        self.index = index
        self.code = iata
        self.name = name
        self.routes = []
        self.route_hash = {}
        self.out_weight = 1  # write appropriate value

    def __repr__(self):
        return "{0}\t{1}".format(self.code, self.name)

    @staticmethod
    def read_airports(path):
        airports_hash: Dict[str, Airport] = {}  # hash key IATA code -> Airport
        count = 0

        print('Reading Airport file from {}'.format(path))
        with open(path, mode='r', encoding='utf8') as f:
            for line in f.readlines():
                s = line.split(',')
                if not re.match('"[A-Z]{3}"', s[4]):
                    continue  # Invalid or missing IATA code (omit airport)

                name = s[1][1:-1] + ', ' + s[3][1:-1]
                iata_code = s[4][1:-1]

                if iata_code in airports_hash:
                    continue  # Airport with this IATA code is duplicated (omit replica)

                a = Airport(index=count, name=name, iata=iata_code)

                airports_hash[a.code] = a

                count += 1
        print('There were {} Airports with IATA code'.format(count))

        return airports_hash
