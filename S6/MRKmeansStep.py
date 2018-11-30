from typing import List, Tuple

import sys
from math import sqrt
from mrjob.job import MRJob
from mrjob.step import MRStep


class MRKmeansStep(MRJob):
    prototypes = {}

    @staticmethod
    def intersection(prot: List[Tuple[str, float]], doc: List[str]) -> float:
        intersection = 0
        i = 0
        j = 0
        while i < len(prot) and j < len(doc):
            if prot[i][0] < doc[j]:
                i += 1
            elif prot[i][0] > doc[j]:
                j += 1
            else:
                intersection += prot[i][1]
                i += 1
                j += 1
        return intersection

    @staticmethod
    def jaccard(prot: List[Tuple[str, float]], doc: List[str]) -> float:
        """
        Compute here the Jaccard similarity between a prototype and a document
        :param prot: List of pairs (word, probability)
        :param doc: List of words (sorted alphabeticaly)
        :return: Similarity value in the range [0, 1]
        """
        intersection = MRKmeansStep.intersection(prot, doc)
        union = sum([p*p for (_, p) in prot]) + len(doc) - intersection
        return intersection/union

    @staticmethod
    def cosine_similarity(prot: List[Tuple[str, float]], doc: List[str]) -> float:
        intersection = MRKmeansStep.intersection(prot, doc)
        divisor = sqrt(sum([p*p for (_, p) in prot]))*sqrt(len(doc))
        return intersection/divisor

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

    # Implementation #

    def load_data(self):
        """
        Loads the current cluster prototypes into a dictionary
        """
        f = open(self.options.prot, 'r')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

    def map_closest_prototype(self, _, line: str):
        """
        MAPPER
        It computes the closest prototype to a document.
        Words should be sorted alphabetically in the prototypes and the documents.
        :param _
        :param line: String "docId: [word_1 .. word_n]
        :return List of pairs (prototype_id, (document_id, document_words))
        """
        doc_id, words = line.split(': ')
        d_words = words.split()

        closest_prototype_id = None
        closest_distance = sys.float_info.max
        for cluster, c_words in self.prototypes.items():
            distance = MRKmeansStep.jaccard(c_words, d_words)
            if distance < closest_distance:
                closest_distance = distance
                closest_prototype_id = cluster

        # Return pair key, value
        yield closest_prototype_id, (doc_id, d_words)

    @staticmethod
    def reduce_closest_prototype(key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word
        """
        new_prototype = {}
        new_prototype_docs = []
        for document in values:
            new_prototype_docs.append(document[0])
            for word in document[1]:
                new_prototype[word] = 1 if word not in new_prototype else new_prototype[word] + 1

        new_prototype = [(word, new_prototype[word] /
                          len(new_prototype_docs)) for word in new_prototype]
        sorted(new_prototype_docs)
        sorted(new_prototype, key=lambda e: e[0])

        yield key, (new_prototype_docs, new_prototype)

    def steps(self):
        return [
            MRStep(mapper_init=self.load_data,
                   mapper=self.map_closest_prototype,
                   reducer=self.reduce_closest_prototype)
        ]


if __name__ == '__main__':
    MRKmeansStep.run()
