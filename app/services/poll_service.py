from sqlalchemy.orm import Session
from typing import List
from app.models.poll import Poll, Option

class PollService:
    @staticmethod
    def get_all_polls(db: Session):
        return db.query(Poll).all()
    
    @staticmethod
    def create_poll(db: Session, title: str, options: List[str]):
        poll = Poll(title=title)
        db.add(poll)
        db.commit()
        db.refresh(poll)
        
        for option_text in options:
            if option_text.strip():
                option = Option(text=option_text, poll_id=poll.id)
                db.add(option)
        db.commit()
        return poll

    @staticmethod
    def get_poll(db: Session, poll_id: int):
        return db.query(Poll).filter(Poll.id == poll_id).first()

    @staticmethod
    def submit_vote(db: Session, option_id: int):
        option = db.query(Option).filter(Option.id == option_id).first()
        option.votes += 1
        db.commit()
        return option 