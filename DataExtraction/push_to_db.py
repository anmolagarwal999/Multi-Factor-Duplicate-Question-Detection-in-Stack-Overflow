# Not complete

import psycopg2
conn = None
cur = None

def connect_to_database():
    global conn
    conn = psycopg2.connect(host='localhost', database='core', user='postgres', password='password')

def get_db():
    global conn, cur
    if conn is None:
        connect_to_database()
    if cur is None:
        cur = conn.cursor()
    return cur


def refresh_table():
    db = get_db()
    
    print(db)

def main():
    refresh_table()

if __name__ == '__main__':
    main()
    


