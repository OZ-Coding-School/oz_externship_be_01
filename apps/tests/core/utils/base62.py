# apps/base62.py

import json

from django.db import models

# 변경 1: Base62 인코딩 함수 추가
BASE62_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode_base62(num: int, length: int = 6) -> str:
    """
    정수를 Base62 문자열로 인코딩합니다.
    지정된 길이에 맞추기 위해 앞에 '0'을 채웁니다.
    """
    if num == 0:
        return BASE62_CHARS[0] * length

    result = []
    base = len(BASE62_CHARS)
    while num > 0:
        result.append(BASE62_CHARS[num % base])
        num //= base

    encoded_str = "".join(reversed(result))
    # 지정된 길이에 맞추기 위해 앞에 '0' 채우기
    return encoded_str.zfill(length)


def generate_questions_snapshot_json(test_instance: models.Model) -> str | None:
    """
    Test 인스턴스에서 질문 스냅샷 JSON 문자열을 생성합니다.
    """
    if hasattr(test_instance, "questions") and test_instance.questions.exists():
        questions_data = [
            {
                "id": q.id,
                "question": q.question,
                "prompt": q.prompt,
                "type": q.type,
                "options": getattr(q, "options_json", None),
                "answer": q.answer,
                "point": q.point,
                "explanation": q.explanation,
            }
            for q in test_instance.questions.all()
        ]
        return json.dumps(questions_data, ensure_ascii=False)
    return None
