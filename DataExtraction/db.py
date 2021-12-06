"""
:brief: Create a interface class to communicate with the database
"""
import psycopg2
from psycopg2.extras import execute_values, DictCursor
from question import Question

columns_w_type = [("Body", str),
                  ("CreationDate", str), ("Id", int), ("PostTypeId", int),
                  ("Tags", str), ("Title", str), ("cleaned_body", str),
                  ("cleaned_title", str), ("body_vec", list),
                  ("title_vec", list), ("dups_list", list), ("tags_list", list),
                  ("topic", list)
                  ]
cols = [col[0] for col in columns_w_type]


class Database:
    def __init__(self):
        """Create a Postgres Database interface class"""
        self.conn = psycopg2.connect(host='localhost', database='core',
                                     user='postgres', password='password')

    def get_db(self):
        """Get a cursor to manupilate data"""
        cur = self.conn.cursor()
        return cur

    def drop_questions(self):
        """Drop all questions"""
        db = self.get_db()
        query = """
        DROP TABLE IF EXISTS Questions;
        """
        db.execute(query)
        self.commit()

    def commit(self):
        """Commit the changes to database"""
        try:
            self.conn.commit()
        except Exception:
            self.conn.rollback()

    def create_questions(self):
        """Create a table to store the questions"""
        query = """
        CREATE TABLE Questions (
            Body text,
            CreationDate TIMESTAMP,
            Id int PRIMARY KEY,
            PostTypeId int,
            Tags text,
            Title text,
            cleaned_body text,
            cleaned_title text,
            body_vec text[],
            title_vec text[],
            dups_list text[],
            tags_list text[],
            topic numeric[]
        );
        """
        db = self.get_db()
        db.execute(query=query)
        self.commit()

    def add_questions(self, questions):
        """Add questions to database"""
        query = f"""
        INSERT INTO Questions ({",".join(cols)}) VALUES %s
        """
        value_list = []
        for q in questions:
            try:
                value = []
                for col, t in columns_w_type:
                    value.append(t(q[col]))
                value_list.append(tuple(value))
            except Exception as err:
                print(q)
                print(err)
                exit(1)
        cur = self.get_db()
        execute_values(cur, query, value_list)
        self.commit()

    def refresh_questions(self):
        """Delete all questions and create a new table"""
        self.drop_questions()
        self.create_questions()

    def get_questions(self, start_row, n_docs):
        """
        Get `n_docs` questions from `start_row` sorted by CreationDate
        """
        query = f"""
        select * from questions order by CreationDate asc offset {start_row} limit {n_docs};
        """
        cur = self.get_db()
        cur.execute(query)
        records = cur.fetchall()
        print(len(records))
        questions = {}
        _id = start_row
        for rec in records:
            q = {}
            for i in range(len(columns_w_type)):
                q[cols[i]] = rec[i]
                if cols[i] == 'CreationDate':
                    q[cols[i]] = rec[i].isoformat()
                if cols[i] == 'topic' and rec[i] is not None:
                    q[cols[i]] = [float(t) for t in rec[i]]
            q['sort_id'] = _id
            questions[q['sort_id']] = q
            _id += 1
        self.commit()
        return questions

    def update_questions(self, questions, new_col):

        """
        Temporary function to merge LDA topic values to the database
        """
        query = f"""
        UPDATE questions SET {new_col}=data.{new_col} FROM (VALUES %s) AS data(Id, {new_col}) WHERE questions.Id = data.Id;
        """
        value_list = []
        for q in questions:
            value_list.append((int(q['qid']), list(map(float, q[new_col]))))
        cur = self.get_db()
        execute_values(cur, query, value_list)
        self.commit()
