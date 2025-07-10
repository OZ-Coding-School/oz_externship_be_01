import os

from rest_framework.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
BLOCKED_ATTACHMENT_EXTENSIONS = {".exe"}


def validate_uploaded_files(
    files, max_count: int, field_name: str, allowed_extensions=None, blocked_extensions=None, max_size_mb=None
):

    if len(files) > max_count:
        raise ValidationError({field_name: [f"{field_name}는 최대 {max_count}개까지 업로드할 수 있습니다."]})

    for file in files:
        ext = os.path.splitext(file.name)[1].lower()

        if not ext:
            raise ValidationError({field_name: [f"'{file.name}'에는 확장자가 없습니다."]})

        if allowed_extensions and ext not in allowed_extensions:
            raise ValidationError({field_name: [f"'{file.name}'은(는) 허용되지 않는 파일 형식입니다."]})

        if blocked_extensions and ext in blocked_extensions:
            raise ValidationError({field_name: [f"'{file.name}'은(는 업로드할 수 없는 파일 형식입니다."]})

        if max_size_mb is not None:
            max_size_bytes = max_size_mb * 1024 * 1024
            if file.size > max_size_bytes:
                raise ValidationError({field_name: [f"'{file.name}'의 크기는 {max_size_mb}MB를 초과할 수 없습니다."]})
