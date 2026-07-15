from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 테스트 및 즉시 구동을 위해 SQLite를 사용합니다. 
# TRD의 PostgreSQL 16 환경 적용 시 아래 주석을 해제하세요.
# DATABASE_URL = "postgresql://username:password@localhost:5432/contact_db"
DATABASE_URL = "sqlite:///./contact_service.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 의존성 주입을 위한 DB 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()