from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal, Poll, Option
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from .security import create_access_token, get_current_user, get_current_admin

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# 정적 파일 마운트 경로 수정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    polls = db.query(Poll).all()
    for poll in polls:
        poll.total_votes = sum(option.votes for option in poll.options)
    return templates.TemplateResponse("index.html", {"request": request, "polls": polls})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "next": next}
    )

@app.get("/vote/{poll_id}")
def vote(request: Request, poll_id: int, db: Session = Depends(get_db)):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=404,
            detail="해당 투표를 찾을 수 없습니다"
        )
    return templates.TemplateResponse("vote.html", {"request": request, "poll": poll})

@app.post("/vote/{poll_id}")
async def submit_vote(
    poll_id: int,
    option_id: int = Form(...),
    db: Session = Depends(get_db)
):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=404,
            detail="해당 투표를 찾을 수 없습니다"
        )
    
    option = db.query(Option).filter(Option.id == option_id).first()
    if not option or option.poll_id != poll_id:
        raise HTTPException(
            status_code=400,
            detail="유효하지 않은 투표 항목입니다"
        )
    
    option.votes += 1
    db.commit()
    return RedirectResponse(url=f"/vote/{poll_id}", status_code=303)

# 로그인 엔드포인트
@app.post("/token")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    next: str = Form("/")
):
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=400,
            detail="잘못된 사용자명 또는 비밀번호입니다"
        )
    
    access_token = create_access_token(
        data={"sub": form_data.username}
    )
    response = RedirectResponse(url=next, status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request.url.path.split("/")[-1] + ".html" if request.url.path != "/" else "create_poll.html",
        {
            "request": request,
            "error": exc.detail
        },
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request.url.path.split("/")[-1] + ".html" if request.url.path != "/" else "create_poll.html",
        {
            "request": request,
            "error": "처리 중 오류가 발생했습니다"
        },
        status_code=500
    )

@app.get("/admin")
async def admin_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin)
):
    polls = db.query(Poll).all()
    return templates.TemplateResponse("admin.html", {"request": request, "polls": polls})

@app.post("/admin/polls")
async def create_poll(
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin)
):
    form = await request.form()
    title = form.get("title")
    options = form.getlist("options[]")
    
    if not title or not options:
        raise HTTPException(status_code=400, detail="제목과 옵션은 필수입니다")
    
    try:
        poll = Poll(title=title)
        db.add(poll)
        db.commit()
        db.refresh(poll)
        
        for option_text in options:
            if option_text.strip():
                option = Option(text=option_text, poll_id=poll.id)
                db.add(option)
        db.commit()
        
        return RedirectResponse(url="/admin", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/polls/{poll_id}/delete")
async def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin)
):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="투표를 찾을 수 없습니다")
    
    db.delete(poll)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/api/polls")
async def get_polls(db: Session = Depends(get_db)):
    polls = db.query(Poll).all()
    polls_data = []
    
    for poll in polls:
        total_votes = sum(option.votes for option in poll.options)
        options_data = [{"text": opt.text, "votes": opt.votes} for opt in poll.options]
        
        polls_data.append({
            "id": poll.id,
            "title": poll.title,
            "options": options_data,
            "total_votes": total_votes
        })
    
    return JSONResponse(content=polls_data)

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response