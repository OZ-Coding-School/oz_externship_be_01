from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class MockQuestionUpdateView(APIView):
    def patch(self, request: Request, question_id: int) -> Response:
        return Response(
            {
                "id": question_id,
                "title": request.data.get("title", "기존 제목"),
                "content": request.data.get("content", "기존 내용"),
                "author": {"id": 7, "nickname": "oz_student"},
                "category": {"id": request.data.get("category_id", 4), "depth_3": "Python 문법"},
                "images": request.data.get("image_urls", []),
                "created_at": "2025-06-22T14:00:00Z",
                "updated_at": "2025-06-23T08:30:00Z",
            },
            status=status.HTTP_200_OK,
        )


class MockQuestionDetailView(APIView):
    def get(self, request: Request, question_id: int) -> Response:
        return Response(
            {
                "id": question_id,
                "title": "Django 마이그레이션 오류 질문입니다",
                "content": "migrate 명령 시 오류가 납니다. 해결 방법이 궁금합니다.",
                "images": ["https://cdn.ozcoding.com/media/questions/101/1.jpg"],
                "author": {
                    "id": 7,
                    "nickname": "oz_student",
                    "profile_image_url": "https://cdn.ozcoding.com/profiles/user7.png",
                },
                "category": {"depth_1": "백엔드", "depth_2": "Python", "depth_3": "Django 오류"},
                "view_count": 24,
                "created_at": "2025-06-23T05:00:00Z",
                "answers": [
                    {
                        "id": 201,
                        "content": "settings.py에 DATABASE 설정을 다시 확인해보세요.",
                        "is_adopted": True,
                        "created_at": "2025-06-23T06:00:00Z",
                        "author": {
                            "id": 8,
                            "nickname": "oz_helper",
                            "profile_image_url": "https://cdn.ozcoding.com/profiles/user8.png",
                        },
                        "comments": [
                            {
                                "id": 301,
                                "content": "덕분에 해결했어요 감사합니다!",
                                "created_at": "2025-06-23T07:00:00Z",
                                "author": {
                                    "id": 7,
                                    "nickname": "oz_student",
                                    "profile_image_url": "https://cdn.ozcoding.com/profiles/user7.png",
                                },
                            }
                        ],
                    }
                ],
            },
            status=status.HTTP_200_OK,
        )


class MockQuestionListView(APIView):
    def get(self, request: Request) -> Response:
        return Response(
            {
                "count": 32,
                "next": "/api/v1/qna/questions/?page=2",
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "title": "Django 마이그레이션 질문입니다",
                        "content": "makemigrations 이후 migrate 시 오류가 납니다.",
                        "author": {
                            "nickname": "oz_student",
                            "profile_image_url": "https://cdn.ozcoding.com/profile/oz_student.jpg",
                        },
                        "category": {"depth_1": "웹개발", "depth_2": "Django", "depth_3": "오류 해결"},
                        "answer_count": 3,
                        "view_count": 123,
                        "created_at": "2025-06-23T02:22:00Z",
                        "thumbnail": "https://cdn.ozcoding.com/media/questions/1/thumb.jpg",
                    }
                ],
            },
            status=status.HTTP_200_OK,
        )


class MockQuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:

        data = request.data

        return Response(
            {
                "id": 101,
                "title": data.get("title", "제목 없음"),
                "content": data.get("content", "내용 없음"),
                "author": {
                    "id": request.user.id if request.user.is_authenticated else 7,
                    "nickname": request.user.nickname if request.user.is_authenticated else "oz_student",
                },
                "category": {"id": data.get("category_id", 2), "depth_3": "Django 오류"},
                "images": data.get(
                    "image_urls",
                    [
                        "https://cdn.ozcoding.com/media/questions/101/1.jpg",
                        "https://cdn.ozcoding.com/media/questions/101/2.jpg",
                    ],
                ),
                "created_at": "2025-06-23T05:00:00Z",
            },
            status=status.HTTP_200_OK,
        )
