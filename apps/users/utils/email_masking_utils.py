# 이메일마스킹처리
def mask_email(email: str) -> str:
    try:
        local_part, domain = email.split("@")
    except ValueError:
        return email

    if len(local_part) <= 2:
        masked_local = local_part[0] + "*"
    else:
        masked_local = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]

    return f"{masked_local}@{domain}"
