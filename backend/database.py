from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import os
# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

data_dir = "data" if os.path.exists("data") else "."
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{os.path.join(data_dir, sqlite_file_name)}"

connect_args = {"check_same_thread": False} # allows multiple threads to access the db at the time
engine = create_engine(sqlite_url, connect_args=connect_args)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_Session():
    with Session(engine) as session:
        yield session
