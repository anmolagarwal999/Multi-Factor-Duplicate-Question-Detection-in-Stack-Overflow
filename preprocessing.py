import json
from pprint import pprint
from nltk.stem import PorterStemmer
from collections import Counter
from scipy import spatial
# from nltk.tokenize import word_tokenize
import re


from stopwords import STOPWORDS


class Preprocess():
    def __init__(self, output_path) -> None:    
        self.ps = PorterStemmer()
        self.DATADIR = output_path
        with open(f'{self.DATADIR}/0.json', 'r') as f:
            self.questions = json.load(f)
        pprint(len(self.questions))
        pprint(self.questions['4'])
        self.cleaned_question = {}
        self.punc_string = "!|\(|\)|-|\[|\]|\{|\}|;|:|'|\"|\|,|<|>|/|\?|@|=|\$|%|^|&|\*|\+|_|~"
        self.punc_regex = re.compile(self.punc_string)

    
    def remove_stopwords(self, text):
        reduced_words = [word for word in text if word not in STOPWORDS]
        return reduced_words

    def stemming(self, text: list) -> list:
        stemmed_words = [self.ps.stem(word) for word in text]
        return stemmed_words

    def parse_string(self, text):
        text = text.lower()
        # tokenized_text = word_tokenize(text)
        text = self.punc_regex.sub(' ', text)
        # text = re.sub(self.punc_string,'', text)
        tokenized_text = text.split()
        tokenized_text = self.stemming(tokenized_text)
        # tokenized_text = self.remove_stopwords(tokenized_text)
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
                vec_m.append(counts_m[word]/sum_m)
            except:
                vec_m.append(0)
            try:
                vec_n.append(counts_n[word]/sum_n)
            except:
                vec_n.append(0)
        cosine = self.cosine_similarity(vec_n, vec_m)
        return cosine
            

    def parse(self):
        self.cleaned_questions = {key: {k: self.parse_string(v) if k in ['body', 'title'] else v for k, v in _value.items()} for key, _value in self.questions.items()}
        

if __name__ == "__main__":
    processing = Preprocess(output_path = 'processed/output')
    # print(processing.parse_string("I'm new to C# and I want to use a track-bar to change a form's opacity. This is my code: decimal trans = trackBar Value / 5000; this.Opacity = trans; When I try to build it, I get this error: ' Cannot implicitly convert type 'decimal' to 'double' I tried making trans a double, but then the control doesn't work. This code worked fine for me in VB.NET. What do I need to do differently? you?"))
    # processing.parse()
    