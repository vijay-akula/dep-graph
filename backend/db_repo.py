# db_repo.py

import sqlite3
from contextlib import contextmanager

DB_PATH = "graph.db"

@contextmanager
def get_db_cursor():
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db_cursor() as cursor:
        # Create the main graph table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph (
                node_id TEXT PRIMARY KEY,
                status TEXT
            );
        ''')

        # Create the node_dependencies table with correct schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS node_dependencies (
                node_id TEXT,
                dependency TEXT
            );
        ''')


def insert_node(node_id, status="pending"):
    with get_db_cursor() as cursor:
        cursor.execute('INSERT OR REPLACE INTO graph (node_id, status) VALUES (?, ?)', (node_id, status))

def insert_dependency(node_id, dependency):
    with get_db_cursor() as cursor:
        cursor.execute('INSERT OR IGNORE INTO node_dependencies (node_id, dependency) VALUES (?, ?)', (node_id, dependency))

def update_node_status(node_id, status):
    with get_db_cursor() as cursor:
        cursor.execute('UPDATE graph SET status = ? WHERE node_id = ?', (status, node_id))

def get_all_nodes():
    with get_db_cursor() as cursor:
        cursor.execute('SELECT node_id, status FROM graph')
        return cursor.fetchall()

def get_all_dependencies():
    with get_db_cursor() as cursor:
        cursor.execute('SELECT node_id, dependency FROM node_dependencies')
        rows = cursor.fetchall()

    dep_map = {}
    for node_id, dependency in rows:
        dep_map.setdefault(node_id, []).append(dependency)
    return dep_map

def get_dependencies_for_node(node_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT dependency FROM node_dependencies WHERE node_id = ?", (node_id,))
        return [row[0] for row in cursor.fetchall()]

def get_nodes_by_status(status):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT node_id FROM graph WHERE status = ?", (status,))
        return [row[0] for row in cursor.fetchall()]
