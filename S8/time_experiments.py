import time
import matplotlib.pyplot as plt

from lsh import LSH

FIRST_TEST_IMAGE_INDEX = 1500


def test_lsh_parameters(_k, _m):
    ts = time.time()

    lsh = LSH(_k, _m)
    candidates_mean_size = 0
    test_images = range(FIRST_TEST_IMAGE_INDEX, FIRST_TEST_IMAGE_INDEX + 10)
    for i in test_images:
        image = lsh.data[i]
        candidates = lsh.candidates(image)
        candidates_mean_size += len(candidates)
    candidates_mean_size /= len(test_images)

    te = time.time()
    tt = te - ts

    print(f'k: {_k}, m: {_m}, candidatesSize: {candidates_mean_size}, time: {tt}')
    return candidates_mean_size, tt


if __name__ == '__main__':
    ks = list(range(10, 101, 1))
    ms = list(range(5, 10, 5))

    k_times = []
    k_csize = []
    for k in ks:
        s, t = test_lsh_parameters(k, ms[0])
        k_csize.append(s)
        k_times.append(t)

    m_times = []
    m_csize = []
    for m in ms:
        s, t = test_lsh_parameters(ks[0], m)
        m_csize.append(s)
        m_times.append(t)

    plt.plot(ks, k_times)
    plt.title('Execution time evolution for k')
    plt.xlabel('k')
    plt.ylabel('Execution time (s)')
    plt.savefig('images/k_time.png')
    plt.show()

    plt.plot(ks, k_csize, color='orange')
    plt.title('Candidate set size evolution for k')
    plt.xlabel('k')
    plt.ylabel('Mean candidates set size')
    plt.savefig('images/k_candidates.png')
    plt.show()

    plt.plot(ms, m_times)
    plt.title('Execution time evolution for m')
    plt.xlabel('m')
    plt.ylabel('Execution time (s)')
    plt.savefig('images/m_time.png')
    plt.show()

    plt.plot(ms, m_csize, color='orange')
    plt.title('Candidate set size evolution for m')
    plt.xlabel('m')
    plt.ylabel('Mean candidates set size')
    plt.savefig('images/m_candidates.png')
    plt.show()
