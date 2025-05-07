import sqlite3
from contextlib import contextmanager

DB_PATH = "graph.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

@contextmanager
def get_db_cursor():
    with get_db_connection() as conn:
        yield conn.cursor()


def init_db():
    with get_db_cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph (
                node_id TEXT PRIMARY KEY,
                status TEXT
            );
        ''')


def get_all_nodes():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM graph")
        return cursor.fetchall()


def update_node_status(node_id, status):
    with get_db_cursor() as cursor:
        cursor.execute(
            'INSERT OR REPLACE INTO graph (node_id, status) VALUES (?, ?)',
            (node_id, status)
        )


def initialize_graph(dependencies):
    with get_db_cursor() as cursor:
        for node_id in dependencies:
            cursor.execute(
                'INSERT OR REPLACE INTO graph (node_id, status) VALUES (?, ?)',
                (node_id, "pending")
            )


def get_nodes_by_status(status):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT node_id FROM graph WHERE status = ?", (status,))
        return [row[0] for row in cursor.fetchall()]
