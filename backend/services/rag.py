from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os

class FlashcardSchema(BaseModel):
    front : str = Field(description="This is the front of the flashcard (question)")
    back : str = Field(description="This is the back of the flashcard (answer)")

class FlashcardDeckSchema(BaseModel):
    cards : List[FlashcardSchema] = Field(description="This is our list of 5 flashcards")

class RAGService:
    def __init__(self, persist_directory : str = "./chroma_db", model_name : str = 'llama3.1'):
        self.model_name = model_name
        self.persist_directory = persist_directory

        # Initialize embedding and LLM
        self.embedding_function = OllamaEmbeddings(model=self.model_name)
        self.llm = ChatOllama(model=self.model_name, temperature=0.1)

    def scrape_and_load(self, url : str) -> List[Any]:
        """Scrapes and loads the content of our Wikipedia page"""
        if "wikipedia.org" not in url:
            raise ValueError("URL must be from wikipedia.org")
        
        os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"
        
        try:
            loader = WebBaseLoader(web_paths=(url,))

            docs = loader.load()
            return docs
        except Exception as e:
            raise ValueError(f"Could not load the URL: {url}. Error {e}")
    
    def chunk_documents(self, docs : List[Any], chunk_size : int = 1000, chunk_overlap : int = 200) -> List[Any]:
        """Divides the conent of our Wikipedia page into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        splits = text_splitter.split_documents(docs)
        return splits
    
    def index_documents(self, chunks : List[Any], collection_name : str) -> Chroma: # vectorization
        """Vectorizes our chunks"""

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_function,
            collection_name=collection_name,
            persist_directory=self.persist_directory
        )

        return vector_store

    def generate_flashcards(self, collection_name : str, topic : str = "Create 10 flashcards about this wikipedia page") -> List[Dict[str, str]]:
            """Generates our flashcards utilizing RAG
                Retrieves context from our vectordb and prompts the LLM
            """
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_function,
                persist_directory=self.persist_directory
            )

            retriever = vector_store.as_retriever(search_kwargs = {'k': 12}) # top 12 answers, the closest
            context_docs = retriever.invoke(f"important facts, key definitions, concepts, summary about {topic}")
            context_text = format_docs(context_docs)

            parser = JsonOutputParser(pydantic_object=FlashcardDeckSchema)
            
            # template = """
            #         ROLE:
            #         You are an academic knowledge assistant. Your mission is to transform raw text (Wikipedia data) into high-quality pedagogical materials (flashcards).

            #         TASK:
            #         Analyze the provided context and generate flashcards optimized for spaced repetition based on the user's request. Everytime, try to generate different flashcards.

            #         GOALS:
            #         1. Extract core definitions, core information, and scientific concepts.
            #         2. Focus on single, atomic facts for better memory retention.
            #         3. Use precise, objective academic language.
            #         4. Output strictly as a JSON object following the format instructions below.

            #         CONTEXT (SOURCE MATERIAL):
            #         {context}

            #         RULES:
            #         - Do NOT add information that is not present in the CONTEXT documents.
            #         - IGNORE metadata like edit dates, licensing info, or source citations, etc.
            #         - If facts are missing, do not invent information.
            #         - NO conversational fillers (e.g., {{"Here are your flashcards"}} etc.). Output ONLY the JSON.

            #         FORMAT INSTRUCTIONS:
            #         {format_instructions}

            #         USER REQUEST:
            #         {topic}
            #         """
            # prompt = ChatPromptTemplate.from_template(template)

            prompt = ChatPromptTemplate.from_messages([
                (
                    "system", """
                    ROLE:
                    You are an academic knowledge assistant. Your mission is to transform raw text (Wikipedia data) into high-quality pedagogical materials (flashcards).

                    GOALS:
                    1. Extract 5 most fundamental facts: core definitions, core information, and scientific concepts.
                    2. Focus on single, atomic facts for better memory retention.
                    3. Use the "Minimum Information Principle": each card must be brief and focus on ONE specific piece of information.
                    4. Front should be a clear question, Back should be a concise answer.
                    5. Use precise, objective academic language.
                    6. Output strictly as a JSON object following the format instructions below.

                    RULES:
                    - Do NOT add information that is not present in the CONTEXT documents.
                    - IGNORE metadata like edit dates, licensing info, or source citations, etc.
                    - If facts are missing, do not invent information.
                    - NO conversational fillers (e.g., {{"Here are your flashcards"}} etc.). Output ONLY the JSON.

                    FORMAT INSTRUCTIONS:
                    {format_instructions}
                """),
                ("user","""
                    TASK:
                    Analyze the provided context and generate flashcards optimized for spaced repetition based on the user's request. Everytime, try to generate different flashcards.
                 
                    CONTEXT (SOURCE MATERIAL):
                    {context}

                    USER REQUEST:
                    {topic}
                """)
            ])

            chain = prompt | self.llm | parser

            try:
                response = chain.invoke({
                    'context' : context_text,
                    'topic' : topic,
                    'format_instructions' : parser.get_format_instructions()
                })

                return response.get('cards', [])
            except Exception as e:
                print(f'Error when generating flashcards : {e}')
                return []
            
    def delete_collection(self, collection_name : str):
        """Cleans up our vector_store collection"""
        try:
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_function,
                persist_directory=self.persist_directory
            )

            vector_store.delete_collection()
            print(f"Collection {collection_name} successfully deleted")
        except Exception as e:
            print(f"Failed to delete the collection / the collection does not exist: {e}")


    def process_and_ask(self, url: str) -> List[Dict[str, str]]:
        """Test function - testing the workflow"""
        collection_name = "wiki_data"
        
        print(f"Loading {url}...")
        docs = self.scrape_and_load(url)
        
        chunks = self.chunk_documents(docs)
        
        print("Indexing...")
        self.index_documents(chunks, collection_name)
        
        print("Generating flashcards...")
        flashcards = self.generate_flashcards(collection_name)
        
        return flashcards
