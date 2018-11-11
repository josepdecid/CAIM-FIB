import re

with open('airports.txt', 'r') as f:
    airports_with_iata = []
    for line in f.readlines():
        parsed_line = line.split(',')
        iata_code = parsed_line[4]
        if re.match(r'"[A-Z]{3}"', iata_code):
            airports_with_iata.append(line)
    with open('airports_filtered.txt', 'w') as ff:
        ff.write(''.join(airports_with_iata))
