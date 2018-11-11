class Airport:
    def __init__(self, iata=None, name=None):
        self.code = iata
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 1 # write appropriate value

    def __repr__(self):
        return "{0}\t{2}\t{1}".format(self.code, self.name, self.pageIndex)