#!/usr/bin/env python
# coding: utf-8

# In[33]:


import os
import json
import re
from preprocessing import Preprocess as preprocess_class
from copy import deepcopy


# In[34]:


preprocess_object=preprocess_class()


# ### Decide the input and output paths

# In[35]:


PREFIX_FILE_PATH="data_files/pp_nov_28/result/"
PREFIX_OUTPUT_FILE_PATH="data_files/cleaned_pp_nov_28_all/"


# In[36]:


lb_file_idx=0
ub_file_idx=102


# ### To clean self-closing tags and both closing tags from URL

# In[37]:


#https://stackoverflow.com/a/11229866
self_contained_ref_regex=r"<[^>]*>"
self_contained_ref_pattern=re.compile(self_contained_ref_regex)

def clean_tags_prevent_content(curr_text):
    curr_text=self_contained_ref_pattern.sub(" ",curr_text)
    return curr_text


# ##### Tests

# In[38]:


tc_cases=["< Hello> There </Hello>",
            "billy butcher",
              "<Doncaster/>"
            ]


# In[39]:


for curr_tc in tc_cases:
    print("tc is ",curr_tc)
    print("Output  is ",clean_tags_prevent_content(curr_tc) )
    print("**********")


# ### Cleaning newlines and tabs

# In[40]:


def clean_newline_stuff(curr_text):
    curr_text=curr_text.replace("\n","")
    curr_text=curr_text.replace("\t","")
    return curr_text


# #### Fetching question tags

# In[41]:


def fetch_tags_list(tag_text):
    arr=tag_text.split(">")
    arr=list(filter(lambda x:x!="",arr))
    arr=[x[1:] for x in arr]
    return arr


# In[42]:


tc_cases=['<performance><unix><awk><aix>',
            '<c#><exception><error-handling>',
              "<Doncaster>"
            ]


# In[43]:


for curr_tc in tc_cases:
    print("tc is ",curr_tc)
    print("Output  is ",fetch_tags_list(curr_tc) )
    print("**********")


# ### Removing all variations of the word "DUPLICATE" from title

# In[44]:


test_dup_reg=re.compile(r"\[\s*duplicate\s*\]", re.IGNORECASE)
testing_dup_title_string=["abcd [  duplicaTe] fghi j "
                            ,"[   duplicaTE       ]"
                             ,"[duplicaTE]"
                          ,"abcdef [duplicaTE] dupl sis os"        ,
                          "skjsis9",
                          "Is null harmful? [Duplicate]"
                         ]

#dup_regex = re.compile("duplicate", re.IGNORECASE)
def rem_dup(text):
    return test_dup_reg.sub(" ", text)

for curr_tc in testing_dup_title_string:
    matches=test_dup_reg.findall(curr_tc)
    print(curr_tc)
    print(matches)
    print("Rem part is ", rem_dup(curr_tc))
    print("##########")


# In[ ]:





# ### Removing "code"/blockquote tag and the content inside it

# In[45]:


code_paired_refs_regex=r"<code((.|\n)*?)<\/code>"
code_paired_refs_pattern=re.compile(code_paired_refs_regex)
def rem_code(text):
    return code_paired_refs_pattern.sub(" ", text)


# ##### test code block removal

# In[46]:


tc=["<p>I'm new to C# and I want to use a track-bar to change a form's opacity            .</p>\n\n<p>This is my code:</p>\n\n<pre>        <code>decimal trans = trackBar1.Value / 5000;\nthis.Opacity = trans;\n</code>                </pre>\n\n<p>When I try to build it, I get this error:</p>\n\n<blockquote>\n  <p>Cannot implicitly convert type 'decimal' to 'double'</p>\n</blockquote>\n\n<p>I tried making\ <code>trans</code>     a double, but then the control doesn't work. This code worked fine for me in VB.NET. </p>\n\n<p>What do I need to do differently?</p>\n",
    "<code>decimal trans = trackBar1.Value / 5000;\nthis.Opacity = trans;\n</code>",
    "Homelander <code> Hi Hi </code> Bi <code>Hello there</code>"
   ]


# In[47]:


for curr_tc in tc:
    print(curr_tc)
    print(":::::::::")
    print(rem_code(curr_tc))
    print("##################################")


# ##### -----------

# In[48]:


url_regex = re.compile(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})")
def fetch_urls(curr_str):
    url_matches = url_regex.findall(curr_str)      
    return [x[0] for x in url_matches]


# In[49]:


blockquote_paired_refs_regex=r"<blockquote((.|\n)*?)<\/blockquote>"
blockquote_paired_refs_pattern=re.compile(blockquote_paired_refs_regex)
def rem_blockquote(text):
    #print("num is : ",len(fetch_urls(text)))
    if ("blockquote" in text)  and (len(fetch_urls(text))>0):
        return blockquote_paired_refs_pattern.sub(" ", text)
    else:
        return text


# In[50]:


tc=['<blockquote>\n  <h2>Duplicate</h2>\n  \n  <p><a href=\"http://stackoverflow.com/questions/403539/what-are-extension-methods\">What are Extension Methods?</a><br />\n  <a href=\"http://stackoverflow.com/questions/403619/usage-of-extension-methods\">Usage of Extension Methods</a><br />\n  <a href=\"http://stackoverflow.com/questions/487904/what-advantages-of-extension-methods-have-you-found\">What Advantages of Extension Methods have you found?</a>  </p>\n</blockquote>\n',
   "<blockquote>\n  <p>Cannot implicitly convert type 'decimal' to 'double'</p>\n</blockquote>",
   "<blockquote>\n  <p>Duplicate:\n  <a href=\"http://stackoverflow.com/questions/163434/are-nulls-in-a-relational-database-okay\">http://stackoverflow.com/questions/163434/are-nulls-in-a-relational-database-okay</a></p>\n</blockquote>\n"]
for curr_tc in tc:
    print(curr_tc)
    print(":::::::::")
    print("ans is : ",rem_blockquote(curr_tc))
    print("##################################")


# ## =========================================================

# In[51]:


def fetch_question_satisfying_a_condition(fn):
    ans=None
    for file_id in range(lb_file_idx, ub_file_idx+1):
        if ans!=None:
            break
        print("Starting file with id: ", file_id)
        with open(PREFIX_FILE_PATH+f"/post_{file_id}.json",'r') as fd:
            df=json.load(fd)
        new_df=dict()
        for curr_key, curr_val in df.items():
            # we do not want to process answers
            if curr_val["PostTypeId"]!="1":
                continue
            if fn(curr_val):
                ans=deepcopy(curr_val)
                print("Found")
                break
    return ans


# In[52]:


def code_tag_in_body(curr_obj):
    all_matches=code_paired_refs_pattern.findall(curr_obj['Body'])
    return len(all_matches)>0


# In[53]:


def blockquote_tag_in_body(curr_obj):
    all_matches=blockquote_paired_refs_pattern.findall(curr_obj['Body'])
    return len(all_matches)>0


# In[54]:


def fetch_question_id_object(q_id):
    ans=None
    assert(type(q_id)==str)
    for file_id in range(lb_file_idx, ub_file_idx+1):
        if ans!=None:
            break
        print("Starting file with id: ", file_id)
        with open(PREFIX_FILE_PATH+f"/post_{file_id}.json",'r') as fd:
            df=json.load(fd)
        new_df=dict()
        for curr_key, curr_val in df.items():
            # we do not want to process answers
            if curr_val["PostTypeId"]!="1":
                continue
            if curr_val['Id']==q_id:
                ans=deepcopy(curr_val)
                print("Found")
                break
    return ans


# ## ===============================================

# In[55]:


#fetch_question_satisfying_a_condition(code_tag_in_body)


# In[56]:


#fetch_question_satisfying_a_condition(blockquote_tag_in_body)


# In[ ]:





# In[57]:


#fetch_question_id_object("777711")


# #### Just investigate the PostTypeIDs present (DEV)

# In[58]:


def check_post_types():
    for curr_id, curr_val in df.items():
        if curr_val['PostTypeId']!='1':
            print(curr_val['PostTypeId'])


# ## ========================================

# ### Now, first find a duplicate and verify Gurkirat claim of just 2 duplicates using the paper's method

# In[59]:


def find_dups_in_title():
    lb_file_idx=0
    ub_file_idx=102

    potential_dups_yet=0

    for file_id in range(lb_file_idx, ub_file_idx+1):
        print("Starting file with id: ", file_id)
        with open(PREFIX_FILE_PATH+f"/post_{file_id}.json",'r') as fd:
            df=json.load(fd)
        new_df=dict()
        for curr_key, curr_val in df.items():
            # we do not want to process answers
            if curr_val["PostTypeId"]!="1":
                continue
            matches=test_reg.findall(curr_val['Title'])
            if len(matches)>0:
                print(curr_key)
                print(curr_val)
                print("$$$$$$$$$$$$$$$$$$")


# In[60]:


#find_dups_in_title()


# ## ================================================

# ## Run loop

# In[61]:


def clean_post(post_obj):
    new_val=deepcopy(post_obj)
    new_val['cleaned_body']=rem_blockquote(new_val['Body'])
    #print("After rem is ",new_val['cleaned_body'] )
    new_val['cleaned_body']=rem_code(new_val['cleaned_body'])
    new_val['cleaned_body']=clean_tags_prevent_content(new_val['cleaned_body'])
    new_val['cleaned_body']=clean_newline_stuff(new_val['cleaned_body'])

    new_val['cleaned_title']=rem_dup(new_val['Title'])

    new_val['body_vec']=preprocess_object.parse_string(new_val['cleaned_body'])
    new_val['title_vec']=preprocess_object.parse_string(new_val['cleaned_title'])

    try:
        new_val['tags_list']=fetch_tags_list(new_val['Tags'])
    except:
        new_val['tags_list']=[]
        print(curr_val)
        #break
    return new_val


# ### Initial test

# In[62]:


test_arr=[fetch_question_satisfying_a_condition(code_tag_in_body),
         fetch_question_satisfying_a_condition(blockquote_tag_in_body),
          fetch_question_id_object('777711'),
          fetch_question_id_object('783926')
                                               ]


# In[63]:


test_ans=[]
for curr_tc in test_arr:
    curr_d=dict()
    curr_d['input']=deepcopy(curr_tc)
    curr_d['output']=clean_post(curr_tc)
    test_ans.append(curr_d)
with open("sample_of_cleanings.json",'w') as fd:
    json.dump(test_ans, fd, indent=4)


# ### Final loop

# In[64]:


tot_cnt=0


# In[65]:


for file_id in range(lb_file_idx, ub_file_idx+1):
    print("Starting file with id: ", file_id)
    with open(PREFIX_FILE_PATH+f"/post_{file_id}.json",'r') as fd:
        df=json.load(fd)
    new_df=dict()
    for curr_key, curr_val in df.items():
        # we do not want to process answers
        if curr_val["PostTypeId"]!="1":
            continue
        tot_cnt+=1
        if tot_cnt%1000==0:
            print(tot_cnt)
        new_df[curr_key]=clean_post(curr_val)
    print("Finished ", file_id)
    print("-----------")
    with open(PREFIX_OUTPUT_FILE_PATH+f"/post_{file_id}.json",'w') as fd:
        json.dump(new_df, fd, indent=1)


# In[ ]:


tot_cnt

