from app import create_app
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 