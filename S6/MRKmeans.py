import argparse
import os
import shutil
from functools import reduce
from time import time

from mrjob.util import to_lines

from MRKmeansStep import MRKmeansStep

assignation = {}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes.txt', help='Initial prototypes file')
    parser.add_argument('--docs', default='documents.txt', help='Documents data')
    parser.add_argument('--iter', default=5, type=int, help='Number of iterations')
    parser.add_argument('--nmaps', default=2, type=int, help='Number of parallel map processes to use')
    parser.add_argument('--nreduces', default=2, type=int, help='Number of parallel reduce processes to use')
    return parser.parse_args()


def copy_prototypes(prototypes_file):
    cwd = os.getcwd()
    shutil.copy(f'{cwd}/{prototypes_file}', f'{cwd}/prototypes0.txt')


def run_runner(mr_job, i):
    with mr_job.make_runner() as runner:
        runner.run()
        new_assignation = {}
        new_prototype = {}
        for line in to_lines(runner.cat_output()):
            key, value = mr_job.parse_output(line)

            new_assignation[key] = value[0]
            new_prototype[key] = value[1]

        cwd = os.getcwd()
        with open(f'{cwd}/assignments{i + 1}.txt', mode='w') as new_assignation_file:
            for key, values in new_assignation.items():
                aux = reduce(lambda acc, x: f'{acc} {x}', values, f'{key}:')
                new_assignation_file.write(f'{aux}\n')

        global assignation
        if assignation == new_assignation:
            return i
        else:
            assignation = new_assignation

        with open(f'{cwd}/prototypes{i + 1}.txt', mode='w') as new_prototype_file:
            for key, values in new_prototype.items():
                aux = reduce(lambda acc, x: f' {aux} {x[0]}+{repr(x[1])}', values, f'{key}:')
                new_prototype_file.write(f'{aux}\n')


def perform_iterations(iterations, docs, nmaps, nreduces):
    start_time = time()
    cwd = os.getcwd()

    i = 0
    for i in range(iterations):
        print(f'Iteration #{i+1}')

        # The --file flag tells to MRjob to copy the file to HADOOP
        # The --prot flag tells to MRKmeansStep where to load the prototypes from
        mr_job = MRKmeansStep(args=['-r', 'local', docs,
                                    '--file', f'{cwd}/prototypes{i}.txt',
                                    '--prot', f'{cwd}/prototypes{i}.txt',
                                    '--jobconf', f'mapreduce.job.maps={nmaps}',
                                    '--jobconf', f'mapreduce.job.reduces={nreduces}'])
        stopping_iteration = run_runner(mr_job, i)
        print(f'Time = {time() - start_time} seconds')

        # If there are no changes in two consecutive iteration we can stop
        if stopping_iteration is not None:
            print('Algorithm converged')
            return stopping_iteration

    return i


def print_results(iteration):
    cwd = os.getcwd()
    with open(f'{cwd}/prototypes{iteration}.txt', mode='r') as f:
        for l in f.readlines():
            print(l)


def main(args):
    copy_prototypes(args.prot)
    num_its = perform_iterations(args.iter, args.docs, args.nmaps, args.nreduces)
    print_results(num_its)


if __name__ == '__main__':
    main(parse_args())
