import time
from os import system

if __name__ == '__main__':
    start_time = time.time()

    map_threads = '--jobconf mapreduce.job.maps=4'
    red_threads = '--jobconf mapreduces.job.reduces=4'

    system('python S6/SteamDocs.py --index news | python S6/MRWordCount.py -r local {} {}'
           .format(map_threads, red_threads))

    print('Total time: {}'.format(time.time() - start_time))
