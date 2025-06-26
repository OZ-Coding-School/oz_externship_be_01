from datetime import datetime, timedelta
from typing import Dict

import jwt
from django.conf import settings


def generate_jwt_token_pair(user_id: int) -> Dict[str, str]:
    payload_access: Dict[str, object] = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=60),
        "type": "access",
    }
    payload_refresh: Dict[str, object] = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh",
    }

    access_token: str = jwt.encode(payload_access, settings.SECRET_KEY, algorithm="HS256")
    refresh_token: str = jwt.encode(payload_refresh, settings.SECRET_KEY, algorithm="HS256")

    return {"access": access_token, "refresh": refresh_token}
