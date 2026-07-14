from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import models
from database import engine
from routers import auth, categories, contacts
import os

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contact Management Web Service")

# 1. 라우터 등록
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(contacts.router)

# 2. 정적 파일 서빙 설정 (html=True 제거)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. ROOT 경로 설정 (가장 중요: index.html을 찾아줌)
@app.get("/")
async def read_index():
    return FileResponse("index.html")

# 4. 영상 스트리밍 엔드포인트
@app.get("/video/stream")
async def video_stream(request: Request):
    path = "static/bg_video.mp4"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    file_size = os.path.getsize(path)
    range_header = request.headers.get("range")

    if range_header:
        range_str = range_header.replace("bytes=", "").split("-")
        start = int(range_str[0])
        end = int(range_str[1]) if range_str[1] else file_size - 1
        size = end - start + 1

        def iter_file():
            with open(path, "rb") as f:
                f.seek(start)
                yield f.read(size)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(size),
            "Content-Type": "video/mp4",
        }
        return StreamingResponse(iter_file(), status_code=206, headers=headers)
    
    return FileResponse(path, media_type="video/mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)