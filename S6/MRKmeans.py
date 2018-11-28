import argparse
import os
import shutil
from time import time

from mrjob.util import to_lines

from MRKmeansStep import MRKmeansStep


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes.txt', help='Initial prototypes file')
    parser.add_argument('--docs', default='documents.txt', help='Documents data')
    parser.add_argument('--iter', default=5, type=int, help='Number of iterations')
    parser.add_argument('--nmaps', default=2, type=int, help='Number of parallel map processes to use')
    parser.add_argument('--nreduces', default=2, type=int, help='Number of parallel reduce processes to use')
    return parser.parse_args()


def copy_prototypes(prototypes):
    cwd = os.getcwd()
    shutil.copy(f'{cwd}/{prototypes}', f'{cwd}/prototypes0.txt')


def run_runner(mr_job):
    with mr_job.make_runner() as runner:
        runner.run()
        new_assign = {}
        new_proto = {}
        # Process the results of the script, each line one results
        for line in to_lines(runner.cat_output()):
            key, value = mr_job.parse_output_line(line)
            # You should store things here probably in a data structure

        # If your scripts returns the new assignments you could write them in a file here

        # You should store the new prototypes here for the next iteration

        # If you have saved the assignments, you can check if they have changed from the previous iteration


def perform_iterations(iterations, docs, nmaps, nreduces):
    cwd = os.getcwd()
    no_move = False  # Stores if there has been changes in the current iteration
    start_time = time()

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
        run_runner(mr_job)
        print(f'Time = {time() - start_time} seconds')

        # If there are no changes in two consecutive iteration we can stop
        if no_move:
            print('Algorithm converged')
            break

    return i


def print_results(iteration):
    cwd = os.getcwd()
    with open(f'{cwd}/prototypes{iteration}.txt', mode='r') as f:
        for l in f.readlines():
            print(l)


def main():
    args = parse_args()
    copy_prototypes(args.prot)
    num_its = perform_iterations(args.iter, args.docs, args.nmaps, args.nreduces)
    print_results(num_its)


if __name__ == '__main__':
    main()
