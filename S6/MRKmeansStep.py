from typing import List, Tuple

import sys
from mrjob.job import MRJob
from mrjob.step import MRStep


class MRKmeansStep(MRJob):
    prototypes = {}
    distance_function = None

    @staticmethod
    def jaccard(prot: List[Tuple[str, float]], doc: List[str]):
        """
        Compute here the Jaccard similarity between a prototype and a document
        :param prot: List of pairs (word, probability)
        :param doc: List of words (sorted alphabeticaly)
        :return: Similarity value in the range [0, 1]
        """
        intersection = 0
        i = 0
        j = 0
        while i < len(prot) and j < len(doc):
            if prot[i][0] < doc[j]:
                i += 1
            elif prot[i][0] > doc[j]:
                j += 1
            else:
                intersection += 1
                i += 1
                j += 1

        union = len(prot) + len(doc)
        return intersection / (union - intersection)

    @staticmethod
    def cosine_sim(prot: List[Tuple[str, int]], doc: List[str]):
        """
        Compute here the Cosine similarity between a prototype and a document
        :param prot: List of pairs (word, probability ∈ {0, 1})
        :param doc: List of words (sorted alphabeticaly)
        :return: Similarity value in the range [0, 1]
        """
        return 1

    def configure_args(self, distance_function=jaccard):
        """
        Additional configuration flag to get the prototypes files
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')
        self.distance_function = distance_function

    # Implementation #

    def load_data(self):
        """
        Loads the current cluster prototypes:
        """
        f = open(self.options.prot, 'r')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

    def map_closest_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document
        Words should be sorted alphabetically in the prototypes and the documents
        This function has to return at list of pairs (prototype_id, document words)
        You can add also more elements to the value element, for example the document_id
        """
        doc_id, words = line.split(': ')  # docId: [word1..n]
        d_words = words.split()

        closest_prototype_id = None
        closest_distance = sys.float_info.max
        for cluster, c_words in self.prototypes.items():
            distance = self.distance_function(c_words, d_words)
            if distance < closest_distance:
                closest_distance = distance
                closest_prototype_id = cluster

        # Return pair key, value
        yield closest_prototype_id, (doc_id, d_words)

    def reduce_closest_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word
        """
        yield (0, 1)

    def steps(self):
        return [
            MRStep(mapper_init=self.load_data, mapper=self.map_closest_prototype, reducer=self.reduce_closest_prototype)
        ]


if __name__ == '__main__':
    MRKmeansStep.run()
