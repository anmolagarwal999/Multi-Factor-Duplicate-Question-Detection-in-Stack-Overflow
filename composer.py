"""
:brief: To find all the similarity scores for each candidate question per duplicate question
        To estimate the 4 parameters \alpha, \beta, \gamma and \delta
"""
import datetime
import heapq
import json
import sys
from random import random
from tqdm import tqdm

from preprocessing import Preprocess


class Composer:
    def __init__(self, duplicate_path="", question_path=""):
        self.duplicate_path = duplicate_path
        self.question_path = question_path
        self.processor = Preprocess()
        self.iterations = 10
        self.dup_score_details = {}
        self.N = 400  # number of dups to be considered
        self.K = 10  # recall

    def duplicate_similarity(self):

        # Load all paths
        print("Opening and loading all duplicates")
        with open(self.duplicate_path, "r") as f:
            list_of_dups = json.load(f)

        print(f"Dups loaded : found {len(list_of_dups)}")

        # Change this to adjust for ordered dict
        activate_dup_keys = list(list_of_dups.keys())[self.N - 100: self.N]

        # Store a dictionary with 3 things
        # NOTE: Making every qid to int from string
        self.dup_score_details = {
            qid: {"expected_questions": list(
                map(int, list_of_dups[qid]["parent_q_list"])), "scores": []}
            for qid in activate_dup_keys
        }

        # for file in os.listdir(self.question_path):
        #     if "json" not in file:
        #         continue

        # print("curr file to be used is ", file)
        for i in range(50):
            print(f"File Number {i}")
            with open(f"{self.question_path}/{i}.json", "r") as f:

                candidate_questions = json.load(f)
                # print("Loaded a question dict with num candidates:", len(candidate_questions))

                for curr_dup_id in activate_dup_keys:
                    # print("Id of dup question being investigated is ", curr_dup_id)
                    # print("Total dups in ground truth is ", len(list_of_dups[curr_dup_id]['parent_q_list']))

                    if list_of_dups[curr_dup_id]['topic'] is None:
                        continue

                    # sort_id_of_dup = list_of_dups[curr_dup_id]['sort_id']

                    # print("dup sorted id is ", sort_id_of_dup)

                    for _, cand in candidate_questions.items():

                        candidate_sorted_id = cand['sort_id']

                        if cand['topic'] is None or cand['Id'] == \
                                list_of_dups[curr_dup_id]['Id']:
                            continue

                        # if candidate_sorted_id > sort_id_of_dup:
                        #     break
                        if list_of_dups[curr_dup_id]['CreationDate'] < cand[
                            'CreationDate']:
                            break

                        sim_scores = self.processor.calculate_similarity(
                            list_of_dups[curr_dup_id], cand
                        )

                        # print("SIm scores found to be ", sim_scores)
                        self.dup_score_details[curr_dup_id]["scores"].append(
                            {
                                "candidate_qid": cand["Id"],
                                "title_score": sim_scores["title"],
                                "body_score": sim_scores["body"],
                                "tag_score": sim_scores["tags"],
                                "topic_score": sim_scores["topics"],
                            }
                        )

        with open('dup_score_details_100_test.json', 'w') as f:
            json.dump(self.dup_score_details, f)

    def cal_param_scores_for_a_question(self, params, scores_dict):
        # dup_id=id_of_dup_q
        # for this duplicate, calculate 

        init_heap = []

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
        """estimates all the parameters of the weighted sum of the components"""
        if len(self.dup_score_details) == 0:
            with open('dup_score_details.json', 'r') as f:
                self.dup_score_details = json.load(f)
        # expected output = alpha, beta, gamma, delta
        # return a array with 4 tuple values

        # best params and score from all restarts
        best_params = [0 for _ in range(4)]
        best_score = 0

        # heaps for each duplicate question which contain top K questions as predicted by algorithm
        q_heaps = {
            _id: heapq.heapify([]) for _id in self.dup_score_details.keys()
        }

        for _ in tqdm(range(self.iterations)):

            # random restart type approach, for each iteration choose a new set of starting params
            init_params = [random() for _ in range(4)]

            for dup_q_id in self.dup_score_details.keys():
                q_heaps[dup_q_id] = self.cal_param_scores_for_a_question(
                    init_params,
                    self.dup_score_details[dup_q_id][
                        "scores"])
            # score for initial set of params
            init_score = self.evaluation_criteria(q_heaps)

            # trial params are copy of initial set of params
            params = init_params.copy()

            # update and try values for each parameter iteratively
            for i in tqdm(range(4)):
                j = 0
                while j < 1.01:
                    # try each value from 0 to 1
                    params[i] = j

                    # iterate through each duplicate question
                    for dup_q_id in self.dup_score_details.keys():
                        # calculate scores using current set of trial params
                        q_heaps[
                            dup_q_id] = self.cal_param_scores_for_a_question(
                            params,
                            self.dup_score_details[dup_q_id][
                                "scores"])
                    score = self.evaluation_criteria(q_heaps)

                    # if score for these sets of parameters is better than best score for this iteration, then update
                    # best params of this iteration 
                    if score > init_score:
                        init_params[i] = j
                        init_score = score
                    j += 0.05

                # update trial params to best params of current restart before fine-tuning next parameter
                params[i] = init_params[i]

            # take best params of each iteration in random restart
            if init_score > best_score:
                best_params = init_params.copy()
                best_score = init_score
                print(f"Better score: {best_score}")

        # return best params from all restarts
        return best_params, best_score

    def evaluation_criteria(self, q_heaps):

        # I curently have a heap with qid as key and list of pairs of (score, best candid)
        # exp found in dup_score_details[qid][expected_questions]

        wanted_q_ids = list(q_heaps.keys())
        success_num = 0
        success_denom = len(wanted_q_ids)
        for curr_q_id, curr_heap in q_heaps.items():
            predicted_best = set([x[1] for x in curr_heap])
            actual_best = self.dup_score_details[curr_q_id][
                'expected_questions']
            matched = predicted_best.intersection(actual_best)
            if len(matched):
                success_num += 1
        params_score = success_num / success_denom
        return params_score


if __name__ == "__main__":
    begin = datetime.datetime.now()

    # sorted = 3000 posts
    # duplicate path = 300 elements
    # question_path = folder path where 60 files are stored
    composer = Composer(duplicate_path=sys.argv[1], question_path=sys.argv[2])
    # composer.duplicate_similarity()
    best_params, best_score = composer.param_estimation()
    print(f'final best score: {best_score} with {best_params} params')

    print(datetime.datetime.now() - begin)
