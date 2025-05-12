from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    options = relationship("Option", back_populates="poll")

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    votes = Column(Integer, default=0)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    poll = relationship("Poll", back_populates="options") 