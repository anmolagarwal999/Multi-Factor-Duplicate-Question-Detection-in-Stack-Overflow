"""
 Get the top 30 for the test 100 duplicate questions
 Append any left off expected questions
 Populate the ids with data
 Run bert embeddings for this
 Calculate the score
 Find a good linear combination for the two scores
 Rerank the questions and find if there is an improvement
"""

import datetime
import heapq
import json
import sys
from tqdm import tqdm
import numpy as np
from sentence_transformers import SentenceTransformer
from preprocessing import Preprocess

class TopK:
    def __init__(self, score_path=""):
        self.score_path = score_path
        self.dup_score_details = {}
        self.K = 30
        self.processing = Preprocess()
        self.findings = {}
        self.model = SentenceTransformer('bert-base-nli-mean-tokens')

    def duplicate_loader(self):

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

        return init_heap

    def finder(self):
        best_params = [0.9, 0.85, 0.3152632209444808, 0.3]

        q_heaps = {
            _id: heapq.heapify([]) for _id in self.dup_score_details.keys()
        }

        for dup_q_id in tqdm(self.dup_score_details.keys()):
            q_heaps[dup_q_id] = self.cal_param_scores_for_a_question(best_params,
                                                                        self.dup_score_details[dup_q_id][
                                                                            "scores"])

        for curr_q_id, curr_heap in q_heaps.items():
            predicted_best = [x[1] for x in curr_heap]
            actual_best = self.dup_score_details[curr_q_id]['expected_questions']
            
            best_not_included = [ques for ques in actual_best if ques not in predicted_best]
            predicted_best.extend(best_not_included)
            self.findings[curr_q_id] = {'ranking': predicted_best, 'expected': actual_best}

        with open(f'top_{self.K}_preds_test.json', 'w') as f:
            json.dump(self.findings, f, indent=2)

    def populate(self, question_path=""):
        with open(f'top_{self.K}_preds_test.json', 'r') as f:
            self.findings = json.load(f)
        
        for i in tqdm(range(50)):
            with open(f'{question_path}/{i}.json', 'r') as f:
                cand_questions = json.load(f)

                for qid, data in self.findings.items():
                    for index, cand_id in enumerate(data['ranking']):
                        if (type(cand_id) != dict) and str(cand_id) in cand_questions:
                            self.findings[qid]['ranking'][index] = cand_questions[str(cand_id)]

        with open(f'top_{self.K}_preds_test_pop.json', 'w') as f:
            json.dump(self.findings, f)
            
    def bert_embedding_pop(self): 
        
        
        with open(f'top_{self.K}_preds_test_pop.json', 'r') as f:
            self.findings = json.load(f)
            
        [
            [
                self.findings[qid]['ranking'][index].update(
                    {
                        "title_bert": list(np.float_(self.model.encode(cand['cleaned_title']))),
                        "body_bert": list(np.float_(self.model.encode(cand['cleaned_body'])))
                    }
                )
                for index, cand in enumerate(data['ranking'])
            ]
            for qid, data in tqdm(self.findings.items())
        ]
        
        with open(f'top_{self.K}_preds_test_pop_emb.json', 'w') as f:
            json.dump(self.findings, f)
    
    def create_bert_embedding_dup(self, dup_path=""):
        
        with open(f'{dup_path}/0.json', 'r') as f:
            dups = json.load(f)
        
        imp_dups = {}    
        activate_dup_keys = list(dups.keys())[300: 400]
        
        for qid in activate_dup_keys:
            imp_dups[qid] = dups[qid].copy()
            imp_dups[qid].update(
                {
                "title_bert": list(np.float_(self.model.encode(dups[qid]['cleaned_title']))),
                "body_bert": list(np.float_(self.model.encode(dups[qid]['cleaned_body'])))
                }
            )

        with open(f'test_dups_bert_embedding.json', 'w') as f:
            json.dump(imp_dups, f)

    def sim_score(self): 
        
        with open(f'top_{self.K}_preds_test_pop_emb.json', 'r') as f:
            self.findings = json.load(f)
        
        with open(f'test_dups_bert_embedding.json', 'r') as f:
            duplicates = json.load(f)

        [
            [
                self.findings[qid]['ranking'][index].update(
                    {
                        "sim_score_title": self.processing.cosine_similarity(duplicates[qid]["title_bert"], cand["title_bert"]),
                        "sim_score_body": self.processing.cosine_similarity(duplicates[qid]["body_bert"], cand["body_bert"])
                    }
                )
                for index, cand in enumerate(data['ranking'])
            ]
            for qid, data in tqdm(self.findings.items())
        ]
        
        with open(f'top_{self.K}_preds_test_pop_emb_score.json', 'w') as f:
            json.dump(self.findings, f)

    def rerank(self):
        with open(f'top_{self.K}_preds_test_pop_emb_score.json', 'r') as f:
            self.findings = json.load(f)
            
        params = [0.6, 0.5]

        q_heaps = {
            _id: heapq.heapify([]) for _id in self.findings.keys()
        }
        
        for qid, data in tqdm(self.findings.items()):
            init_heap = []

            for index, score_obj in enumerate(data['ranking']):
                composer_score = (
                        score_obj["sim_score_title"] * params[0]
                        + score_obj["sim_score_body"] * params[1]
                )

                heapq.heappush(
                    init_heap,
                    (composer_score, score_obj["Id"], index),
                )
            
            q_heaps[qid] = init_heap

        return self.evaluation_criteria(q_heaps)
            

    def evaluation_criteria(self, q_heaps):
        unique_20 = 0
        score_20 = 0
        score_30 = 0

        for curr_q_id, curr_heap in q_heaps.items():
            actual_best = self.findings[curr_q_id]['expected']
            flag_already = 0
            for index, cand in enumerate(curr_heap):
                if cand[1] in actual_best:
                    if cand[2] <= 20:
                        flag_already = 1
                        break
            for index, cand in enumerate(curr_heap):
                if cand[1] in actual_best:
                    if cand[2] > 30 and index <= 20:
                        score_30 += 1
                    if cand[2] > 20 and index <= 20:
                        score_20 += 1
                        if flag_already == 0:
                            unique_20 += 1
                    

        return score_20, unique_20, score_30
        


if __name__ == "__main__":
    begin = datetime.datetime.now()

    topper = TopK(score_path=sys.argv[1])
    # topper.duplicate_loader()
    # topper.finder()
    # topper.populate(question_path=sys.argv[2])
    # topper.bert_embedding_pop()
    # topper.create_bert_embedding_dup(dup_path="full_proper_dups")
    # topper.sim_score()
    score_20, unique_20, score_30 = topper.rerank()
    print(f"Bert Improved: Unique 20: {unique_20}, Richness: {score_20}, RKO out of nowhere: {score_30}")

    print(datetime.datetime.now() - begin)
