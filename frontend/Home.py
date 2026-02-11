import streamlit as st
from typing import Tuple, List, Dict, Any
import httpx
import os

# API_URL = "http://0.0.0.0:8000"
API_URL = os.getenv("BACKEND_URL", "http://0.0.0.0:8000")

st.set_page_config(page_title="RAG Flashcards", layout="wide")

def fetch_decks_and_due_count() -> Tuple[List[Dict[str, Any]], int]:
    try:
        with httpx.Client() as client:
            # hardcoded user id = 1, we don't have login/registration
            response = client.get(f"{API_URL}/decks/?user_id=1")
            if response.status_code == 200:
                decks = response.json()
            else:
                decks = []
                st.error("Failed to fetch decks.")
                
            # fetch Due Count
            due_response = client.get(f"{API_URL}/study/due?user_id=1")
            due_count = len(due_response.json()) if due_response.status_code == 200 else 0
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        decks = []
        due_count = 0
    
    return decks, due_count

def delete_deck():
    try:
        with httpx.Client() as client:
            res = client.delete(f"{API_URL}/decks/{deck['id']}")
                            
            if res.status_code == 200:
                st.success("Deleted!")
                st.rerun()
            else:
                st.error(f"Error: {res.status_code}")
    except Exception as e:
        st.error(f"Connection error: {e}")

# st.title(" WikiCard AI")
# st.subheader("RAG-Powered Flashcard Generation")

st.markdown("""
    <style>
    .vertical-center {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

col_logo, col_text = st.columns([2, 2], vertical_alignment="center")
with col_logo:
    st.image("sources/godlo_wat_z_nazwa_angielska.png", width="stretch")

with col_text:
    st.title("WikiCard AI", text_alignment="center")
    st.caption("RAG-Powered Flashcard Generation", width="stretch", text_alignment="center")
    st.markdown(
    """
    <div style="text-align: center; line-height: 1.6;">
        <strong>Przedmiot:</strong> Programowanie w Językach Funkcyjnych<br>
        <strong>Prowadzący:</strong> mgr inż. Piotr Bączyk<br>
        <br>
        <strong>Autor:</strong> Michał Ślęzak<br>
        WCY23IJ2S1 | 860 65
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# sidebar for actual status
with st.sidebar:
    st.write("Logged in as: User 1")

# fetch decks
# try:
#     with httpx.Client() as client:
#         # hardcoded user id = 1, we don't have login/registration
#         response = client.get(f"{API_URL}/decks/?user_id=1")
#         if response.status_code == 200:
#             decks = response.json()
#         else:
#             decks = []
#             st.error("Failed to fetch decks.")
            
#         # fetch Due Count
#         due_response = client.get(f"{API_URL}/study/due?user_id=1")
#         due_count = len(due_response.json()) if due_response.status_code == 200 else 0
# except Exception as e:
#     st.error(f"Could not connect to backend: {e}")
#     decks = []
#     due_count = 0
decks, due_count = fetch_decks_and_due_count()

# MSM-2 metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Decks", len(decks))
with col2:
    st.metric("Cards Due Now", due_count, delta_color="inverse")

st.markdown("### Your Decks")
if not decks:
    st.info("No decks found. Go to 'Generate Deck' to create one 😌")
else:
    for deck in decks:
        with st.expander(f"📖 {deck['title']}"):
            st.markdown(f"**Desc:** {deck.get('description', 'No description')}")
            st.markdown(f"**Status:** {deck['status']}")

            col_action, col_delete = st.columns([0.85, 0.15])
            with col_action:
                if st.button("Go to your decks", key=f"deck_page_btn_{deck['id']}", help="Go to Study Deck page"):
                    st.switch_page("pages/3_Study_Deck.py")

            with col_delete:
                if st.button("🗑️", key=f"del_{deck['id']}", help="Delete this deck"):
                    # try:
                    #     with httpx.Client() as client:
                    #         res = client.delete(f"{API_URL}/decks/{deck['id']}")
                            
                    #         if res.status_code == 200:
                    #             st.success("Deleted!")
                    #             st.rerun()
                    #         else:
                    #             st.error(f"Error: {res.status_code}")
                    # except Exception as e:
                    #     st.error(f"Connection error: {e}")
                    delete_deck()
