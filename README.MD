# WikiCard AI – RAG-Powered Flashcard Generator
**Final Project for Functional Programming Languages (PJF)**  
**Author:** Michał Ślęzak, WCY23IJ2S1, nr albumu 860 65  
**Lab Instructor:** mgr inż. Piotr Bączyk  

WikiCard AI is an application that generates educational flashcards based on Wikipedia pages. It utilizes RAG (Retrieval-Augmented Generation) to retrieve key text fragments and create high-quality flashcards. Additionally, the SM-2 algorithm optimizes the learning process through spaced repetition by calculating the optimal interval between review sessions.

---
## Features
- **RAG Pipeline:** Automated content extraction from Wikipedia URLs, chunking, indexing into ChromaDB, and flashcard generation via an LLM.
- **Vector Database:** ChromaDB for semantic context retrieval.
- **Persistent Storage:** SQLite for saving flashcard decks, tracking learning progress, and managing decks (deletion).
- **SM-2 Repetition System:** Calculates review intervals and the ease factor based on the user's rating of a specific flashcard.
---

## Tech Stack
| Category | Technologies |
|-----------|-------------|
| **Language** | Python 3.13.9 |
| **Backend** | FastAPI |
| **Frontend** | Streamlit |
| **AI** | LangChain, Meta Llama 3.1 (Ollama) |
| **Vector Database** | ChromaDB |
| **Database** | SQLite |
| **Containerization** | Docker |
---

## How it works
### RAG Pipeline
1. **Ingestion:** Extracting HTML content from Wikipedia.
2. **Indexing:**Splitting text into chunks and vectorization.
3. **Storage:** Saving embeddings to ChromaDB.
4. **Retrieval + Generation:** Searching for similar chunks and generating flashcards in JSON format using the Llama 3.1 model.

### SM-2 Algorithm
Updates the following metrics based on the user's flashcard rating:
- **Easiness Factor (EF)**
- **Interval** (days until next review)
- **Repetitions** (success counter)
---

## Uruchomienie
### Prerequisites
- Ollama z modelem: `ollama pull llama3.1`
- Python 3.13.9+

### Getting Started
```bash
git clone https://github.com/michal-slezak-dev/wikicard-ai-rag-powered-flashcard-generator.git
cd wikicard-ai-rag-powered-flashcard-generator
conda env create -f environment.yml
conda activate rag-flashcard-generation-env
```

### Start
Run the following commands from the project's root directory wikicard-ai-rag-powered-flashcard-generator using two separate terminals.

Terminal 1 - backend:
```bash
cd backend
uvicorn main:app --reload
```

Terminal 2 - frontend:
```bash
streamlit run frontend/Home.py
```
