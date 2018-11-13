import re

with open('airports.txt', 'r', encoding='utf8') as f:
    airports_with_iata = []
    for line in f.readlines():
        parsed_line = line.split(',')
        iata_code = parsed_line[4]
        if re.match(r'"[A-Z]{3}"', iata_code):
            new_line = (','.join([parsed_line[1], parsed_line[3], parsed_line[4]]) + '\n').replace('"', '')
            airports_with_iata.append(new_line)
    with open('airports_filtered.txt', 'w', encoding='utf8') as ff:
        ff.write(''.join(airports_with_iata))
