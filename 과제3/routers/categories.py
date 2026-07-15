from fastapi import APIRouter, Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas, crud

router = APIRouter(prefix="/categories", tags=["categories"])

def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    if not session_id:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")
    user = crud.get_user_by_session(db, session_id)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")
    return user

@router.post("/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_in: schemas.CategoryCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # 중복 체크
    dup = db.query(models.Category).filter(
        models.Category.user_id == current_user.id, 
        models.Category.name == category_in.name
    ).first()
    if dup:
        raise HTTPException(status_code=409, detail="이미 등록된 카테고리명입니다.")
    
    db_cat = models.Category(user_id=current_user.id, name=category_in.name)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.get("/", response_model=List[schemas.CategoryResponse])
def list_categories(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Category).filter(models.Category.user_id == current_user.id).all()

@router.patch("/{id}", response_model=schemas.CategoryResponse)
def update_category(id: int, category_in: schemas.CategoryCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    cat = db.query(models.Category).filter(models.Category.id == id).first()
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="존재하지 않거나 접근 권한이 없는 리소스입니다.")
    
    dup = db.query(models.Category).filter(
        models.Category.user_id == current_user.id, 
        models.Category.name == category_in.name,
        models.Category.id != id
    ).first()
    if dup:
        raise HTTPException(status_code=409, detail="이미 등록된 카테고리명입니다.")
        
    cat.name = category_in.name
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{id}")
def delete_category(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    cat = db.query(models.Category).filter(models.Category.id == id).first()
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="존재하지 않거나 접근 권한이 없는 리소스입니다.")
    
    # TRD 4 사양 (무결성 보호 제약): 해당 카테고리를 사용하는 연락처가 존재하면 삭제 강제 거절
    contact_count = db.query(models.Contact).filter(models.Contact.category_id == id).count()
    if contact_count > 0:
        raise HTTPException(
            status_code=409, 
            detail=f"해당 카테고리를 사용하는 연락처가 [{contact_count}]건 존재하여 삭제할 수 없습니다."
        )
    
    db.delete(cat)
    db.commit()
    return {"message": "카테고리가 성공적으로 삭제되었습니다."}