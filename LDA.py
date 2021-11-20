#!/usr/bin/python
import datetime
import json
import os
import sys

from gensim.corpora import Dictionary
from gensim.models import LdaMulticore
from gensim.test.utils import datapath

import numpy as np

from preprocessing import Preprocess

np.random.seed(2018)


class LDA:
    def __init__(self, data_path="", preprocessing_path="", storage_path=""):
        self.data_path = data_path
        self.storage_path = storage_path
        self.preprocessing_path = preprocessing_path
        self.processing = Preprocess(input_path=self.data_path, remove_small_word=True, do_lemmatization=True)
        self.K = 100
        self.dictionary = None
        self.lda_model = None
        self.dict_filename = "lda_dictionary"
        self.lda_file = datapath("lda_model")

    def dict_creation(self):
        """preprocess text and create dictionary"""

        for file in os.listdir(self.data_path):
            with open(f'{self.data_path}/{file}', 'r') as f:
                questions = json.load(f)
                _processed_docs = [self.processing.parse_string(" ".join([question["body"], question["title"]])) for
                                   question in questions]
                with open(f"{self.preprocessing_path}/{file}", 'w') as fd:
                    json.dump(_processed_docs, fd)

                if self.dictionary is None:
                    self.dictionary = Dictionary(_processed_docs)
                else:
                    self.dictionary.add_documents(_processed_docs)

        self.dictionary.filter_extremes(no_below=15, no_above=0.5)
        self.dictionary.save_as_text(self.dict_filename)

    def lda_creation(self):
        """create lda model"""

        if self.dictionary is None:
            self.dictionary = Dictionary.load_from_text(self.dict_filename)

        for file in os.listdir(self.preprocessing_path):
            with open(f'{self.preprocessing_path}/{file}', 'r') as f:
                processed_docs = json.load(f)
                bow_corpus = [self.dictionary.doc2bow(doc) for doc in processed_docs]
                if self.lda_model is None:
                    self.lda_model = LdaMulticore(bow_corpus, num_topics=self.K, id2word=self.dictionary, passes=2,
                                                  workers=2)
                else:
                    self.lda_model.update(bow_corpus)

        self.lda_model.save(self.lda_file)

    def get_topics(self):
        """Final Topics for each post"""

        if self.lda_model is None:
            self.lda_model = LdaMulticore.load(self.lda_file)

        for file in os.listdir(self.data_path):
            with open(f'{self.data_path}/{file}', 'r') as f:
                questions = json.load(f)
                with open(f'{self.preprocessing_path}/{file}', 'r') as fp:
                    processed_docs = json.load(fp)
                    questions = [
                        question.update({"topic": self.lda_model[self.dictionary.doc2bow(processed_docs[index])]})
                        for index, question in enumerate(questions)]
                    with open(f'{self.storage_path}/{file}', 'w') as fd:
                        json.dump(questions, fd)


# def cosine_similarity(self, q_index_1: int, q_index_2: int) -> float:
#     """q_index are the indexes of the questions in the bag pf words corpus"""
#     similarity = self.processing.cosine_similarity(self.lda_model[self.bow_corpus[q_index_1]],
#                                                    self.lda_model[self.bow_corpus[q_index_2]])
#     return similarity


if __name__ == "__main__":
    begin = datetime.datetime.now()
    LDA = LDA(data_path=sys.argv[1], preprocessing_path=sys.argv[2], storage_path=sys.argv[3])
    LDA.dict_creation()
    LDA.lda_creation()
    LDA.get_topics()
    print(datetime.datetime.now() - begin)
