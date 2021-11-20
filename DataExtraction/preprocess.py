from question import Question, get_question
from bs4 import BeautifulSoup
import re

HTML_CLEAN = re.compile('<.*?>')
WHITESPACE_CLEAN = re.compile('^\\s*|\\s\\s*')


def check_duplicate(title):
    return re.search(r'\[\s*duplicate\s*\]', title, flags=re.IGNORECASE) is not None


def preprocess(obj):
    q = None
    if isinstance(obj, Question):
        q = obj
    elif isinstance(obj, dict):
        q = get_question(obj)
    else:
        return None
    is_duplicate = False
    dup_ids = []
    soup = BeautifulSoup(q.body, 'html.parser')
    if check_duplicate(q.title):
        try:
            for bq in soup.find_all('blockquote'):
                to_remove = False
                for a in bq.find_all('a'):
                    link = a.get('href').split('/')
                    if link[2] == 'stackoverflow.com':
                        dup_ids.append(int(link[4]))
                        to_remove = True
                if to_remove:
                    bq.decompose()
        except Exception:
            pass

    q.body = remove_whitespace(soup.text)
    q.dups = dup_ids
    return q


def remove_html(raw_html):
    return re.sub(HTML_CLEAN, '', raw_html)


def remove_whitespace(text):
    return re.sub(WHITESPACE_CLEAN, ' ', text).strip()


def clean(text):
    text = remove_html(text)
    text = remove_whitespace(text)
    return text
