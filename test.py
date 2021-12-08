"""
:brief: To get the results on test dataset using the best parameters
"""
import datetime
import heapq
import json
from random import random
import sys
from tqdm import tqdm
import pandas as pd



class Tester:
    def __init__(self, score_path=""):
        self.score_path = score_path
        self.dup_score_details = {}
        self.K = 10  # recall
        self.errors = {}
        self.random_results = []

    def duplicate_loader(self):

        # Load all duplicate question scores
        print("Opening and loading all duplicate score")
        with open(self.score_path, "r") as f:
            self.dup_score_details = json.load(f)
        
        print("All scores loaded")

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

            if len(init_heap) > self.K:
                heapq.heappop(init_heap)

        # return list of pairs (score, qid)
        return init_heap

    def random_scorer(self):
        q_heaps = {
            _id: heapq.heapify([]) for _id in self.dup_score_details.keys()
        }

        best_params = [0.9, 0.85, 0.3152632209444808, 0.3]
        self.random_results.append({"alpha": best_params[0], "beta": best_params[1], "gamma": best_params[2], "delta": best_params[3], "recall-rate@10": 0.56, "recall-rate@20": 0.64})
        
        for _ in tqdm(range(50)):
            params = [random() for _ in range(4)]

            # random restart type approach, for each iteration choose a new set of starting params
            for dup_q_id in tqdm(self.dup_score_details.keys()):
                q_heaps[dup_q_id] = self.cal_param_scores_for_a_question(params,
                                                                            self.dup_score_details[dup_q_id][
                                                                                "scores"])
            # score for initial set of params
            test_score_20 = self.evaluation_criteria(q_heaps)
            
            self.K = 10 # changing k to 10
            for dup_q_id in tqdm(self.dup_score_details.keys()):
                q_heaps[dup_q_id] = self.cal_param_scores_for_a_question(params,
                                                                            self.dup_score_details[dup_q_id][
                                                                                "scores"])
            # score for initial set of params
            test_score_10 = self.evaluation_criteria(q_heaps)
            self.K = 20 #reseting
            
            self.random_results.append({"alpha": params[0], "beta": params[1], "gamma": params[2], "delta": params[3], "recall-rate@10": test_score_10, "recall-rate@20": test_score_20})
        
        df = pd.DataFrame(self.random_results)
        df.sort_values(by=['recall-rate@20', 'recall-rate@10'], inplace=True, ascending=False)
        df.to_csv('random_results.csv')

    def scorer(self):
        """estimates all the parameters of the weighted sum of the components"""

        # expected output = alpha, beta, gamma, delta
        # return a array with 4 tuple values

        # best params and score from all restarts
        best_params = [0.49999999999999994, 0.49999999999999994, 0.045457461811456046, 0.44999999999999996]
        test_score = 0

        # heaps for each duplicate question which contain top K questions as predicted by algorithm
        q_heaps = {
            _id: heapq.heapify([]) for _id in self.dup_score_details.keys()
        }

        # random restart type approach, for each iteration choose a new set of starting params

        for dup_q_id in tqdm(self.dup_score_details.keys()):
            q_heaps[dup_q_id] = self.cal_param_scores_for_a_question(best_params,
                                                                        self.dup_score_details[dup_q_id][
                                                                            "scores"])
        # score for initial set of params
        test_score = self.evaluation_criteria(q_heaps)

        # with open('ablate_2_error.json', 'w') as f:
        #     json.dump(self.errors, f)

        # return best params from all restarts
        return best_params, test_score

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
            else:
                self.errors[curr_q_id] = {'expected_questions': list(actual_best), 'prediction': list(predicted_best)}
        params_score = success_num / success_denom
        return params_score


if __name__ == "__main__":
    begin = datetime.datetime.now()

    # sorted = 3000 posts
    # duplicate path = 300 elements
    # question_path = folder path where 60 files are stored
    composer = Tester(score_path=sys.argv[1])
    composer.duplicate_loader()
    best_params, test_score = composer.scorer()
    # composer.random_scorer()
    print(f'final best score: {test_score} with {best_params} params')

    print(datetime.datetime.now() - begin)
