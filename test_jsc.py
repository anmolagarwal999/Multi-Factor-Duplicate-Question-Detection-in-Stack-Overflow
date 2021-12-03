import json


def jac_present():
    dup_score_details = {}
    print("loading...")
    with open('jac_dup_score_details_300.json', "r") as f:
        dup_score_details = json.load(f)
    print("done..")
    count = 0
    many = 0
    for qid, dup in dup_score_details.items():
        for score_obj in dup["scores"]:
            # print(score_obj)
            if "jaccard_sim" not in score_obj.keys():
                many+=1
                if count == 0:
                    print(qid, dup)
                    count+=1

    print(many)

jac_present()