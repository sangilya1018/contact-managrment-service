from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, crud, security

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: schemas.UserSignUp, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="이미 존재하는 아이디입니다.")
    crud.create_user(db, user_data)
    return {"message": "회원가입이 완료되었으며 기본 카테고리가 생성되었습니다."}

@router.post("/login")
def login(user_data: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user or not security.verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호가 일치하지 않습니다.")
    
    session_id = crud.create_session(db, user.id)
    # TRD 3-1 규격: HTTP 응답 Set-Cookie 헤더에 session_id 주입
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return {"message": "로그인 성공"}

@router.get("/me", response_model=schemas.UserResponse)
def get_me(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    if not session_id:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")
    user = crud.get_user_by_session(db, session_id)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")
    return user

@router.post("/logout")
def logout(response: Response, session_id: str = Cookie(None), db: Session = Depends(get_db)):
    if session_id:
        crud.delete_session(db, session_id)
    response.delete_cookie("session_id")
    return {"message": "로그아웃 성공"}