from __future__ import print_function

from Airport import Airport

AIRPORTS_FILE = 'airports_filtered.txt'
ROUTES_FILE = 'routes.txt'


edgeList = []  # list of Edge
edgeHash = dict()  # hash of edge to ease the match


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
    airports_list, airports_hash = Airport.read_airports(AIRPORTS_FILE)
    readRoutes(ROUTES_FILE)
    # time1 = time.time()
    # iterations = computePageRanks()
    # time2 = time.time()
    # outputPageRanks()
    # print("#Iterations:", iterations)
    # print("Time of computePageRanks():", time2-time1)
