# Contact Management Web Service

FastAPI로 구현된 사용자 기반 연락처 관리 웹 서비스입니다. 사용자별로 카테고리를 구분하여 연락처를 관리할 수 있습니다.

## 주요 기능

### 인증 (Authentication)
- **회원가입**: 새로운 사용자 계정 생성 (`POST /auth/signup`)
- **로그인**: 사용자 인증 및 세션 생성 (`POST /auth/login`)
- **로그아웃**: 세션 삭제 (`POST /auth/logout`)
- **현재 사용자 조회**: 로그인된 사용자 정보 조회 (`GET /auth/me`)
- 세션 기반 인증 (Cookie 사용)

### 카테고리 관리 (Categories)
- **생성**: 새로운 카테고리 추가 (`POST /categories/`)
- **조회**: 사용자의 모든 카테고리 조회 (`GET /categories/`)
- **수정**: 카테고리명 변경 (`PATCH /categories/{id}`)
- **삭제**: 카테고리 삭제 (사용 중인 연락처가 없을 때만)
- 사용자별 카테고리명 중복 방지

### 연락처 관리 (Contacts)
- **생성**: 새로운 연락처 추가 (`POST /contacts/`)
- **조회**: 전체/필터링된 연락처 조회 (`GET /contacts/`)
  - 이름으로 부분 검색 지원
  - 카테고리별 필터링 지원
- **수정**: 연락처 정보 수정 (`PATCH /contacts/{id}`)
- **삭제**: 연락처 삭제 (`DELETE /contacts/{id}`)
- 사용자별 전화번호 중복 방지
- 전화번호 형식 검증 (010으로 시작하는 11자리)

### 미디어 스트리밍
- **동영상 스트리밍**: HTTP Range 지원 (`GET /video/stream`)
- **웹 UI**: 정적 파일 서빙

## 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite (기본) / PostgreSQL 16 (프로덕션 환경)
- **ORM**: SQLAlchemy
- **Server**: Uvicorn
- **Password Hashing**: pwdlib (Argon2)
- **Validation**: Pydantic

## 프로젝트 구조

```
과제3/
├── main.py                 # 애플리케이션 진입점
├── models.py              # SQLAlchemy ORM 모델 (User, Session, Category, Contact)
├── schemas.py             # Pydantic 스키마 (요청/응답 데이터 정의)
├── database.py            # 데이터베이스 설정 및 세션 관리
├── crud.py                # CRUD 작업 함수
├── security.py            # 보안 관련 함수 (비밀번호 해싱/검증)
├── routers/
│   ├── auth.py           # 인증 라우터
│   ├── categories.py     # 카테고리 관리 라우터
│   └── contacts.py       # 연락처 관리 라우터
├── static/               # 정적 파일
│   ├── bg_video.mp4
│   ├── bg_dashboard.mp4
│   └── dashboard.html
├── index.html            # 웹 UI 진입점
├── requirements.txt      # 의존성 목록
├── Dockerfile            # Docker 이미지 빌드 설정
└── contact_service.db    # SQLite 데이터베이스 (자동 생성)
```

## 시작하기

### 필수 요구사항
- Python 3.11 이상
- pip

### 설치 및 실행

1. 의존성 설치
```bash
pip install -r requirements.txt
```

2. 애플리케이션 시작
```bash
python main.py
```

3. 웹 브라우저에서 접속
```
http://localhost:8000
```

## Docker 배포

1. Docker 이미지 빌드
```bash
docker build -t contact-service .
```

2. Docker 컨테이너 실행
```bash
docker run -p 8000:8000 contact-service
```

## API 문서

서버 실행 후 다음 URL에서 API 문서 확인 가능:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 데이터베이스 모델

### User
- `id` (PK): 사용자 ID
- `username`: 사용자명 (고유)
- `password_hash`: 암호화된 비밀번호
- `created_at`: 생성 시간

### Session
- `session_id` (PK): 세션 ID
- `user_id` (FK): 사용자 ID
- `created_at`: 생성 시간

### Category
- `id` (PK): 카테고리 ID
- `user_id` (FK): 사용자 ID
- `name`: 카테고리명 (사용자별 고유)

### Contact
- `id` (PK): 연락처 ID
- `user_id` (FK): 사용자 ID
- `category_id` (FK): 카테고리 ID
- `name`: 연락처명 (최대 5자)
- `phone`: 전화번호 (010으로 시작하는 11자리, 사용자별 고유)
- `addr`: 주소 (선택사항)

## 보안 기능

- 세션 기반 인증 (HttpOnly Cookie)
- 비밀번호 Argon2 해싱
- 사용자별 데이터 격리
- 접근 권한 검증 (타 사용자 데이터 접근 방지)
- 전화번호 형식 검증

## 프로덕션 환경 설정

PostgreSQL 사용 시 `database.py`의 주석 처리된 부분을 활성화:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/contact_db"
```

## 라이선스

미정
