import datetime
import heapq
import json
import os
import math
import sys

from preprocessing import Preprocess

# 60 files, each file has 5000 posts = 3 lakh posts
# sorted


class Composer:
    def __init__(self, duplicate_path="", question_path=""):
        self.duplicate_path = duplicate_path
        self.question_path = question_path
        self.processer = Preprocess()
        self.iterations = 10
        self.duplicate_map = {}
        self.N = 2 # number of dups to be considered
        self.K = 20 # recall

    def duplicate_similarity(self):

        # load all paths
        print("Opening and loading all duplicates")
        with open(self.duplicate_path, "r") as f:
            list_of_dups = json.load(f)

        print(f"Dups loaded : found {len(list_of_dups)}")
        # return 

        # change this to adjust for ordered dict
        activate_dup_keys = list(list_of_dups.keys())[: self.N]
        self.duplicate_map = {
            qid: {"actual_questions": list_of_dups[qid]["dups_list"], "scores": []}
            for qid in activate_dup_keys
        }

        for file in os.listdir(self.question_path):
            if "json" not in file:
                continue
            print("curr file to be used is ", file)
            with open(f"{self.question_path}/{file}", "r") as f:

                # 0.json = 50 sorted elements
                # 0th duplicate = 25th 
                #1st dup = 38th position
                # candidate questions

                # load all 50
                questions = json.load(f)

                # load all candidates


                # iterate through all candidates


                
                for qid, question in questions.items():

                    # 
                    ids_to_remove = []

                    # run twice
                    # iterate through all list_of_dups
                    for dup_qid in activate_dup_keys:
                        if qid == dup_qid:
                            continue

                        # not a valid contender
                        if (
                            question["creation_date"]
                            >= list_of_dups[dup_qid]["creation_date"]
                        ):
                            ids_to_remove.append(dup_qid)
                            continue


                        sim_scores = self.processer.calculate_similarity(
                            list_of_dups[dup_qid], question
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

                        # if len(self.duplicate_map[dup_qid]["scores"]) >= self.K:
                        #     self.duplicate_map[dup_qid]["scores"].pop()

                    activate_dup_keys = [
                        x for x in activate_dup_keys if (x not in ids_to_remove)
                    ]

    def cal_param_scores_for_a_question(self, four_params, scores_dict):
        # dup_id=id_of_dup_q
        # for this duplicate, calculate 

        init_heap=heapq.heapify([])


        for score_obj in scores_dict:
            composer_score = (
                score_obj["title_score"] * params[0]
                + score_obj["body_score"] * params[1]
                + score_obj["topic_score"] * params[2]
                + score_obj["tag_score"] * params[3]
            )
            heapq.heappush(
                init_heap,
                (composer_score, score_obj["qid"]),
            )

            if len(duplicate_question_score[dup_id]) >= self.K:
                heapq.heappop(duplicate_question_score[dup_id])

            return heap_dict


    def param_estimation(self):

        # expected output = alpha, beta, gamma, delta
        # return a array with 4 tuple values

        best_params = [0, 0, 0, 0]
        best_score = 0

        # iterate for some iterations

        # scores already done

        #######################################
        for _ in range(self.iterations):

            # init as on line 13 of paper code
            params = [0, 0, 0, 0]

            # randomly init current params between 0 and 1
            for i in range(4):
                params[i] = math.random()

            # init let best_params let [a,b,c,d]
            # let it be [0.01, 0.02, 0.03, 0.04]
            # best_params = 0

            for i in range(4):

                # best_params = [alpha,0,0,0]
                best_params[i] = params[i]
                params[i] = 0

                for j in range(0, 1.01, 0.01):
                    params[i]=j
                    duplicate_question_score = {
                        id: heapq.heapify([]) for id in self.duplicate_map.keys()
                    }

                    # iterate through each duplicate question
                    for dup_id in self.duplicate_map.keys():

                        duplicate_question_score[dup_id]=cal_param_scores_for_a_question(params, self.duplicate_map[dup_id]["scores"])

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

    # sorted = 3000 posts
    # duplicate path = 300 elements
    # question_path = folder path where 60 files are stored
    composer = Composer(duplicate_path=sys.argv[1], question_path=sys.argv[2])
    composer.duplicate_similarity()

    
    composer.param_estimation()

    print(datetime.datetime.now() - begin)
