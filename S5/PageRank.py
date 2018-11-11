from __future__ import print_function

import re
from collections import namedtuple
import time
import sys
from Edge import Edge
from Airport import Airport

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes.txt'


edgeList = []  # list of Edge
edgeHash = dict()  # hash of edge to ease the match
airportList = []  # list of Airport
airportHash = dict()  # hash key IATA code -> Airport


def read_airports(path):
    print('Reading Airport file from {0}'.format(path))
    with open(path, mode='r', encoding='utf8') as f:
        cont = 0
        for line in f.readlines():
            s = line.split(',')
            if not re.match('"[A-Z]{3}"', s[4]):
                continue # Invalid or missing IATA code

            a = Airport()
            a.name = s[1][1:-1] + ", " + s[3][1:-1]
            a.code = s[4][1:-1]

            airportList.append(a)
            airportHash[a.code] = a

            cont += 1
    print('There were {0} Airports with IATA code'.format(cont))


def readRoutes(fd):
    print("Reading Routes file from {0}".format(fd))
    # write your code


def computePageRanks():
    pass
    # write your code


def outputPageRanks():
    pass
    # write your code


if __name__ == '__main__':
    readAirports(AIRPORTS_FILE)
    readRoutes(ROUTES_FILE)
    # time1 = time.time()
    # iterations = computePageRanks()
    # time2 = time.time()
    # outputPageRanks()
    # print("#Iterations:", iterations)
    # print("Time of computePageRanks():", time2-time1)
