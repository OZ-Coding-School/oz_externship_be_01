from typing import Any, Dict, Optional, cast

import requests


def verify_kakao_token(access_token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)

    if response.status_code != 200:
        raise ValueError("유효하지 않은 카카오 토큰입니다.")

    return cast(dict[str, Any], response.json())


def verify_naver_token(access_token: str) -> Optional[Dict[str, Optional[str]]]:
    print("verify_naver_token() 함수 시작")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)

    print("네이버 응답 상태코드:", response.status_code)
    print("네이버 응답 본문:", response.text)

    if response.status_code != 200:
        return None

    data = response.json()
    if data.get("resultcode") != "00":
        return None

    profile = data.get("response", {})
    return profile
