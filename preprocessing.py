"""
:brief: Util function to do all the pre-processing / compute similarity tasks
"""
from collections import Counter
import json
import re

from nltk.stem import PorterStemmer, WordNetLemmatizer
import numpy as np

from stopwords import STOPWORDS


class Preprocess:
    def __init__(
        self,
        remove_small_word=False,
        do_lemmatization=False,
    ) -> None:
        self.ps = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.cleaned_question = {}
        self.punc_string = (
            r"!|\(|\)|-|\[|\]|\{|\}|;|:|'|\"|<|>|\/|\?|@|=|\$|%|\^|&|\*|\+|_|~|\.|\,|\\"
        )
        self.space_string = r"/\s\s+/g"
        self.punc_regex = re.compile(self.punc_string)
        self.space_regex = re.compile(self.space_string)
        self.do_lemmatization = do_lemmatization
        self.remove_small_word = remove_small_word

    def remove_stopwords(self, text: list) -> list:
        """remove stopwords and words have less than 3 lengths"""

        reduced_words = [word for word in text if word not in STOPWORDS]
        if self.remove_small_word:
            reduced_words = [word for word in reduced_words if len(word) > 3]
        return reduced_words

    def stemming(self, text: list) -> list:
        """stemming"""

        stemmed_words = [self.ps.stem(word) for word in text]
        return stemmed_words

    def lemmatizing(self, text: list, pos: str = "n") -> list:
        """Lemmatization"""

        lemmatized_words = [self.lemmatizer.lemmatize(word, pos=pos) for word in text]
        return lemmatized_words

    def parse_string(self, text: str) -> list:
        """text cleaning and preprocessing"""
        text = text.lower()
        text = self.punc_regex.sub(" ", text)
        text = self.space_regex.sub(" ", text).strip()
        tokenized_text = text.split()
        if self.do_lemmatization:
            tokenized_text = self.lemmatizing(tokenized_text, pos="v")
        else:
            tokenized_text = self.stemming(tokenized_text)
        tokenized_text = self.remove_stopwords(tokenized_text)
        return tokenized_text

    def calculate_similarity(self, question_1: dict, question_2: dict) -> dict:
        """Provide 2 questions and it will return the 4 cosine similarities b/w each components"""

        similarities = {"title": 0, "body": 0, "tags": 0, "topics": 0, "jaccard_sim": 0}
        keys = ["title_vec", "body_vec", "tags_list", "topic"]
        for key in keys:
            if key == "title_vec":
                similarities["title"] = self.merge_bog(question_1[key], question_2[key])
            elif key == "body_vec":
                similarities["body"] = self.merge_bog(question_1[key], question_2[key])
            elif key == "tags_list":
                similarities["tags"] = self.merge_bog(question_1[key], question_2[key])
            elif key == "topic":
                similarities["topics"] = self.cosine_similarity(
                    question_1[key], question_2[key]
                )

    def jaccard_similarity(self, question_1, question_2):
        question_1_set = set(question_1['title_vec'])
        question_1_set.update(question_1["body_vec"])
        question_1_set.update(question_1["tags_list"])

        question_2_set = set(question_2['title_vec'])
        question_2_set.update(question_2["body_vec"])
        question_2_set.update(question_2["tags_list"])

        return len(question_1_set.intersection(question_2_set)) / len(question_1_set.union(question_2_set))


    
    def cosine_similarity(self, vec_n, vec_m):
        """Find cosine similarity b/w the 2 vectors"""
        if len(vec_m) == 0 or len(vec_n) == 0:
            return 0
        vec_n = np.array(vec_n)
        vec_m = np.array(vec_m)
        dot = np.dot(vec_m, vec_n)
        norm_n = np.linalg.norm(vec_n)
        norm_m = np.linalg.norm(vec_m)
        if norm_m != 0 and norm_n != 0:
            return dot / (norm_m * norm_n)
        else:
            return 0

    def merge_bog(self, bog_m, bog_n):
        """bag of words creation of 2 list of strings"""

        bog_u = list(set(bog_m) | set(bog_n))
        counts_m = Counter(bog_m)
        counts_n = Counter(bog_n)
        sum_m = len(bog_m)
        sum_n = len(bog_n)
        vec_m = []
        vec_n = []
        for word in bog_u:
            if word in counts_m:
                vec_m.append(counts_m[word] / sum_m)
            else:
                vec_m.append(0)

            if word in counts_n:
                vec_n.append(counts_n[word] / sum_n)
            else:
                vec_n.append(0)

        cosine = self.cosine_similarity(vec_n, vec_m)
        return cosine
