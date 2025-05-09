from datetime import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, SmallInteger


SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(os.path.dirname(__file__), "tips.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Tip(Base):
    __tablename__ = "tips"
    id = Column(Integer, primary_key=True, autoincrement=True)
    faiss_index = Column(Integer)
    type = Column(String)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class SimilarTip(Base):
    __tablename__ = "similar_tips"
    id = Column(Integer, primary_key=True, autoincrement=True)
    faiss_index = Column(Integer)
    type = Column(String)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)

def create_tip(faiss_index: int, tip_type: str, text: str) -> Tip:
    """
    Create and store a new Tip in the database.
    
    Args:
        faiss_index: The FAISS index for the tip
        tip_type: The type of the tip
        text: The content of the tip
    
    Returns:
        The created Tip object
    """
    db = SessionLocal()
    tip = Tip(faiss_index=faiss_index, type=tip_type, text=text)
    db.add(tip)
    db.commit()
    db.refresh(tip)
    db.close()
    return tip

def create_similar_tip(faiss_index: int, tip_type: str, text: str) -> SimilarTip:
    """
    Create and store a new SimilarTip in the database.
    
    Args:
        faiss_index: The FAISS index for the tip
        tip_type: The type of the tip
        text: The content of the tip
    
    Returns:
        The created SimilarTip object
    """
    db = SessionLocal()
    similar_tip = SimilarTip(faiss_index=faiss_index, type=tip_type, text=text)
    db.add(similar_tip)
    db.commit()
    db.refresh(similar_tip)
    db.close()
    return similar_tip