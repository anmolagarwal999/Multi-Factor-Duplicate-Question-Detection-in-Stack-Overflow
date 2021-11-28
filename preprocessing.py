from collections import Counter
import json
import re

from nltk.stem import PorterStemmer, WordNetLemmatizer
from scipy import spatial

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
        # print(text)
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

        similarities = {"title": 0, "body": 0, "tags": 0, "topics": 0}
        keys = ["title_vec", "body_vec", "tags_list", "topic"]
        # print("dict received is ", question_1)
        for key in keys:
            if key == "title_vec":
                similarities["title"] = self.merge_bog(
                    question_1[key], question_2[key]
                )
            elif key == "body_vec":
                similarities["body"] = self.merge_bog(
                    question_1[key], question_2[key]
                )
            elif key == "tags_list":
                similarities["tags"] = self.merge_bog(question_1[key], question_2[key])
            elif key == "topic":
                # print("COol stuff")
                # print(question_1[key])
                # print(question_1[key])
                similarities["topics"] = self.cosine_similarity(
                    question_1[key], question_2[key]
                )

        return similarities

    def cosine_similarity(self, vec_n, vec_m):
        """Find cosine similarity b/w the 2 vectors"""

        return 1 - spatial.distance.cosine(vec_n, vec_m)

    def merge_bog(self, bog_m, bog_n):
        """bag of words creation of 2 list of strings"""

        bog_u = list(set(bog_m) | set(bog_n))
        counts_m = Counter()
        counts_n = Counter()
        counts_m.update(word for word in bog_m)
        counts_n.update(word for word in bog_n)
        sum_m = len(bog_m)
        sum_n = len(bog_n)
        vec_m = []
        vec_n = []
        for word in bog_u:
            try:
                vec_m.append(counts_m[word] / sum_m)
            except:
                vec_m.append(0)
            try:
                vec_n.append(counts_n[word] / sum_n)
            except:
                vec_n.append(0)

        cosine = self.cosine_similarity(vec_n, vec_m)
        return cosine
