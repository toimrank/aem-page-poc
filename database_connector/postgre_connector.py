import psycopg2
from psycopg2.extras import execute_values
from config.config_loader import DB_CONFIG
import streamlit as st

conn = None
cursor = None

@st.cache_resource
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def get_cursor(conn):
    cursor = conn.cursor()
    return cursor

def close_connection(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()
