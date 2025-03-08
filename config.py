import streamlit as st
from sqlalchemy import create_engine
from urllib.parse import quote_plus

def get_db_engine():
    db_url = st.secrets["database"]["DB_URL"]
    return create_engine(db_url)
