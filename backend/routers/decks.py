from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel

from database import get_Session
from models import Deck, Flashcard, DeckStatus, User
from services.rag import RAGService

router = APIRouter(prefix="/decks", tags=["decks"])
rag_service = RAGService()

class GenerateRequest(BaseModel):
    url: str
    user_id: int

class DeckResponse(BaseModel):
    id: int
    title: str
    status: str
    flashcards: List[dict]

@router.post("/generate", response_model=DeckResponse)
def generate_deck(request: GenerateRequest, session: Session = Depends(get_Session)):
    # create a draft deck
    # TODO: later - fetch real title from URL or scrape it
    deck = Deck(
        title=f"Draft from {request.url}",
        description=f"Generated from {request.url}",
        user_id=request.user_id,
        status=DeckStatus.DRAFT
    )
    session.add(deck)
    session.commit()
    session.refresh(deck)
    

    try:
        docs = rag_service.scrape_and_load(request.url)
        wiki_title = docs[0].metadata.get('title', 'Wikipedia Page').strip()

        chunks = rag_service.chunk_documents(docs)
        collection_name = f"deck_{deck.id}"
        
        # topic = "the content" 
        
        # index
        rag_service.index_documents(chunks, collection_name)
        
        # generate
        generated_cards = rag_service.generate_flashcards(collection_name, topic=f"Create 10 flashcards about {wiki_title}")
        
        # save our flashcard to db
        created_cards = []
        for card in generated_cards:
            flashcard = Flashcard(
                front=card.get("front", "Error"),
                back=card.get("back", "Error"),
                deck_id=deck.id,

                # SM-2 default vals
                easiness_factor=2.5,
                interval=0,
                repetitions=0
            )
            session.add(flashcard)
            created_cards.append(flashcard)
            
        session.commit()
        
        # chroma db cleanup
        rag_service.delete_collection(collection_name)
        
        return {
            "id": deck.id,
            "title": deck.title,
            "status": deck.status,
            "flashcards": [{"front": c.front, "back": c.back, "id": c.id} for c in created_cards]
        }
        
    except Exception as e:
        # cleanup if sth failed
        session.delete(deck)
        session.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{deck_id}/save")
def save_deck(deck_id: int, session: Session = Depends(get_Session)):
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    deck.status = DeckStatus.ACTIVE
    session.add(deck)
    session.commit()
    return {"status": "success", "deck_status": deck.status}

@router.post("/{deck_id}/discard")
def discard_deck(deck_id: int, session: Session = Depends(get_Session)):
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    deck.status = DeckStatus.ARCHIVED
    session.add(deck)
    session.commit()

    # session.delete(deck)
    # session.commit()
    return {"status": "success", "deck_status": deck.status}

@router.get("/", response_model=List[Deck])
def list_decks(user_id: int, session: Session = Depends(get_Session)):
    statement = select(Deck).where(Deck.user_id == user_id, Deck.status == DeckStatus.ACTIVE)
    decks = session.exec(statement).all()
    return decks

@router.get("/{deck_id}/cards", response_model=List[Flashcard])
def get_deck_cards(deck_id : int, session : Session = Depends(get_Session)):
    deck = session.get(Deck, deck_id)

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    return deck.flashcards

@router.delete("/{deck_id}")
def delete_deck(deck_id: int, session: Session = Depends(get_Session)):
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    session.delete(deck)
    session.commit()

    return {"message": f"Deck: {deck_id} and all related data deleted successfully"}
