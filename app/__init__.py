from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.poll_routes import router
from app.database.connection import engine
from app.models.poll import Base

def create_app():
    app = FastAPI()
    
    # 데이터베이스 초기화
    Base.metadata.create_all(bind=engine)
    
    # 정적 파일 설정
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 라우터 등록
    app.include_router(router)
    
    return app 