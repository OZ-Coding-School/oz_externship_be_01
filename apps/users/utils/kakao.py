import os
import random
import re
import string
from datetime import datetime
from typing import Dict, Optional, Tuple

import requests

from apps.users.models import User


def get_kakao_access_token(code: str, redirect_uri: str) -> Tuple[Optional[str], Optional[str]]:
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": os.environ.get("KAKAO_CLIENT_ID"),
        "redirect_uri": redirect_uri,
        "code": code,
    }

    response = requests.post(url, data=data)

    if response.status_code != 200:
        try:
            error_description = response.json().get("error_description", "")
        except Exception:
            error_description = "카카오 서버 응답 파싱 실패"
        return None, error_description

    return response.json().get("access_token"), None


def get_kakao_user_info(access_token: str) -> Optional[Dict[str, Optional[str]]]:
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    response_json = response.json()
    kakao_account = response_json.get("kakao_account", {})
    profile = kakao_account.get("profile", {})

    return {
        "kakao_id": response_json.get("id"),
        "email": kakao_account.get("email"),
        "nickname": profile.get("nickname"),
        "phone_number": kakao_account.get("phone_number"),
        "birthyear": kakao_account.get("birthyear"),
        "birthday": kakao_account.get("birthday"),
        "profile_image_url": profile.get("profile_image_url"),
        "name": kakao_account.get("name"),
        "gender": kakao_account.get("gender"),
    }


def format_full_birthday(year: Optional[str], mmdd: Optional[str]) -> Optional[str]:
    if not year or not mmdd or len(mmdd) != 4:
        return None
    try:
        return datetime.strptime(f"{year}{mmdd}", "%Y%m%d").date().isoformat()
    except ValueError:
        return None


def generate_unique_nickname(base: str) -> str:
    base = base[:10]  # 너무 길면 자름
    while True:
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        nickname = f"{base}_{suffix}"
        if not User.objects.filter(nickname=nickname).exists():
            return nickname


# 전화번호 정규화
def normalize_phone_number(phone: str) -> str:
    if not phone:
        return ""

    # +82 10-1234-5678 → 010-1234-5678
    phone = phone.strip().replace(" ", "").replace("+82", "0")

    # 숫자만 남기기
    digits = re.sub(r"[^\d]", "", phone)

    # 번호 조합 (010 포함 10자리 or 11자리)
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    else:
        return phone
