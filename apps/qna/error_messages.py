# apps/qna/error_messages.py


class AnswerErrorMessages:
    """답변 관련 에러 메시지들"""

    # ===== 400 Bad Request 에러들 =====

    # 답변 채택 관련
    ADOPTED_ANSWER_ALREADY_EXISTS = {"detail": "이미 채택된 답변이 존재합니다."}  # 이미 채택된 다른 답변이 있을 때
    CANNOT_ADOPT_OWN_ANSWER = {"detail": "본인의 답변은 채택할 수 없습니다."}
    ANSWER_ALREADY_ADOPTED = {"detail": "이미 채택된 답변입니다."}  # 같은 답변을 한번 더 채택하려고 할 때

    # 이미지 업로드 관련
    # IMAGE_FILE_TOO_LARGE = {"detail": "이미지 파일 크기는 10MB를 초과할 수 없습니다."}
    # IMAGE_FORMAT_NOT_SUPPORTED = {"detail": "지원하지 않는 이미지 형식입니다. (JPEG, PNG, GIF, WebP만 가능)"}
    # TOO_MANY_IMAGES = {"detail": "이미지는 최대 5개까지 업로드할 수 있습니다."}
    # IMAGE_UPLOAD_FAILED = {"detail": "이미지 업로드에 실패했습니다. 다시 시도해주세요."}

    # ===== 403 Forbidden 에러들 =====

    # 답변 관련 권한
    ANSWER_AUTHOR_ONLY = {"detail": "본인이 작성한 답변만 수정할 수 있습니다."}
    ANSWER_DELETE_PERMISSION_DENIED = {"detail": "본인이 작성한 답변만 삭제할 수 있습니다."}
    ANSWER_CREATE_PERMISSION_DENIED = {"detail": "답변 작성 권한이 없습니다."}

    # 답변 채택 관련 권한
    QUESTION_AUTHOR_ADOPT_ONLY = {"detail": "본인의 질문에만 답변을 채택할 수 있습니다."}
    ADOPT_STUDENT_ONLY = {"detail": "수강생만 답변을 채택할 수 있습니다."}

    # ===== 404 Not Found 에러들 =====
    QUESTION_NOT_FOUND = {"detail": "해당 질문이 존재하지 않습니다."}
    ANSWER_NOT_FOUND = {"detail": "해당 답변이 존재하지 않습니다."}


class AnswerSuccessMessages:
    """답변 관련 성공 메시지들"""

    # 답변 관련
    ANSWER_CREATED = {"message": "답변이 성공적으로 등록되었습니다."}
    ANSWER_UPDATED = {"message": "답변이 성공적으로 수정되었습니다."}

    # 답변 채택 관련
    ANSWER_ADOPTED = {"message": "답변 채택 완료"}

    # 댓글 관련
    COMMENT_CREATED = {"message": "댓글 등록 완료"}

    # 이미지 관련
    # IMAGE_UPLOADED = {"message": "이미지가 성공적으로 업로드되었습니다."}
    # IMAGE_DELETED = {"message": "이미지가 성공적으로 삭제되었습니다."}
