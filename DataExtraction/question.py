from dataclasses import dataclass, field


@dataclass
class Question:
    qid: int
    body: str
    creation_date: str
    last_activity_date: str
    last_edit_date: str
    title: str
    tags: list[int] = field(default_factory=list)
    dups: list[int] = field(default_factory=list)


def preprocess_tags(s: str):
    tags = []
    try:
        for tag in s.split('>'):
            tag = tag[1:]
            tag = tag.strip()
            if tag != '' and tag is not None:
                tags.append(tag)
    except Exception:
        pass
    return tags


def get_question(one_object) -> Question:
    q = Question(
        qid=one_object['Id'],
        body=one_object['Body'],
        last_activity_date=one_object['LastActivityDate'],
        last_edit_date=one_object['LastEditDate'],
        tags=preprocess_tags(one_object['Tags']),
        title=one_object['Title'],
        creation_date=one_object['CreationDate'])
    return q
