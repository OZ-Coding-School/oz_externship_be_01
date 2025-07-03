import os
from datetime import datetime
from typing import Dict, Optional

import requests


def get_kakao_access_token(code: str) -> Optional[str]:
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": os.environ.get("KAKAO_CLIENT_ID"),
        "redirect_uri": os.environ.get("KAKAO_REDIRECT_URI"),
        "code": code,
    }

    response = requests.post(url, data=data)

    return response.json().get("access_token")


def get_kakao_user_info(access_token: str) -> Optional[Dict[str, Optional[str]]]:
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    kakao_account = response.json().get("kakao_account", {})
    profile = kakao_account.get("profile", {})
    return {
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
