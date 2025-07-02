from typing import Dict, Optional

import requests


def verify_naver_token(access_token: str) -> Optional[Dict[str, Optional[str]]]:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()
    if data.get("resultcode") != "00":
        return None

    profile = data.get("response", {})
    return {
        "id": profile.get("id"),  # 네이버 아이디
        "email": profile.get("email"),
        "nickname": profile.get("nickname"),
        "name": profile.get("name"),
        "profile_image": profile.get("profile_image"),
    }
