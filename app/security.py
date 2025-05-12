from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

# 보안 설정
SECRET_KEY = "your-secret-key"  # 실제로는 환경변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(access_token: Optional[str] = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    
    try:
        # "Bearer " 제거
        token = access_token.split("Bearer ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
        return username
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

async def get_current_admin(current_user: str = Depends(get_current_user)):
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return current_user 