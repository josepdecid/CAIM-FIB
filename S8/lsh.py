import argparse
import time

import numpy as np

SEED = 1234
FIRST_TEST_IMAGE_INDEX = 1500


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(f'{method.__name__} {kw} {te - ts} sec')
        return result

    return timed


class LSH(object):
    """
    Implementation of LSH for digits database in file 'images.npy'
    """

    def __init__(self, k, m):
        """
        Initialize a LSH instance with k # of bits and m # of repeats
        :param k: #bits
        :param m: #repeats
        """
        self.k = k
        self.m = m

        # data is numpy nD-array with images
        self.data = np.load('images.npy')

        # Length of bit representation of images such that length of each image is pixels * max_value
        self.pixels = 64
        self.max_value = 16
        self.len_image = self.pixels * self.max_value

        # k random hash functions for each repeat
        np.random.seed(SEED)
        self.hash_bits = np.random.randint(self.len_image, size=(m, k))

        # Stores the hashed images in a list of m dictionaries
        self.hashes = [dict() for _ in range(self.m)]
        self.hash_all_images()

    def hash_all_images(self):
        """
        Iterates over all non-test images and store them in hash tables(s)
        """
        for idx, img in enumerate(self.data[:FIRST_TEST_IMAGE_INDEX]):
            for i in range(self.m):
                code = self.hash_code(img, i)
                if code not in self.hashes[i]:
                    self.hashes[i][code] = []
                self.hashes[i][code].append(idx)

    def hash_code(self, img: np.ndarray, i: int) -> str:
        """
        Gets the i-th hash code for the given image
        :param img: image to get the i-th hash code from
        :param i: # hash code (0 <= i < m)
        :return:
        """
        """ get the i'th hash code of image im (0 <= i < m)"""
        pixels = img.flatten()
        row = self.hash_bits[i]
        code = ""
        for x in row:
            pix = int(x) // int(self.max_value)
            num = x % self.max_value
            code += ('1' if num <= pixels[pix] else '0')
        return code

    def candidates(self, img):
        """
        Finds matching candidates for the given image
        :param img: image to look for matching candidates
        :return: set of matching images ids
        """
        """ given image im, return matching candidates (well, the indices) """
        res = set()
        for i in range(self.m):
            code = self.hash_code(img, i)
            if code in self.hashes[i]:
                res.update(self.hashes[i][code])
        return res


@timeit
def main(k, m):
    print(f'Running lsh.py with parameters k = {k} and m = {m}')

    lsh = LSH(k, m)

    for i in range(FIRST_TEST_IMAGE_INDEX, FIRST_TEST_IMAGE_INDEX + 10):
        image = lsh.data[i]
        candidates = lsh.candidates(image)
        print(f'There are {len(candidates)} candidates for image {i}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', default=20, type=int)
    parser.add_argument('-m', default=5, type=int)
    arguments = parser.parse_args()

    main(k=arguments.k, m=arguments.m)
