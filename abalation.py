"""
:brief: To ablate one parameter out of 4 using composer and re-train the model.
"""
import datetime
import heapq
import json
import os
from random import random
import sys
from tqdm import tqdm


class Ablation:
    def __init__(self, score_path="", param_ablate="2"):
        self.score_path = score_path
        self.param_ablate = int(param_ablate)
        self.num_params = 4
        assert (self.param_ablate >= 0 and self.param_ablate < self.num_params)
        self.iterations = 10
        self.dup_score_details = {}
        self.K = 20  # recall

    def duplicate_similarity(self):

        # Load all duplicate question scores
        print("Opening and loading all duplicate score")
        with open(self.score_path, "r") as f:
            self.dup_score_details = json.load(f)
        
        print("All scores loaded")
        
    def cal_param_scores_for_a_question(self, params, scores_dict):

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

        # expected output = alpha, beta, gamma, delta
        # return a array with 4 tuple values

        # best params and score from all restarts
        best_params = [0 for _ in range(self.num_params)]
        best_score = 0

        # heaps for each duplicate question which contain top K questions as predicted by algorithm
        q_heaps = {
            _id: heapq.heapify([]) for _id in self.dup_score_details.keys()
        }

        for _ in tqdm(range(self.iterations)):

            # random restart type approach, for each iteration choose a new set of starting params
            init_params = [random() for _ in range(self.num_params)]
            init_params[self.param_ablate] = 0

            for dup_q_id in self.dup_score_details.keys():
                q_heaps[dup_q_id] = self.cal_param_scores_for_a_question(init_params,
                                                                         self.dup_score_details[dup_q_id][
                                                                             "scores"])
            # score for initial set of params
            init_score = self.evaluation_criteria(q_heaps)

            # trial params are copy of initial set of params
            params = init_params.copy()

            # update and try values for each parameter iteratively
            for i in range(self.num_params):
                if i == self.param_ablate:
                    continue
                j = 0
                while j < 1.01:
                    # try each value from 0 to 1
                    params[i] = j

                    # iterate through each duplicate question
                    for dup_q_id in self.dup_score_details.keys():
                        # calculate scores using current set of trial params
                        q_heaps[dup_q_id] = self.cal_param_scores_for_a_question(params,
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
            actual_best = self.dup_score_details[curr_q_id]['expected_questions']
            matched = predicted_best.intersection(actual_best)
            if len(matched):
                success_num += 1
        params_score = success_num / success_denom
        return params_score


if __name__ == "__main__":
    begin = datetime.datetime.now()

    ablation = Ablation(score_path=sys.argv[1], param_ablate=sys.argv[2])
    ablation.duplicate_similarity()
    best_params, best_score = ablation.param_estimation()
    print(f'Final Best Score: {best_score} with {best_params} params ablating param {sys.argv[2]}')

    print(datetime.datetime.now() - begin)
