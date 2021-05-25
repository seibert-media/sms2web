from os import environ, getcwd
from os.path import dirname, realpath, join, exists
from contextlib import closing
import sqlite3

DATA_PATH = environ.get('DATA_PATH') or realpath(join(getcwd(), dirname(__file__)))
DB_PATH = join(DATA_PATH, 'sms2web.db')


def select(query, **params):
    return _query(query, **params).fetchall()


def insert(query, **params):
    return _query(query, **params).lastrowid


def _query(query, **params):
    sqlite3.paramstyle = 'named'

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

    return cursor


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init_db():
    if not exists(DB_PATH):
        _query('''
            CREATE TABLE sms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                sender INTEGER NOT NULL
            )
        ''')
        _query('''
            CREATE INDEX index_sms_on_timestamp
            ON sms (timestamp)
        ''')
