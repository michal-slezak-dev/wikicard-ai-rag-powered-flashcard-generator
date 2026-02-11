import streamlit as st
import httpx
import os

# API_URL = "http://0.0.0.0:8000"
API_URL = os.getenv("BACKEND_URL", "http://0.0.0.0:8000")

st.set_page_config(page_title="Study Session", layout="centered")

def fetch_study_queue():
    try:
        with httpx.Client() as client:
            res = client.get(f"{API_URL}/study/due?user_id=1")
            if res.status_code == 200:
                current_api_queue = res.json()

                if len(current_api_queue) != len(st.session_state.study_queue): # if new cards were added
                    st.session_state.study_queue = current_api_queue
                    st.session_state.current_card_index = 0
            else:
                st.error("Failed to load your flashcards.")
    except Exception as e:
        st.error(f"Connection error: {e}")

if "study_queue" not in st.session_state:
    st.session_state.study_queue = []
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "show_back" not in st.session_state:
    st.session_state.show_back = False

st.title("Study Session", text_alignment="center")

# load study queue if empty
if not st.session_state.study_queue:
    with st.spinner("Fetching due cards..."):
        # try:
        #     with httpx.Client() as client:
        #         res = client.get(f"{API_URL}/study/due?user_id=1")
        #         if res.status_code == 200:
        #             st.session_state.study_queue = res.json()
        #         else:
        #             st.error("Failed to load your flashcards.")
        # except Exception as e:
        #     st.error(f"Connection error: {e}")
        fetch_study_queue()

queue = st.session_state.study_queue
idx = st.session_state.current_card_index

if idx < len(queue):
    card = queue[idx]
    
    progress = (idx) / len(queue)
    st.progress(progress, text=f"Card {idx+1} of {len(queue)}")
    
    # flashcard UI
    st.markdown("---")
    st.markdown(f"### Q: {card['front']}")
    st.markdown("---")
    
    if st.session_state.show_back:
        st.markdown(f"### A: {card['back']}")
        st.markdown("---")
        
        st.write("How difficult was this review?")
        
        c1, c2, c3, c4 = st.columns(4)
        def submit_review(grade):
            try:
                with httpx.Client() as client:
                    client.post(f"{API_URL}/study/review", json={
                        "flashcard_id": card['id'],
                        "grade": grade
                    })

                # init next state
                st.session_state.show_back = False
                st.session_state.current_card_index += 1

                if st.session_state.current_card_index >= len(st.session_state.study_queue):
                    st.session_state.study_queue = []
                    st.session_state.current_card_index = 0
                #st.rerun()
            except Exception as e:
                st.error(f"Error submitting review: {e}")

        with c1:
            st.button("Total Blackout (0)", on_click=submit_review, args=(0,), use_container_width=True)
        with c2:
            st.button("Hard (3)", on_click=submit_review, args=(3,), use_container_width=True)
        with c3:
            st.button("Good (4)", on_click=submit_review, args=(4,), use_container_width=True)
        with c4:
            st.button("Easy (5)", on_click=submit_review, args=(5,), use_container_width=True)
            
    else:
        st.button("Show Answer", on_click=lambda: st.session_state.update({"show_back": True}), type="primary", use_container_width=True)

else:
    if st.session_state.study_queue: # if not empty in the beginning
        st.success("🎉 All caught up! Good job.")
        if st.button("Return Home"):
            
            # cleanup
            st.session_state.study_queue = []
            st.session_state.current_card_index = 0
            st.switch_page("Home.py")
    else:
        st.info("No cards due right now. Go generate some new decks!")
