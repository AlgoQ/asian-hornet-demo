from models import *
from database import engine

def create_tables():
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully")
