"""
:brief: Tokenization of title and body string for each post.
"""
import datetime
import json
import sys
from tqdm import tqdm

from preprocessing import Preprocess

class Vectorize:
    def __init__(self, vec_path="", question_path=""):
        self.vec_path = vec_path
        self.question_path = question_path
        self.processor = Preprocess()

    def vectorize(self):
        for i in tqdm(range(50)):
            print(f"File Number {i}")
            with open(f"{self.question_path}/{i}.json", "r") as f:
                candidate_questions = json.load(f)
                [
                        candidate_questions[index].update(
                            {
                                "title_vec": self.processor.parse_string(question['cleaned_title']),
                                "body_vec": self.processor.parse_string(question['cleaned_body'])
                            }
                        )
                        for index, question in candidate_questions.items()
                ]

                with open(f"{self.vec_path}/{i}.json", 'w') as f1:
                    json.dump(candidate_questions, f1)


if __name__ == "__main__":
    begin = datetime.datetime.now()

    vectorizer = Vectorize(vec_path=sys.argv[1], question_path=sys.argv[2])
    vectorizer.vectorize()

    print(datetime.datetime.now() - begin)