from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session
from models import User
from database import create_db_and_tables, engine
from routers import decks, study

def create_default_user():
    with Session(engine) as session:
        try:
            user = session.get(User, 1)
            if not user:
                test_user = User(
                    id=1, 
                    username="admin",   
                    email="admin@test.com"
                )
                session.add(test_user)
                session.commit()
        except Exception as e:
            print(f"Error when creating default user: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    create_default_user()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the WikiCard AI - RAG-Powered Flashcard Generation App API"}

app.include_router(decks.router)
app.include_router(study.router)
