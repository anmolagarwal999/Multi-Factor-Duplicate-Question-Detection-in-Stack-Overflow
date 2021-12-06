"""
:brief: To create jaccard similarity score for each candidate question per duplicate question
"""
import datetime
import heapq
import json
import os
import sys
from random import random
from tqdm import tqdm

from preprocessing import Preprocess


class Jaccard:
    def __init__(self, duplicate_details_train_path="", duplicate_details_test_path="", question_path="", dup_question_path=""):
        self.duplicate_details_train_path = duplicate_details_train_path
        self.duplicate_details_test_path = duplicate_details_test_path
        self.question_path = question_path
        self.processor = Preprocess()
        self.dup_question_path = dup_question_path
        self.dup_score_details_train = {}
        self.dup_score_details_test = {}
        self.duplicates = {}

    def update_jaccard(self):
        
        with open(self.duplicate_details_train_path, "r") as f:
            self.dup_score_details_train = json.load(f)

        print("Train loaded")
        
        with open(self.duplicate_details_test_path, "r") as f:
            self.dup_score_details_test = json.load(f)

        print("Test loaded")

        with open(self.dup_question_path, "r") as f:
            self.duplicates = json.load(f)
        
        print("Duplicates loaded")

        for i in tqdm(range(50)):
            with open(f"{self.question_path}/{i}.json", "r") as f:
                candidate_questions = json.load(f)
                
                if i < 40:
                    [
                        [
                            self.dup_score_details_train[qid]["scores"][index].update({'jaccard_sim': self.processor.jaccard_similarity(candidate_questions[str(cand["candidate_qid"])], self.duplicates[qid])}) 
                            for index, cand in enumerate(dup["scores"]) if str(cand["candidate_qid"]) in candidate_questions.keys()
                        ]
                        for qid, dup in self.dup_score_details_train.items()
                    ]

                [
                    [
                        self.dup_score_details_test[qid]["scores"][index].update({'jaccard_sim': self.processor.jaccard_similarity(candidate_questions[str(cand["candidate_qid"])], self.duplicates[qid])}) 
                        for index, cand in enumerate(dup["scores"]) if str(cand["candidate_qid"]) in candidate_questions.keys()
                    ]
                    for qid, dup in self.dup_score_details_test.items()
                ]
        
        print("Compute done")

        with open('jac_dup_score_details_300.json', 'w') as f:
            json.dump(self.dup_score_details_train, f)
        
        print("Train written")
        
        with open('jac_dup_score_details_100_test.json', 'w') as f:
            json.dump(self.dup_score_details_test, f)
        
        print("Test written")
                
                


if __name__ == "__main__":
    begin = datetime.datetime.now()
    jaccard = Jaccard(duplicate_details_train_path=sys.argv[1], duplicate_details_test_path=sys.argv[2], question_path=sys.argv[3], dup_question_path=sys.argv[4])
    jaccard.update_jaccard()

    print(datetime.datetime.now() - begin)