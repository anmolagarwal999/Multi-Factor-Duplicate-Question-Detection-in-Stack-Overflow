import datetime
import heapq
import json
import os
import math
import sys
import random

from preprocessing import Preprocess

# 60 files, each file has 5000 posts = 3 lakh posts
# sorted


class Composer:
    def __init__(self, duplicate_path="", question_path=""):
        self.duplicate_path = duplicate_path
        self.question_path = question_path
        self.processer = Preprocess()
        self.iterations = 10
        self.dup_score_details = {}
        self.N = 2 # number of dups to be considered
        self.K = 10 # recall

    def duplicate_similarity(self):

        # load all paths
        print("Opening and loading all duplicates")
        with open(self.duplicate_path, "r") as f:
            list_of_dups = json.load(f)

        print(f"Dups loaded : found {len(list_of_dups)}")
        # return 

        # change this to adjust for ordered dict
        activate_dup_keys = list(list_of_dups.keys())[: self.N]

        # store a dictionary with 3 things
        self.dup_score_details = {
            qid: {"expected_questions": list_of_dups[qid]["dups_list"], "scores": []}
            for qid in activate_dup_keys
        }

        for curr_dup_id in activate_dup_keys:
            print("Id of dup question being ivestigated is ", curr_dup_id)
            print("legnth ", len(list_of_dups[curr_dup_id]['dups_list']))

            if list_of_dups[curr_dup_id]['topic']==None:
                continue
            # print(f"This q has {len(list_of_dups[curr_dup_id]["dups_list"])}")

            sort_id_of_dup=list_of_dups[curr_dup_id]['sort_id']

            print("dup sorted id is ", sort_id_of_dup)
            for file in os.listdir(self.question_path):
                if "json" not in file:
                    continue

                
                print("curr file to be used is ", file)
                with open(f"{self.question_path}/{file}", "r") as f:

                    candidate_questions = json.load(f)
                    print("Loaded a dict with num candidates as ", len(candidate_questions))
                            
                    for can_qid in candidate_questions:

                        candidate_sorted_id=candidate_questions[can_qid]['sort_id']
                        if candidate_questions[can_qid]['topic']==None:
                            continue

                        if candidate_sorted_id>sort_id_of_dup:
                            break
                        sim_scores = self.processer.calculate_similarity(
                            list_of_dups[curr_dup_id], candidate_questions[can_qid]
                        )

                        print("SIm scores found to be ", sim_scores)
                        self.dup_score_details[curr_dup_id]["scores"].append(
                            {
                                "candidate_qid": can_qid,
                                "title_score": sim_scores["title"],
                                "body_score": sim_scores["body"],
                                "tag_score": sim_scores["tags"],
                                "topic_score": sim_scores["topics"],
                            }
                        )
                        # return
                        if len(self.dup_score_details[curr_dup_id]["scores"])==3:
                            break
            

    def cal_param_scores_for_a_question(self,params, scores_dict):
        # dup_id=id_of_dup_q
        # for this duplicate, calculate 

        init_heap=[]


        for score_obj in scores_dict:
            composer_score = (
                score_obj["title_score"] * params[0]
                + score_obj["body_score"] * params[1]
                + score_obj["topic_score"] * params[2]
                + score_obj["tag_score"] * params[3]
            )
            heapq.heappush(
                init_heap,
                (composer_score, score_obj["candidate_qid"]),
            )

            if len(init_heap) >= self.K:
                heapq.heappop(init_heap)

        # return list of pairs (score, qid)
        return init_heap


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
                params[i] = random.random()

            # init let best_params let [a,b,c,d]
            # let it be [0.01, 0.02, 0.03, 0.04]
            # best_params = 0

            for i in range(4):

                # best_params = [alpha,0,0,0]
                best_params[i] = params[i]
                params[i] = 0
                j=0
                while(j<1.01):
                    params[i]=j
                    q_heaps = {
                        id: heapq.heapify([]) for id in self.dup_score_details.keys()
                    }

                    # iterate through each duplicate question
                    for dup_q_id in self.dup_score_details.keys():
                        q_heaps[dup_q_id]=self.cal_param_scores_for_a_question(params, self.dup_score_details[dup_q_id]["scores"])

                    score = self.evalution_criteria(q_heaps)
                    if score > best_score:
                        best_params[i] = j
                        best_score = score
                    j+=0.05

                params[i] = best_params[i]

        return best_params

    def evalution_criteria(self, q_heaps):

        # I curently have a heap with qid as key and list of pairs of (score, best candid)
        # exp found in dup_score_details[qid][expected_questions]
        wanted_q_ids=list(q_heaps.keys())
        success_num=0
        success_denom=len(wanted_q_ids)
        for curr_q_id, curr_heap in q_heaps.items():
            predicted_best=set([x[1] for x in curr_heap])
            actual_best=self.dup_score_details[curr_q_id]['expected_questions']
            for exp_candidate in actual_best:
                if exp_candidate in predicted_best:
                    success_num+=1
                    break
        params_score=success_num/success_denom
        return params_score
        
        


if __name__ == "__main__":

    begin = datetime.datetime.now()

    # sorted = 3000 posts
    # duplicate path = 300 elements
    # question_path = folder path where 60 files are stored
    composer = Composer(duplicate_path=sys.argv[1], question_path=sys.argv[2])
    composer.duplicate_similarity()

    
    composer.param_estimation()

    print(datetime.datetime.now() - begin)
