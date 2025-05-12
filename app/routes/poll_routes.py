from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.controllers.poll_controller import PollController

router = APIRouter()
controller = PollController()

@router.get("/")
async def home(request, db):
    return await controller.home(request, db)

@router.post("/create_poll")
async def create_poll(request, title, options, db):
    result = await controller.create_poll(request, title, options, db)
    return RedirectResponse(url=result["url"], status_code=result["status_code"])

@router.get("/vote/{poll_id}")
async def vote(request, poll_id: int, db):
    return await controller.vote(request, poll_id, db)

@router.post("/vote/{poll_id}")
async def submit_vote(poll_id: int, option_id: int, db):
    result = await controller.submit_vote(poll_id, option_id, db)
    return RedirectResponse(url=result["url"], status_code=result["status_code"]) 