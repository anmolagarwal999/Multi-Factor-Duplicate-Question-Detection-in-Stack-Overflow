import json
from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import Counter
from scipy import spatial
import re

from stopwords import STOPWORDS


class Preprocess:
    def __init__(self, input_path, remove_small_word=False, do_lemmatization=False, ) -> None:
        self.ps = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.DATADIR = input_path
        with open(f'{self.DATADIR}/0.json', 'r') as f:
            self.questions = json.load(f)
        self.cleaned_question = {}
        self.punc_string = "!|\(|\)|-|\[|\]|\{|\}|;|:|'|\"|\|,|<|>|/|\?|@|=|\$|%|^|&|\*|\+|_|~"
        self.punc_regex = re.compile(self.punc_string)
        self.do_lemmatization = do_lemmatization
        self.remove_small_word = remove_small_word

    def remove_stopwords(self, text):
        """remove stopwords and words have less than 3 lengths"""

        reduced_words = [word for word in text if word not in STOPWORDS]
        if self.remove_small_word:
            reduced_words = [word for word in reduced_words if len(word) > 3]
        return reduced_words

    def stemming(self, text: list) -> list:
        stemmed_words = [self.ps.stem(word) for word in text]
        return stemmed_words

    def lemmatizing(self, text: list, pos: str = 'n') -> list:
        lemmatized_words = [self.lemmatizer.lemmatize(word, pos=pos) for word in text]  # pos='v' mean verb
        return lemmatized_words

    def parse_string(self, text):
        """text cleaning and preprocessing"""
        text = text.lower()
        # tokenized_text = word_tokenize(text)
        text = self.punc_regex.sub(' ', text)
        tokenized_text = text.split()
        if self.do_lemmatization:
            tokenized_text = self.lemmatizing(tokenized_text, pos='v')
        # else:
        tokenized_text = self.stemming(tokenized_text)
        tokenized_text = self.remove_stopwords(tokenized_text)
        return tokenized_text

    def cosine_similarity(self, vec_n, vec_m):
        return 1 - spatial.distance.cosine(vec_n, vec_m)

    def merge_bog(self, bog_m, bog_n):
        bog_u = list(set(bog_m) | set(bog_n))
        counts_m = Counter()
        counts_n = Counter()
        counts_m.update(word for word in bog_m)
        counts_n.update(word for word in bog_n)
        # sum_m = sum(counts_m.values)
        sum_m = len(bog_m)
        # sum_n = sum(counts_n.values)
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

    def parse(self):
        self.cleaned_questions = {
            key: {k: self.parse_string(v) if k in ['body', 'title'] else v for k, v in _value.items()} for key, _value
            in self.questions.items()}


if __name__ == "__main__":
    processing = Preprocess(input_path='processed/output')
    # print(processing.parse_string("I'm new to C# and I want to use a track-bar to change a form's opacity. This is my code: decimal trans = trackBar Value / 5000; this.Opacity = trans; When I try to build it, I get this error: ' Cannot implicitly convert type 'decimal' to 'double' I tried making trans a double, but then the control doesn't work. This code worked fine for me in VB.NET. What do I need to do differently? you?"))
    # processing.parse()
