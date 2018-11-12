import re
from random import random
from typing import Dict


class Airport:
    def __init__(self, iata=None, name=None):
        self.code = iata
        self.name = name
        self.routes = []
        self.route_hash = {}
        self.out_weight = 1  # write appropriate value
        self.rank = random()

    def __repr__(self):
        return "{0}\t{1}".format(self.code, self.name)

    @staticmethod
    def read_airports(path):
        airport_hash: Dict[str, Airport] = {}  # hash key IATA code -> Airport

        print('Reading Airport file from {0}'.format(path))
        with open(path, mode='r', encoding='utf8') as f:
            cont = 0
            for line in f.readlines():
                s = line.split(',')
                if not re.match('"[A-Z]{3}"', s[4]):
                    continue  # Invalid or missing IATA code

                a = Airport()
                a.index = cont
                a.name = s[1][1:-1] + ', ' + s[3][1:-1]
                a.code = s[4][1:-1]

                airport_hash[a.code] = a

                cont += 1
        print('There were {0} Airports with IATA code'.format(cont))

        return airport_hash
