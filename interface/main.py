"""
:brief: File to run streamlit and visualize the data
"""

import heapq
import streamlit as st
from db import Database
from params import params_dict
import pandas as pd


@st.cache(allow_output_mutation=True,
          hash_funcs={"_thread.RLock": lambda _: None})
def connect_to_db():
    db = Database()
    return db


db = connect_to_db()


@st.experimental_memo()
def get_ques(qid):
    results = db.run_query(
        f"""
        SELECT title, body, cleaned_body, cleaned_title, tags_list
        from questions_v1
        where id = {qid}
        """)
    if len(results):
        question_raw = results[0]
        question = {
            'Title': question_raw[0],
            'Body': question_raw[1],
            'Cleaned Body': question_raw[2],
            'Cleaned Title': question_raw[3],
            'Tags': question_raw[4],
        }
        return question
    else:
        return f"No question with id {qid}"


@st.experimental_memo()
def get_all_test_questions_id():
    results = db.run_query(f"""
    SELECT id
    from question_scores_test;
    """)
    if len(results):
        questions = {}
        for question_raw in results:
            question = {
                'Id': int(question_raw[0]),
            }
            questions[question['Id']] = question
        return questions
    else:
        return {}


@st.experimental_memo()
def get_questions(qids):
    results = db.run_query(f"""
    SELECT cleaned_title, cleaned_body, tags_list
    from questions
    where  id in ({",".join(list(map(str, qids)))}) 
    """)
    if len(results):
        questions = {}
        for qid, question_raw in zip(qids, results):
            question = {
                'Title': question_raw[0],
                'Body': question_raw[1],
                'Cleaned Body': question_raw[2],
                'Cleaned Title': question_raw[2],
                'Tags': question_raw[2],
            }
            questions[qid] = question
        return questions
    else:
        return {}


@st.experimental_memo(suppress_st_warning=True)
def get_score_data(qid):
    st.write("Cache Miss")
    results = db.run_query(
        f"""
        SELECT data
        from question_scores_test
        where id = {qid}
        """)
    if len(results):
        questions_raw = results[0]
        data = questions_raw[0]
        return data
    else:
        return f"Not found question {qid}"


@st.experimental_memo(suppress_st_warning=True)
def get_score_data_bert(qid):
    results = db.run_query(
        f"""
        SELECT data
        from question_scores_bert
        where id = {qid}
        """)
    if len(results):
        questions_raw = results[0]
        data = questions_raw[0]
        return data
    else:
        return f"Not found question {qid}"


@st.experimental_memo(suppress_st_warning=True)
def get_duplicate(params, qid, jac, K):
    scores_data = get_score_data(qid)
    if isinstance(scores_data, str):
        return 'Not found'
    scores = scores_data['scores']
    init_heap = []
    for score_obj in scores:
        score = score_obj['title_score'] * params[0]
        score += score_obj['body_score'] * params[1]
        score += score_obj['topic_score'] * params[2]
        score += score_obj['tag_score'] * params[3]
        if jac:
            score += score_obj['jaccard_sim'] * params[4]

        heapq.heappush(init_heap, (score, score_obj['candidate_qid']))

        if len(init_heap) > K:
            heapq.heappop(init_heap)
    return init_heap


# @st.experimental_memo
def get_bert_duplicate(qid, params):
    scores_data = get_score_data_bert(qid)
    if isinstance(scores_data, str):
        return 'Not found'
    scores = scores_data['predicition']
    init_heap = []
    for score_obj in scores:
        score = score_obj['title_score'] * params[0]
        score += score_obj['body_score'] * params[1]

        heapq.heappush(init_heap, (score, score_obj['id']))

        if len(init_heap) > K:
            heapq.heappop(init_heap)
    return init_heap


all_test_scores = get_all_test_questions_id()
qid = st.sidebar.selectbox(label='Question Id',
                           options=list(all_test_scores.keys()))
question = get_ques(qid)

use_bert_fine_tune = st.sidebar.checkbox("Use Bert fine tune")
if not use_bert_fine_tune:
    use_jaccard = st.sidebar.checkbox("Use Jaccard Co-efficient")
else:
    use_jaccard = False

options = list(params_dict.keys())
if use_bert_fine_tune:
    options = [options[0]]
elif use_jaccard:
    options = [options[-1]]
else:
    options = options[:-1]

K = st.sidebar.number_input('K', value=20, max_value=25)
if not use_bert_fine_tune:
    choice = st.sidebar.selectbox('Preset Parameters', options=options)
else:
    choice = options[0]

params = params_dict[choice]

if use_bert_fine_tune:
    bert_a = st.sidebar.number_input('Bert a', value=.6)
    bert_b = st.sidebar.number_input('Bert b', value=.5)
    params_current = [bert_a, bert_b]
else:
    alpha = st.sidebar.number_input('Alpha', value=params[0])
    beta = st.sidebar.number_input('Beta', value=params[1])
    gamma = st.sidebar.number_input('Gamma', value=params[2])
    delta = st.sidebar.number_input('Delta', value=params[3])
    params_current = [alpha, beta, gamma, delta]
    if use_jaccard:
        jac_coeff = st.sidebar.number_input('Jaccard', value=params[4])
        params_current.append(jac_coeff)

st.sidebar.write("#### Post")
st.sidebar.write(question)

## Main screen


st.write("""#### Formula used for computing similarity""")
if use_bert_fine_tune:
    st.write(f"""$$
        BERT Similarity = {params_current[0]:.2f}*bert\_title\_similarity() + {params_current[1]:.2f} * bert\_body\_similarity() $$
        """)
else:
    if use_jaccard:
        st.write(f"""$$
            Similarity = {params_current[0]:.2f} * title\_similarity() + {params_current[1]:.2f} * topic\_similarity + 
            {params_current[2]:.2f} * body\_similarity() + {params_current[3]:.2f} * tags\_similarity() + {params_current[4]:.2f} * jaccard\_similarity()$$
            """)
    else:
        st.write(f"""$$
            Similarity = {params_current[0]:.2f} * title\_similarity() + {params_current[1]:.2f} * topic\_similarity + 
            {params_current[2]:.2f} * body\_similarity() + {params_current[3]:.2f} * tags\_similarity() $$
            """)

duplicate_ques = None
if use_bert_fine_tune:
    duplicate_ques = get_bert_duplicate(qid, params_current)
else:
    duplicate_ques = get_duplicate(params_current, qid, use_jaccard, K)
df = pd.DataFrame(duplicate_ques, columns=['Similarity', 'Question Id'])
questions = get_questions(df['Question Id'].to_list())
df['Title'] = df['Question Id'].apply(lambda _qid: questions[_qid]['Title'])
if use_bert_fine_tune:
    expected_questions = list(map(int, get_score_data_bert(qid)['expected']))
else:
    expected_questions = list(
        map(int, get_score_data(qid)['expected_questions']))
df['Correct'] = df['Question Id'].apply(
    lambda _qid: _qid in expected_questions)


def mark_correct(s):
    return ['background-color: green'] * len(s) if s.Correct else [
                                                                      'background-color: none'] * len(
        s)


df.sort_values(by='Similarity', inplace=True, ascending=False)
df.reset_index(inplace=True)
df.drop('index', 1, inplace=True)
marked = df.style.apply(mark_correct, axis=1)
st.dataframe(marked, height=600)
