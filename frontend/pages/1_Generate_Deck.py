import streamlit as st
import httpx
import pandas as pd
import os

# API_URL = "http://0.0.0.0:8000"
API_URL = os.getenv("BACKEND_URL", "http://0.0.0.0:8000")

st.set_page_config(page_title="Generate Deck from Wikipedia", layout="wide")

def generate_deck():
    try:
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{API_URL}/decks/generate",
                json={"url": url_input, "user_id": 1}
                )
            if response.status_code == 200:
                st.session_state.generated_deck = response.json()
                st.success("Flashcards generated successfully!")
            else:
                st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")

def save_deck():
    try:
        with httpx.Client() as client:
            res = client.post(f"{API_URL}/decks/{deck['id']}/save")
            if res.status_code == 200:
                st.success("Deck saved to your library!")
                st.session_state.generated_deck = None
                st.rerun()
            else:
                st.error("Failed to save your deck.")
    except Exception as e:
        st.error(str(e))

def discard_deck():
    try:
        with httpx.Client() as client:
            client.post(f"{API_URL}/decks/{deck['id']}/discard")
            st.session_state.generated_deck = None
            st.info("Deck discarded.")
            st.rerun()
    except Exception as e:
        st.error(str(e))

st.title("Generate Flashcards", text_alignment="center")
st.markdown("Enter a Wikipedia URL to create a new flashcard deck using AI.", text_alignment="center")

# initialize session state for generated deck
if "generated_deck" not in st.session_state:
    st.session_state.generated_deck = None

url_input = st.text_input("Wikipedia URL", placeholder="https://en.wikipedia.org/wiki/Spaced_repetition")

if st.button("Generate Flashcards", type="primary"):
    if not url_input:
        st.warning("Please enter a URL.")
    elif "wikipedia.org" not in url_input:
        st.warning("Please enter a valid Wikipedia URL!")
    else:
        with st.spinner("Analyzing text, indexing knowledge, and generating your flashcards... This might take a minute 😉"):
            # try:
            #     with httpx.Client(timeout=300.0) as client:
            #         response = client.post(
            #             f"{API_URL}/decks/generate",
            #             json={"url": url_input, "user_id": 1}
            #         )
            #         if response.status_code == 200:
            #             st.session_state.generated_deck = response.json()
            #             st.success("Flashcards generated successfully!")
            #         else:
            #             st.error(f"Error: {response.text}")
            # except Exception as e:
            #     st.error(f"Connection error: {e}")
            generate_deck()

# display generated content
if st.session_state.generated_deck:
    deck = st.session_state.generated_deck
    st.subheader(f"Review: {deck['title']}")
    
    # show flashcards in a table/expanders
    cards = deck['flashcards']
    
    for i, card in enumerate(cards):
        with st.expander(f"Card {i + 1}: {card['front']}"):
            st.markdown(f"**Q:** {card['front']}")
            st.markdown(f"**A:** {card['back']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Deck", use_container_width=True):
            # try:
            #     with httpx.Client() as client:
            #         res = client.post(f"{API_URL}/decks/{deck['id']}/save")
            #         if res.status_code == 200:
            #             st.success("Deck saved to your library!")
            #             st.session_state.generated_deck = None
            #             st.rerun()
            #         else:
            #             st.error("Failed to save your deck.")
            # except Exception as e:
            #     st.error(str(e))
            save_deck()
                
    with col2:
        if st.button("Discard", use_container_width=True):
            # try:
            #     with httpx.Client() as client:
            #         client.post(f"{API_URL}/decks/{deck['id']}/discard")
            #         st.session_state.generated_deck = None
            #         st.info("Deck discarded.")
            #         st.rerun()
            # except Exception as e:
            #     st.error(str(e))
            discard_deck()
