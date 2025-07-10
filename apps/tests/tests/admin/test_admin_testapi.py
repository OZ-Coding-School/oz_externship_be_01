import json

import pytest
from django.urls import reverse
from rest_framework import status

from apps.tests.models import Test as TestModel
from apps.tests.models import TestQuestion
from apps.users.models import User


# 쪽지시험 생성 TEST
@pytest.mark.django_db
class TestCaseAdminTestCreateAPI:
    def test_create_success(self, api_client, admin_user, subject, thumbnail_file):
        print("\n===== [생성] 쪽지시험 생성 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        url = reverse("tests:test-create")
        data = {
            "title": "테스트 쪽지시험 생성",
            "subject_id": subject.id,
            "thumbnail_file": thumbnail_file,
        }

        response = api_client.post(url, data, format="multipart")
        print(
            f"[생성] 테스트 결과: 상태코드={response.status_code}, 설명='생성 성공', 응답 ID={response.data.get('id')}"
        )

        assert response.status_code == status.HTTP_201_CREATED, f"[생성 성공] 예상 201, 실제 {response.status_code}"
        assert "id" in response.data, "[생성 성공] 응답에 'id' 필드가 없습니다."
        assert response.data["title"] == data["title"], f"[생성 성공] title 불일치: {response.data['title']}"
        assert response.data["thumbnail_img_url"].startswith(
            "http"
        ), "[생성 성공] 썸네일 URL이 http로 시작하지 않습니다."

        print("===== [생성] 쪽지시험 생성 테스트 종료 =====\n")

    def test_create_missing_title(self, api_client, admin_user, subject, thumbnail_file):
        print("\n===== [생성] 필수 필드 누락 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        url = reverse("tests:test-create")
        data = {
            # "title" 필드 누락
            "subject_id": subject.id,
            "thumbnail_file": thumbnail_file,
        }

        response = api_client.post(url, data, format="multipart")
        print(f"[생성] 테스트 결과: 상태코드={response.status_code}, 설명='title 누락'")

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f"[title 누락] 예상 400, 실제 {response.status_code}"
        assert (
            "title" in response.data
        ), f"[title 누락] 응답에 'title' 필드 에러 메시지가 없습니다. 응답: {response.data}"

        print("===== [생성] 필수 필드 누락 테스트 종료 =====\n")


# 쪽지시험 수정 TEST
@pytest.mark.django_db
class TestCaseAdminTestUpdateAPI:
    def test_update_success(self, api_client, admin_user, subject):
        print("\n===== [수정] 쪽지시험 수정 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        test = TestModel.objects.create(
            title="수정 전 쪽지시험",
            subject=subject,
            thumbnail_img_url="https://example.com/old-thumbnail.png",
        )

        url = reverse("tests:admin-test-update", args=[test.id])
        data = {
            "title": "수정된 쪽지시험 제목",
        }

        response = api_client.patch(url, data, format="multipart")
        print(f"[수정] 테스트 결과: 상태코드={response.status_code}, 설명='제목 수정 성공'")

        assert response.status_code == status.HTTP_200_OK, f"[제목 수정] 예상 200, 실제 {response.status_code}"
        assert response.data["title"] == data["title"], f"[제목 수정] title 불일치: {response.data['title']}"

        print("===== [수정] 쪽지시험 수정 테스트 종료 =====\n")

    def test_update_with_thumbnail(self, api_client, admin_user, subject, thumbnail_file):
        print("\n===== [수정] 썸네일 포함 수정 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        test = TestModel.objects.create(
            title="썸네일 수정 전 쪽지시험",
            subject=subject,
            thumbnail_img_url="https://example.com/old-thumbnail.png",
        )

        url = reverse("tests:admin-test-update", args=[test.id])
        data = {
            "title": "썸네일 포함 수정",
            "thumbnail_file": thumbnail_file,
        }

        response = api_client.patch(url, data, format="multipart")
        print(f"[수정] 테스트 결과: 상태코드={response.status_code}, 설명='썸네일 포함 수정'")

        assert response.status_code == status.HTTP_200_OK, f"[썸네일 수정] 예상 200, 실제 {response.status_code}"
        assert response.data["title"] == data["title"], f"[썸네일 수정] title 불일치: {response.data['title']}"
        assert response.data["thumbnail_img_url"].startswith(
            "https://fake-s3-bucket/"
        ), f"[썸네일 수정] thumbnail_img_url 예상과 불일치: {response.data['thumbnail_img_url']}"

        print("===== [수정] 썸네일 포함 수정 테스트 종료 =====\n")

    def test_update_not_found(self, api_client, admin_user):
        print("\n===== [수정] 존재하지 않는 ID 수정 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        url = reverse("tests:admin-test-update", args=[999999])
        data = {"title": "수정된 쪽지시험 제목"}

        response = api_client.patch(url, data, format="multipart")
        print(f"[수정] 테스트 결과: 상태코드={response.status_code}, 설명='존재하지 않는 ID'")

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), f"[존재하지 않는 ID] 예상 404, 실제 {response.status_code}"

        print("===== [수정] 존재하지 않는 ID 수정 테스트 종료 =====\n")


# 쪽지시험 삭제 TEST
@pytest.mark.django_db
class TestCaseAdminTestDeleteAPI:
    def test_delete_success(self, api_client, admin_user, subject):
        print("\n===== [삭제] 쪽지시험 삭제 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        test = TestModel.objects.create(
            title="삭제용 테스트 쪽지시험",
            subject=subject,
            thumbnail_img_url="https://example.com/test-thumbnail.png",
        )

        url = reverse("tests:admin-test-delete", args=[test.id])

        response = api_client.delete(url)
        print(f"[삭제] 테스트 결과: 상태코드={response.status_code}, 설명='삭제 성공'")

        assert response.status_code == status.HTTP_204_NO_CONTENT, f"[삭제 성공] 예상 204, 실제 {response.status_code}"
        exists = TestModel.objects.filter(id=test.id).exists()
        assert not exists, "[삭제 성공] 삭제 후에도 쪽지시험이 DB에 남아있습니다."

        print("===== [삭제] 쪽지시험 삭제 테스트 종료 =====\n")

    def test_delete_not_found(self, api_client, admin_user):
        print("\n===== [삭제] 존재하지 않는 ID 삭제 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        url = reverse("tests:admin-test-delete", args=[999999])

        response = api_client.delete(url)
        print(f"[삭제] 테스트 결과: 상태코드={response.status_code}, 설명='존재하지 않는 ID'")

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), f"[존재하지 않는 ID] 예상 404, 실제 {response.status_code}"

        print("===== [삭제] 존재하지 않는 ID 삭제 테스트 종료 =====\n")

    def test_delete_unauthenticated(self, api_client, subject):
        print("\n===== [삭제] 인증 없음 테스트 시작 =====")
        test = TestModel.objects.create(
            title="인증없는 삭제 테스트",
            subject=subject,
            thumbnail_img_url="https://example.com/test-thumbnail.png",
        )

        url = reverse("tests:admin-test-delete", args=[test.id])

        response = api_client.delete(url)
        print(f"[삭제] 테스트 결과: 상태코드={response.status_code}, 설명='인증 없음(401)'")

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), f"[인증 없음] 예상 401, 실제 {response.status_code}"

        print("===== [삭제] 인증 없음 테스트 종료 =====\n")

    def test_delete_forbidden(self, api_client, subject):
        print("\n===== [삭제] 권한 없음 테스트 시작 =====")
        user = User.objects.create_user(
            email="general@example.com",
            password="password123!",
            role=User.Role.GENERAL,
            name="일반유저",
            nickname="genuser",
            phone_number="01000000001",
        )
        api_client.force_authenticate(user=user)

        test = TestModel.objects.create(
            title="권한없는 삭제 테스트",
            subject=subject,
            thumbnail_img_url="https://example.com/test-thumbnail.png",
        )

        url = reverse("tests:admin-test-delete", args=[test.id])

        response = api_client.delete(url)
        print(f"[삭제] 테스트 결과: 상태코드={response.status_code}, 설명='권한 없음(403)'")

        assert response.status_code == status.HTTP_403_FORBIDDEN, f"[권한 없음] 예상 403, 실제 {response.status_code}"

        print("===== [삭제] 권한 없음 테스트 종료 =====\n")


# 쪽지시험 목록조회 Test
@pytest.mark.django_db
class TestCaseAdminTestListAPI:
    def test_list_success(self, api_client, admin_user, subject):
        print("\n===== [목록] 쪽지시험 목록조회 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        # 더미 쪽지시험 여러 개 생성
        for i in range(3):
            TestModel.objects.create(
                title=f"테스트 쪽지시험 {i+1}",
                subject=subject,
                thumbnail_img_url=f"https://example.com/test-thumbnail-{i+1}.png",
            )

        url = reverse("tests:admin-test-list")
        response = api_client.get(url)
        print(f"[목록] 테스트 결과: 상태코드={response.status_code}, 조회된 개수={response.data.get('count')}")

        assert response.status_code == status.HTTP_200_OK, f"[목록조회 성공] 예상 200, 실제 {response.status_code}"
        assert isinstance(response.data, dict), f"[목록조회 성공] 응답 타입이 dict가 아님: {type(response.data)}"
        assert "results" in response.data, "[목록조회 성공] 응답에 'results' 키가 없습니다."
        assert isinstance(response.data["results"], list), "[목록조회 성공] results가 리스트 형태가 아님"
        assert response.data["count"] >= 3, f"[목록조회 성공] 생성한 3개 이상이 조회되지 않음: {response.data['count']}"

        print("===== [목록] 쪽지시험 목록조회 테스트 종료 =====\n")

    def test_list_permission_denied(self, api_client):
        print("\n===== [목록] 인증 없음 목록조회 테스트 시작 =====")
        url = reverse("tests:admin-test-list")
        response = api_client.get(url)
        print(f"[목록] 테스트 결과: 상태코드={response.status_code}, 설명='인증 없음(401)'")

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), f"[인증 없음] 예상 401, 실제 {response.status_code}"

        print("===== [목록] 인증 없음 목록조회 테스트 종료 =====\n")


# 쪽지시험 상세조회 Test
@pytest.mark.django_db
class TestCaseAdminTestDetailAPI:
    def test_detail_success(self, api_client, admin_user, subject):
        print("\n===== [상세] 쪽지시험 상세조회 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        test = TestModel.objects.create(
            title="상세조회용 쪽지시험",
            subject=subject,
            thumbnail_img_url="https://example.com/test-thumbnail.png",
        )

        # 문제 유형별 생성
        TestQuestion.objects.create(
            test=test,
            type="multiple_choice_single",
            question="객관식 단일 문제",
            point=5,
            options_json=json.dumps(["A", "B", "C"]),
            answer="B",
        )
        TestQuestion.objects.create(
            test=test,
            type="multiple_choice_multi",
            question="객관식 다중 문제",
            point=5,
            options_json=json.dumps(["X", "Y", "Z"]),
            answer=["X", "Z"],
        )
        TestQuestion.objects.create(
            test=test,
            type="ox",
            question="O/X 문제",
            point=5,
            answer="O",
        )
        TestQuestion.objects.create(
            test=test,
            type="ordering",
            question="순서 정렬 문제",
            point=5,
            options_json=json.dumps(["1단계", "2단계", "3단계"]),
            answer=["1단계", "2단계", "3단계"],
        )
        TestQuestion.objects.create(
            test=test,
            type="fill_in_blank",
            question="빈칸 채우기 문제",
            point=5,
            answer=["FIFO"],
        )
        TestQuestion.objects.create(
            test=test,
            type="short_answer",
            question="주관식 단답형 문제",
            point=5,
            answer="정답",
        )

        url = reverse("tests:test-detail", args=[test.id])

        response = api_client.get(url)
        print(f"[상세] 테스트 결과: 상태코드={response.status_code}, 설명='상세조회 성공'")

        assert response.status_code == status.HTTP_200_OK, f"[상세조회 성공] 예상 200, 실제 {response.status_code}"
        assert response.data["id"] == test.id, "[상세조회 성공] 쪽지시험 ID 불일치"
        assert response.data["title"] == test.title, "[상세조회 성공] 쪽지시험 제목 불일치"
        assert (
            response.data["question_count"] == 6
        ), f"[상세조회 성공] 문제 개수 불일치: {response.data['question_count']}"
        assert isinstance(response.data["questions"], list), "[상세조회 성공] questions가 리스트가 아님"

        for q in response.data["questions"]:
            qtype = q["type"]
            answer = q["answer"]

            if qtype in ["multiple_choice_multi", "ordering", "fill_in_blank"]:
                assert isinstance(answer, list), f"[{qtype}] answer는 list여야 합니다. 실제: {type(answer)}"
            else:
                assert isinstance(answer, str), f"[{qtype}] answer는 string이어야 합니다. 실제: {type(answer)}"

        print("===== [상세] 쪽지시험 상세조회 테스트 종료 =====\n")

    def test_detail_not_found(self, api_client, admin_user):
        print("\n===== [상세] 존재하지 않는 쪽지시험 상세조회 테스트 시작 =====")
        api_client.force_authenticate(user=admin_user)

        url = reverse("tests:test-detail", args=[999999])
        response = api_client.get(url)
        print(f"[상세] 테스트 결과: 상태코드={response.status_code}, 설명='존재하지 않는 ID'")

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), f"[존재하지 않는 ID] 예상 404, 실제 {response.status_code}"

        print("===== [상세] 존재하지 않는 쪽지시험 상세조회 테스트 종료 =====\n")
