import datetime
import heapq
import json
import os
import math
import sys

from preprocessing import Preprocess


class Composer:
    def __init__(self, duplicate_path="", question_path=""):
        self.duplicate_path = duplicate_path
        self.question_path = question_path
        self.processer = Preprocess()
        self.iterations = 10
        self.duplicate_map = {}
        self.N = 300
        self.K = 20

    def duplicate_similarity(self):
        with open(self.duplicate_path, "w") as f:
            duplicates = json.load(f)

        duplicate_keys = duplicates.keys()[: self.N]
        self.duplicate_map = {
            qid: {"actual_questions": duplicates[qid]["dups"], "scores": []}
            for qid in duplicate_keys
        }

        for file in os.listdir(self.question_path):
            if "json" not in file:
                continue
            with open(f"{self.question_path}/{file}", "r") as f:
                questions = json.load(f)
                for qid, question in questions.items():
                    ids_to_remove = []
                    for dup_qid in duplicate_keys:
                        if qid == dup_qid:
                            continue
                        if (
                            question["creation_date"]
                            >= duplicates[dup_qid]["creation_date"]
                        ):
                            ids_to_remove.append(dup_qid)
                            continue
                        sim_scores = self.processer.calculate_similarity(
                            duplicates[dup_qid], question
                        )
                        self.duplicate_map[dup_qid]["scores"].push(
                            {
                                "qid": qid,
                                "title_score": sim_scores["title"],
                                "body_score": sim_scores["body"],
                                "tag_score": sim_scores["tag"],
                                "topic_score": sim_scores["topics"],
                            }
                        )

                        if len(self.duplicate_map[dup_qid]["scores"]) >= self.K:
                            self.duplicate_map[dup_qid]["scores"].pop()

                    duplicate_keys = [
                        x for x in duplicate_keys if (x not in ids_to_remove)
                    ]

    def param_estimation(self):
        best_params = [], best_score = 0
        for _ in range(self.iterations):
            params = [0, 0, 0, 0]

            for i in range(4):
                params[i] = math.random()

            for i in range(4):
                best_params[i] = params[i]
                params[i] = 0

                for j in range(0, 1.01, 0.01):
                    duplicate_question_score = {
                        id: heapq([]) for id in self.duplicate_map.keys()
                    }
                    for dup_id in self.duplicate_map.keys():
                        for score_obj in self.duplicate_map[dup_id]["scores"]:
                            composer_score = (
                                score_obj["title_score"] * params[0]
                                + score_obj["body_score"] * params[1]
                                + score_obj["topic_score"] * params[2]
                                + score_obj["tag_score"] * params[3]
                            )
                            duplicate_question_score[dup_id].push(
                                (composer_score, score_obj["qid"])
                            )
                    score = self.evalution_criteria(duplicate_question_score)
                    if score > best_score:
                        best_params[i] = j
                        best_score = score

                params[i] = best_params[i]

        return best_params

    def evalution_criteria(self):
        pass


if __name__ == "__main__":
    begin = datetime.datetime.now()
    composer = Composer(duplicate_path=sys.argv[1], question_path=sys.argv[2])
    composer.duplicate_similarity()
    composer.param_estimation()

    print(datetime.datetime.now() - begin)
