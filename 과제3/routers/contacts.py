from fastapi import APIRouter, Depends, HTTPException, Cookie, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, crud

router = APIRouter(prefix="/contacts", tags=["contacts"])

def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    if not session_id:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")
    user = crud.get_user_by_session(db, session_id)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")
    return user

@router.post("/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact_in: schemas.ContactCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # TRD 5-2 검증 사양: 요청 본문의 category_id가 현재 유저 소유의 범위인지 검증
    cat = db.query(models.Category).filter(
        models.Category.id == contact_in.category_id, 
        models.Category.user_id == current_user.id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="존재하지 않거나 접근 권한이 없는 카테고리입니다.")
        
    # 동일 유저 내 전화번호 중복 검증
    dup = db.query(models.Contact).filter(
        models.Contact.user_id == current_user.id, 
        models.Contact.phone == contact_in.phone
    ).first()
    if dup:
        raise HTTPException(status_code=409, detail="이미 등록된 전화번호입니다.")
        
    db_contact = models.Contact(
        user_id=current_user.id,
        category_id=contact_in.category_id,
        name=contact_in.name,
        phone=contact_in.phone,
        addr=contact_in.addr
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.get("/", response_model=List[schemas.ContactResponse])
def list_contacts(
    name: Optional[str] = Query(None), 
    category_id: Optional[int] = Query(None),
    current_user=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    query = db.query(models.Contact).filter(models.Contact.user_id == current_user.id)
    # TRD 5-2 사양: 동적 쿼리 필터링(부분 이름 검색 및 카테고리 필터)
    if name:
        query = query.filter(models.Contact.name.contains(name))
    if category_id:
        query = query.filter(models.Contact.category_id == category_id)
    return query.all()

@router.patch("/{id}", response_model=schemas.ContactResponse)
def update_contact(id: int, contact_in: schemas.ContactUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == id).first()
    # TRD 5-2 사양: 타 유저 오접근 시 데이터 유출 방지를 위해 404 처리 위장
    if not contact or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="존재하지 않거나 접근 권한이 없는 리소스입니다.")
        
    if contact_in.category_id is not None:
        cat = db.query(models.Category).filter(
            models.Category.id == contact_in.category_id, 
            models.Category.user_id == current_user.id
        ).first()
        if not cat:
            raise HTTPException(status_code=404, detail="존재하지 않거나 접근 권한이 없는 카테고리입니다.")
        contact.category_id = contact_in.category_id

    if contact_in.phone is not None:
        dup = db.query(models.Contact).filter(
            models.Contact.user_id == current_user.id, 
            models.Contact.phone == contact_in.phone,
            models.Contact.id != id
        ).first()
        if dup:
            raise HTTPException(status_code=409, detail="이미 등록된 전화번호입니다.")
        contact.phone = contact_in.phone

    if contact_in.name is not None:
        contact.name = contact_in.name
    if contact_in.addr is not None:
        contact.addr = contact_in.addr

    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{id}")
def delete_contact(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == id).first()
    # TRD 5-2 사양: 타 유저 오접근 시 데이터 유출 방지를 위해 404 처리 위장
    if not contact or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="존재하지 않거나 접근 권한이 없는 리소스입니다.")
    
    db.delete(contact)
    db.commit()
    return {"message": "연락처가 성공적으로 삭제되었습니다."}