from fastapi import Request, Depends, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from app.services.poll_service import PollService
from app.db.connection import get_db

templates = Jinja2Templates(directory="templates")

class PollController:
    def __init__(self):
        self.service = PollService()

    def home(self, request: Request, db: Session = Depends(get_db)):
        polls = self.service.get_all_polls(db)
        return templates.TemplateResponse(
            "create_poll.html",
            {"request": request, "polls": polls}
        )

    async def create_poll(
        self,
        request: Request,
        title: str = Form(...),
        options: List[str] = Form(...),
        db: Session = Depends(get_db)
    ):
        self.service.create_poll(db, title, options)
        return {"url": "/", "status_code": 303}

    def vote(self, request: Request, poll_id: int, db: Session = Depends(get_db)):
        poll = self.service.get_poll(db, poll_id)
        return templates.TemplateResponse(
            "vote.html",
            {"request": request, "poll": poll}
        )

    async def submit_vote(
        self,
        poll_id: int,
        option_id: int = Form(...),
        db: Session = Depends(get_db)
    ):
        self.service.submit_vote(db, option_id)
        return {"url": f"/vote/{poll_id}", "status_code": 303} 