#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# get_ipython().system('ls data_files/All_dup_scores')


# # In[ ]:


import os
from copy import deepcopy
import ujson as json
import sys


test_lb_id=int(sys.argv[1])
test_ub_id=int(sys.argv[2])
file_id=int(sys.argv[3])
assert(test_ub_id>test_lb_id)
assert(test_ub_id<100)

# #### Load the files storing the <q_id, list of <4 scores with each contender>

# In[ ]:


with open("./data_files/All_dup_scores/jac_dup_score_details_100_test.json",'r') as fd:
    df=json.load(fd)

print("file loaded")

# In[ ]:


type(df)


# In[ ]:


list(df.keys())[0:3]


# #### verifying there are 100 keys, one per each question in the test set

# In[ ]:


assert(len(df.keys())==100)


# In[ ]:


df['440482']


# In[ ]:


coeff_id_mapping_to_param_pos={
    0:"title_score",
    1:"body_score",
    2:"topic_score",
    3:"tag_score",
    4:"jaccard_sim"
}


# In[ ]:


with open("params_models.json",'r') as fd:
    params_dict=json.load(fd)


# In[ ]:


MAX_PARAMS=5


# In[ ]:


for curr_elem in params_dict:
    # see if number of coeffs less than MAX_PARAMS and pad with zeroes to the right
    while(len(curr_elem['params_arr'])<MAX_PARAMS):
        curr_elem['params_arr'].append(0)


# In[ ]:


params_dict


# ### Store scores

# In[ ]:



keys_list=list(df.keys())[test_lb_id:test_ub_id+1]
assert(len(keys_list)==test_ub_id-test_lb_id+1)

for curr_key in list(df.keys())[:]:
    if curr_key not in keys_list:
        del df[curr_key]
print("keys left is ", df.keys())

curr_test_id=0
for curr_test_q_id, curr_elem in df.items():
    # iterate through each candidate
    print("curr_test id is ", curr_test_id, len(curr_elem['scores']))
    curr_test_id+=1
    for curr_candidate_q in curr_elem['scores']:
        curr_candidate_q['cm_s']=[]
        # store candidates score for each model
        # iterate through each model
        for curr_model in params_dict:
            curr_score=0
            for param_idx, param_val in enumerate(curr_model['params_arr']):
                concerned_feature=coeff_id_mapping_to_param_pos[param_idx]
                curr_score+=param_val * curr_candidate_q[concerned_feature]
                #print("mult : ",param_val , curr_candidate_q[concerned_feature])
            curr_candidate_q['cm_s'].append(curr_score)
        #print("candidate details is ", curr_candidate_q)
        #break
    #break
        

print("All ran")
# In[ ]:


(0.4 * 0) + (0.5 *  0.1500468969841066) + (0.13737961695900214 * 0.006948283464124975) + (0.19916776750438459 * 0.2)


# In[ ]:


with open(f"./data_files/store_model_scores/test_set_q_candidate_model_scores_{file_id}.json",'w') as fd:
    json.dump(df, fd, indent=1)


# In[ ]:



