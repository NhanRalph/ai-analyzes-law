import os
import shutil
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from src.ai_classifier import AIClassifier
from src.document_reader import DocumentReader
from src.json_exporter import JSONExporter
from src.parser import LegalDocumentParser
from src.sheets_exporter import SheetsExporter


def ensure_dirs() -> None:
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("output/web", exist_ok=True)


def create_job(job_id: str, owner_uid: str) -> Dict[str, Any]:
    return {
        "job_id": job_id,
        "owner_uid": owner_uid,
        "status": "queued",
        "message": "Đang chờ xử lý",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "result": {
            "summary": {},
            "files": {},
            "sheets": {},
        },
        "error": None,
    }


def _set_job_status(jobs: Dict[str, Dict[str, Any]], job_id: str, status: str, message: str) -> None:
    jobs[job_id]["status"] = status
    jobs[job_id]["message"] = message
    jobs[job_id]["updated_at"] = datetime.now().isoformat()


def _build_summary(data: list[dict]) -> Dict[str, Any]:
    chapters = {entry.get("chuong") for entry in data if entry.get("chuong")}
    sections = {entry.get("muc") for entry in data if entry.get("muc")}
    articles = {entry.get("dieu") for entry in data if entry.get("dieu")}
    clauses = sum(1 for entry in data if entry.get("khoan"))
    points = sum(1 for entry in data if entry.get("diem"))
    ai_classified = sum(1 for entry in data if entry.get("ai_classification"))

    return {
        "total_entries": len(data),
        "chapters": len(chapters),
        "sections": len(sections),
        "articles": len(articles),
        "clauses": clauses,
        "points": points,
        "ai_classified": ai_classified,
    }


def run_pipeline(
    jobs: Dict[str, Dict[str, Any]],
    job_id: str,
    input_file_path: str,
    *,
    output_json: bool,
    output_sheets: bool,
    mode: str,
    sheets_id: Optional[str],
    sheet_name: Optional[str],
    credentials_path: str,
    no_clear: bool,
    gemini_api_key: Optional[str],
) -> None:
    try:
        _set_job_status(jobs, job_id, "running", "Đang đọc file .docx")
        reader = DocumentReader(input_file_path)
        paragraphs = reader.read()

        if not paragraphs:
            raise ValueError("Không thể đọc file hoặc file rỗng")

        _set_job_status(jobs, job_id, "running", "Đang phân tích cấu trúc văn bản")
        parser = LegalDocumentParser()
        data = parser.parse(paragraphs, source_name=input_file_path)

        if not data:
            raise ValueError("Không parse được dữ liệu")

        if mode == "tool_ai":
            _set_job_status(jobs, job_id, "running", "Đang phân loại bằng Gemini AI")
            ai_classifier = AIClassifier(api_key=gemini_api_key)
            data = ai_classifier.classify_batch(data)
            definitions = {
                "hoa_chat": ai_classifier.definitions_hoa_chat,
                "hang_muc": ai_classifier.definitions_hang_muc,
            }
        else:
            definitions = None

        jobs[job_id]["result"]["summary"] = _build_summary(data)

        if output_json:
            _set_job_status(jobs, job_id, "running", "Đang xuất JSON")
            exporter = JSONExporter(output_dir="output/web")
            nested_data = parser.build_nested_structure()
            flat_path, nested_path = exporter.export_both(
                data,
                nested_data,
                base_filename=f"job_{job_id}",
                definitions=definitions,
            )
            jobs[job_id]["result"]["files"] = {
                "flat": flat_path,
                "nested": nested_path,
            }

        if output_sheets:
            _set_job_status(jobs, job_id, "running", "Đang xuất Google Sheets")
            if not sheets_id:
                raise ValueError("Thiếu sheets_id cho chế độ xuất Google Sheets")
            has_env_credentials = bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or os.getenv("GG_SERVICE_ACCOUNT_JSON"))
            if not os.path.exists(credentials_path) and not has_env_credentials:
                raise ValueError(f"Không tìm thấy credentials: {credentials_path}")

            sheets_exporter = SheetsExporter(credentials_path, sheets_id)
            success = sheets_exporter.export_data(
                data,
                clear_existing=(not no_clear),
                sheet_name=sheet_name,
                van_ban=parser.metadata.get("van_ban"),
                ngay_ban_hanh=parser.metadata.get("ngay_ban_hanh"),
            )
            if not success:
                raise RuntimeError("Xuất Google Sheets thất bại")

            jobs[job_id]["result"]["sheets"] = {
                "sheets_id": sheets_id,
                "url": f"https://docs.google.com/spreadsheets/d/{sheets_id}",
            }

        _set_job_status(jobs, job_id, "done", "Hoàn thành")

    except Exception as error:
        jobs[job_id]["error"] = {
            "message": str(error),
            "trace": traceback.format_exc(),
        }
        _set_job_status(jobs, job_id, "error", "Xử lý thất bại")
    finally:
        if os.path.exists(input_file_path):
            try:
                os.remove(input_file_path)
            except OSError:
                pass


def save_upload_file(source_path: str, target_path: str) -> None:
    with open(source_path, "rb") as source_file, open(target_path, "wb") as target_file:
        shutil.copyfileobj(source_file, target_file)
