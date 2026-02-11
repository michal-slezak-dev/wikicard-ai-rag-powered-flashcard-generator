import streamlit as st
from typing import List, Dict, Any
import httpx
import os

API_URL = "http://0.0.0.0:8000"
API_URL = os.getenv("BACKEND_URL", "http://0.0.0.0:8000")

def next_card():
    if st.session_state.current_card_index < len(st.session_state.cards) - 1:
        st.session_state.current_card_index += 1
        st.session_state.is_flipped = False

def prev_card():
    if st.session_state.current_card_index > 0:
        st.session_state.current_card_index -= 1
        st.session_state.is_flipped = False

def flip_card():
    st.session_state.is_flipped = not st.session_state.is_flipped

def fetch_decks() -> List[Dict[str, Any]]:
    try:
        with httpx.Client() as client:
            # hardcoded user id = 1, we don't have login/registration
            response = client.get(f"{API_URL}/decks/?user_id=1")
            if response.status_code == 200:
                decks = response.json()
            else:
                decks = []
                st.error("Failed to fetch decks.")
            return decks
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        return []

def load_cards(deck_id : int, deck_title : str):
    try:
        with httpx.Client() as client:
            res = client.get(f"{API_URL}/decks/{deck_id}/cards")
            if res.status_code == 200:
                st.session_state.cards = res.json()
                st.session_state.current_card_index = 0
                st.session_state.selected_deck_name = deck_title
                st.session_state.is_flipped = False
            else:
                st.error("Could not load cards for this deck.")
    except Exception as e:
        st.error(f"Error: {e}")

st.set_page_config(page_title="Study Deck", layout="centered")

# initialize Session State
if "cards" not in st.session_state:
    st.session_state.cards = []
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "is_flipped" not in st.session_state:
    st.session_state.is_flipped = False
if "selected_deck_name" not in st.session_state:
    st.session_state.selected_deck_name = ""

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
# except Exception as e:
#     st.error(f"Could not connect to backend: {e}")

decks = fetch_decks()

st.title("Study Decks", text_alignment="center")
if st.button("Generate Deck page"):
        st.switch_page("pages/1_Generate_Deck.py")

if not decks:
    st.info("No decks found. Go to 'Generate Deck' to create one 😌")
else:
    for deck in decks:
        with st.expander(f"📖 {deck['title']}"):
            st.write(f"Status: {deck['status']}")
            if st.button(f"View Cards: {deck['title']}", key=f"view_{deck['id']}"):
                load_cards(deck['id'], deck['title'])

# display flashcards
if st.session_state.cards:
    st.subheader(f"Deck: {st.session_state.selected_deck_name}", anchor=False)
    
    current_idx = st.session_state.current_card_index
    total_cards = len(st.session_state.cards)
    card = st.session_state.cards[current_idx]
    
    with st.container(border=True):
        st.markdown(f"<p style='text-align: center; color: gray;'>Card {current_idx + 1} of {total_cards}</p>", unsafe_allow_html=True)
        
        # flip the flashcard (front / back)
        display_text = card.get('back' if st.session_state.is_flipped else 'front', 
                                card.get('answer' if st.session_state.is_flipped else 'question'))
        
        st.markdown(f"<h2 style='text-align: center; min-height: 150px; display: flex; align-items: center; justify-content: center;'>{display_text}</h2>", unsafe_allow_html=True)
        
        st.button("🔄 Flip Card", on_click=flip_card, use_container_width=True)

    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        st.button("⬅️ Previous", on_click=prev_card, use_container_width=True, disabled=(current_idx == 0))
    with col_next:
        st.button("Next ➡️", on_click=next_card, use_container_width=True, disabled=(current_idx == total_cards - 1))