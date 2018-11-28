from typing import List

from mrjob.job import MRJob
from mrjob.step import MRStep


class MRKmeansStep(MRJob):
    prototypes = {}

    def cosine_sim(self, prot: List[(str, float)], doc: List[str]):
        """
        Compute here the Cosine similarity between a prototype and a document
        :param prot: List of pairs (word, probability)
        :param doc: List of words (sorted alphabeticaly)
        :return: Similarity value in the range [0, 1]
        """
        pass

    def jaccard(self, prot: List[(str, float)], doc: List[str]):
        """
        Compute here the Jaccard similarity between a prototype and a document
        :param prot: List of pairs (word, probability)
        :param doc: List of words (sorted alphabeticaly)
        :return: Similarity value in the range [0, 1]
        """
        pass

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

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

    def assign_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document

        Words should be sorted alphabetically in the prototypes and the documents

        This function has to return at list of pairs (prototype_id, document words)

        You can add also more elements to the value element, for example the document_id
        """

        # Each line is a string docid:wor1 word2 ... wordn
        doc, words = line.split(':')
        lwords = words.split()

        #
        # Compute map here
        #

        # Return pair key, value
        yield None, None

    def aggregate_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word

        :param key:
        :param values:
        :return:
        """

        yield None, None

    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)
                ]


if __name__ == '__main__':
    MRKmeansStep.run()
