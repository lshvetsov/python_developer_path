from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Flashcard(Base):
    __tablename__ = 'flashcard'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    box = Column(Integer)