import os
import uuid
from pathlib import Path
from typing import Dict

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web.auth import get_current_user, get_public_firebase_config
from web.services import create_job, ensure_dirs, run_pipeline

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "web" / "static"
UPLOAD_DIR = BASE_DIR / "uploads"

app = FastAPI(title="AI-Law Web App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_dirs()
JOBS: Dict[str, dict] = {}

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/firebase-config")
def firebase_config():
    config = get_public_firebase_config()
    if not config.get("apiKey") or not config.get("projectId"):
        raise HTTPException(status_code=500, detail="Firebase web config chưa được thiết lập")
    return config


@app.get("/api/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "uid": current_user.get("uid"),
        "email": current_user.get("email"),
    }


@app.post("/api/process")
async def process_document(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    input_file: UploadFile = File(...),
    output_json: bool = Form(True),
    output_sheets: bool = Form(False),
    mode: str = Form("tool"),
    sheets_id: str = Form(""),
    sheet_name: str = Form(""),
    credentials_path: str = Form("credentials/credentials.json"),
    no_clear: bool = Form(False),
    gemini_api_key: str = Form(""),
):
    if not input_file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file .docx")

    if not output_json and not output_sheets:
        raise HTTPException(status_code=400, detail="Phải chọn ít nhất một kiểu xuất dữ liệu")

    mode = mode.strip().lower()
    if mode not in {"tool", "tool_ai"}:
        raise HTTPException(status_code=400, detail="mode chỉ nhận: tool hoặc tool_ai")

    if output_sheets and not sheets_id.strip():
        raise HTTPException(status_code=400, detail="Thiếu Google Sheets ID")

    job_id = str(uuid.uuid4())
    temp_file_path = UPLOAD_DIR / f"{job_id}_{input_file.filename}"

    with open(temp_file_path, "wb") as destination:
        destination.write(await input_file.read())

    JOBS[job_id] = create_job(job_id, owner_uid=current_user.get("uid", ""))

    background_tasks.add_task(
        run_pipeline,
        JOBS,
        job_id,
        str(temp_file_path),
        output_json=output_json,
        output_sheets=output_sheets,
        mode=mode,
        sheets_id=sheets_id.strip() or None,
        sheet_name=sheet_name.strip() or None,
        credentials_path=credentials_path.strip() or "credentials/credentials.json",
        no_clear=no_clear,
        gemini_api_key=gemini_api_key.strip() or None,
    )

    return {"job_id": job_id, "status": "queued"}


@app.get("/api/status/{job_id}")
def get_status(job_id: str, current_user: dict = Depends(get_current_user)):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy job")
    if job.get("owner_uid") != current_user.get("uid"):
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem job này")
    return job


@app.get("/api/download/{job_id}/{output_type}")
def download_file(job_id: str, output_type: str, current_user: dict = Depends(get_current_user)):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy job")
    if job.get("owner_uid") != current_user.get("uid"):
        raise HTTPException(status_code=403, detail="Bạn không có quyền tải file của job này")

    files = job.get("result", {}).get("files", {})
    file_path = files.get(output_type)

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file output")

    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type="application/json")
