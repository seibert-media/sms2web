from os import environ, getcwd
from os.path import dirname, realpath, join
import sqlite3

DATA_PATH = environ.get('DATA_PATH') or realpath(join(getcwd(), dirname(__file__)))
DB_PATH = join(DATA_PATH, 'sms2web.db')


def select(query, **params):
    return _query(query, **params).fetchall()


def insert(query, **params):
    return _query(query, **params).lastrowid


def delete(query, **params):
    return _query(query, **params).rowcount


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
    _query('''
        CREATE TABLE IF NOT EXISTS sms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            timestamp INTEGER NOT NULL, -- the time sent by the provider
            received_at INTEGER NULL, -- the time the message was received by sms2web
            sender INTEGER NOT NULL
        )
    ''')
    _query('''
        CREATE INDEX IF NOT EXISTS index_sms_on_timestamp
        ON sms (timestamp)
    ''')
    _query('''
        CREATE INDEX IF NOT EXISTS index_sms_on_received_at
        ON sms (received_at)
    ''')
    _query('''
        CREATE TABLE IF NOT EXISTS sms77_nonce (
            nonce TEXT PRIMARY KEY,
            expires INTEGER NOT NULL
        )
    ''')
    _query('''
        CREATE INDEX IF NOT EXISTS index_sms77_nonce_on_expires
        ON sms77_nonce (expires)
    ''')
