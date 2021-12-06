import psycopg2
import streamlit as st


class Database:
    def __init__(self, dbname='core'):
        self.dbname = dbname
        self.conn = psycopg2.connect(host='localhost', database=self.dbname,
                                     user='postgres', password='password')

    def get_cur(self):
        """Get cursor to read data"""
        cur = self.conn.cursor()
        return cur

    def commit(self):
        """Commit changes"""
        try:
            self.conn.commit()
        except Exception:
            self.conn.rollback()

    def run_query(self, query: str):
        cur = self.get_cur()
        cur.execute(query)
        records = cur.fetchall()
        self.commit()
        return records

