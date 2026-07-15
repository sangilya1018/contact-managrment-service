# 파이썬 3.11 버전의 가벼운 환경을 사용해요
FROM python:3.11-slim

# 이 상자 안의 /app 폴더를 작업 공간으로 정해요
WORKDIR /app

# 아까 만든 준비물 목록을 상자 안으로 복사하고 설치해요
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 이제 내 컴퓨터의 나머지 코드들을 상자 안으로 다 가져와요
COPY . .

# 8000번 포트를 열어둘게요
EXPOSE 8000

# 프로그램이 시작되게 하는 명령어예요
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]