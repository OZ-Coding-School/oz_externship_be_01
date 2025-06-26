from typing import Any, cast

import requests


def verify_kakao_token(access_token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)

    if response.status_code != 200:
        raise ValueError("유효하지 않은 카카오 토큰입니다.")

    return cast(dict[str, Any], response.json())


def verify_naver_token(access_token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)

    if response.status_code != 200:
        raise ValueError("유효하지 않은 네이버 토큰입니다.")

    return cast(dict[str, Any], response.json())
