import streamlit as st
import requests
import os

st.set_page_config(page_title="VirtuaLook", layout="wide")
API_BASE_URL = os.environ.get("INTERNAL_API_URL", "http://localhost:8000/api")

st.title("VirtuaLook")
st.write("Streamlit interface for VirtuaLook")

st.image("https://via.placeholder.com/400x300", caption="Virtual Try-On Output")
if st.button("Start Try-On"):
    st.info("Try-On logic will connect to FastAPI...")
