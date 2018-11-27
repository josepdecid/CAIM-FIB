import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--prot', default='prototypes-final.txt', help='prototype file')
    parser.add_argument('--natt', default=5, type=int,
                        help='Number of attributes to show')
    args = parser.parse_args()

    f = open(args.prot, 'r')

    for line in f:
        cl, attr = line.split(':')
        print(cl)
        latt = sorted([(float(at.split('+')[1]), at.split('+')[0])
                       for at in attr.split()], reverse=True)
        print(latt[:args.natt])
