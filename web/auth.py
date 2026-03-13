import json
import os
import logging
from functools import lru_cache
from typing import Any, Dict

import firebase_admin
from fastapi import Header, HTTPException
from firebase_admin import auth, credentials
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _build_public_firebase_config() -> Dict[str, str]:
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
    }


@lru_cache
def get_public_firebase_config() -> Dict[str, str]:
    return _build_public_firebase_config()


def _load_admin_credential() -> credentials.Base:
    service_account_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH",
        "credentials/firebase-service-account.json",
    )

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")

    if service_account_json.strip():
        return credentials.Certificate(json.loads(service_account_json))

    if os.path.exists(service_account_path):
        return credentials.Certificate(service_account_path)

    raise RuntimeError(
        "Firebase Admin credentials chưa được cấu hình. "
        "Đặt FIREBASE_SERVICE_ACCOUNT_PATH hoặc FIREBASE_SERVICE_ACCOUNT_JSON"
    )


@lru_cache
def init_firebase_admin() -> bool:
    if firebase_admin._apps:
        return True

    cred = _load_admin_credential()
    firebase_admin.initialize_app(cred)
    return True


def get_current_user(authorization: str = Header(default="")) -> Dict[str, Any]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu Bearer token")

    id_token = authorization.split(" ", 1)[1].strip()
    if not id_token:
        raise HTTPException(status_code=401, detail="ID token rỗng")

    try:
        init_firebase_admin()
        decoded = auth.verify_id_token(id_token)
        return decoded
    except RuntimeError as err:
        logger.exception("Firebase Admin init failed")
        raise HTTPException(
            status_code=500,
            detail=(
                "Backend chưa cấu hình Firebase Admin credentials. "
                "Cần set FIREBASE_SERVICE_ACCOUNT_JSON hoặc FIREBASE_SERVICE_ACCOUNT_PATH trên môi trường deploy."
            ),
        ) from err
    except Exception:
        logger.info("Invalid Firebase ID token")
        raise HTTPException(status_code=401, detail="ID token không hợp lệ")