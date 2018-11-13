import re

with open('routes.txt', 'r', encoding='utf8') as f:
    filtered_routes = []
    for line in f.readlines():
        parsed_line = line.split(',')
        new_line = (','.join([parsed_line[2], parsed_line[4]]) + '\n')
        filtered_routes.append(new_line)
    with open('routes_filtered.txt', 'w', encoding='utf8') as ff:
        ff.write(''.join(filtered_routes))
