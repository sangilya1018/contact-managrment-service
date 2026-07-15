import secrets
from sqlalchemy.orm import Session
import models, schemas, security

# --- 세션 처리 의존성용 함수 ---
def get_user_by_session(db: Session, session_id: str):
    db_session = db.query(models.Session).filter(models.Session.session_id == session_id).first()
    if db_session:
        return db.query(models.User).filter(models.User.id == db_session.user_id).first()
    return None

# --- 회원 인증 비즈니스 로직 ---
def create_user(db: Session, user_data: schemas.UserSignUp):
    hashed_pwd = security.get_password_hash(user_data.password)
    db_user = models.User(username=user_data.username, password_hash=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # TRD 5-1 사양: 회원가입 성공 시 기본 카테고리 시드 데이터 3종(가족, 친구, 기타) 자동 생성
    seed_categories = ["가족", "친구", "기타"]
    for cat_name in seed_categories:
        db_cat = models.Category(user_id=db_user.id, name=cat_name)
        db.add(db_cat)
    db.commit()
    return db_user

def create_session(db: Session, user_id: int) -> str:
    # TRD 3-1 사양: secrets.token_hex(32) 기반 무작위 64자 암호학적 세션 생성
    session_id = secrets.token_hex(32)
    db_session = models.Session(session_id=session_id, user_id=user_id)
    db.add(db_session)
    db.commit()
    return session_id

def delete_session(db: Session, session_id: str):
    db_session = db.query(models.Session).filter(models.Session.session_id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False