# OZ CodingSchool LMS - 백엔드

## 과정 관리 어드민 (1팀)
# 🎓 Externship 수강관리 시스템

> Externship 백엔드 시스템은 관리자와 학생을 위한 수강 관리 기능을 제공합니다.  
> 과정 등록부터 수강 신청, 상태 관리까지 다양한 기능을 제공합니다.

---
## 📌 목차

1. [기술 스택](#-기술-스택)
2. [주요 기능](#-주요-기능)
3. [ERD](#-erd)
4. [프로젝트 구조](#-프로젝트-구조)
5. [API 문서](#-api-문서)
6. [테이블 명세서](#-테이블-명세서)
7. [팀원](#-팀원)

---

## 🔧 기술 스택

- Python 3.12  
- Django 4.x  
- Django REST Framework (DRF)  
- PostgreSQL  
- Redis  
- OAuth2 / JWT 인증  
- drf-spectacular (Swagger/OpenAPI 자동 문서화)  
- Docker, Nginx, Gunicorn, Uvicorn  
- AWS S3 (썸네일 이미지 업로드)  
- CI/CD: GitHub Actions (예정)

> 전체 아키텍처는 아래 다이어그램을 참고하세요.
<img width="1004" height="579" alt="image" src="https://github.com/user-attachments/assets/3b5cbd35-65f1-4eb8-b8ac-dfefa0f87c44" />





---

## 📌 주요 기능

### 관리자
- 과정 등록 / 수정 / 삭제
- 생성기수(Generation) 등록 및 관리
- 과목(Subject) 관리
- 드롭다운 리스트 제공

### 학생
- (예정) 수강 신청, 취소, 이력 조회

---

## 🖼 ERD

> 전체 데이터베이스 구조는 아래 링크에서 확인하실 수 있습니다.

📌 [ERD 보기 (dbdiagram)](https://dbdiagram.io/d/6823ff4e5b2fc4582f7c2afa/?utm_source=dbdiagram_embed&utm_medium=bottom_open)

---

## 📁 프로젝트 구조

```bash
oz_externship/
├── apps/
│   └── courses/
│       ├── __init__.py                        # courses 앱 초기화 모듈
│       ├── apps.py                            # Django 앱 설정 파일
│       ├── models.py                          # Course, Generation, Subject 모델 정의
│       ├── test.py                            # courses 관련 테스트 코드
│       ├── urls.py                            # courses 앱 내 URL 라우팅 정의
│       ├── views.py                           # 뷰 초기화 또는 공통 설정 용도
│       ├── core/                              # 공통 유틸 또는 상속용 클래스 디렉토리
│       ├── migrations/                        # 마이그레이션 파일 저장 폴더
│       ├── serializers/                       # DRF용 데이터 직렬화 클래스 모음
│       │   ├── course_serializers.py              # 과정 등록/조회용 시리얼라이저
│       │   ├── generation_serializer.py           # 생성기수 관련 시리얼라이저
│       │   ├── subject_serializers.py             # 과목 관련 시리얼라이저
│       │   └── dropdown_list_serializers.py       # 드롭다운 선택용 리스트 시리얼라이저
│       └── views/                             # 기능별 API View 클래스 정의
│           ├── __init__.py                        # views 모듈 초기화
│           ├── course_views.py                   # 과정 관련 CRUD API
│           ├── generation_views.py               # 생성기수 관련 CRUD API
│           ├── subject_views.py                  # 과목 관련 CRUD API
│           └── dropdown_list_views.py            # 드롭다운 리스트 조회 API
├── core/                                    # 프로젝트 전역 유틸, 공통 상속 클래스, S3 업로드 등
├── config/                                  # Django 설정 파일 모음
├── manage.py                                # Django 명령행 유틸
└── requirements.txt                         # 프로젝트 의존성 패키지 목록
```

---

## 🧪 API 문서

- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- 📄 [API 명세서 (Notion)](https://www.notion.so/API-209caf5650aa81788822c3094c8d4d80)

---

## 📊 테이블 명세서

> 전체 테이블 구조 및 컬럼 정보는 아래 구글 시트에서 확인하실 수 있습니다.

📄 [테이블 명세서 (Google Sheets)](https://docs.google.com/spreadsheets/d/1Ys_HVx7IofC3FF9eEb-9bVpB7nZTHQhIRiPNF85SXIA/edit?gid=684962824#gid=684962824)

---

## 👥 팀원
<table align="center">
  <tr>
    <th style="text-align: center;">이형묵</th>
    <th style="text-align: center;">장지훈</th>
    <th style="text-align: center;">양지운</th>
  </tr>
  <tr>
    <td style="text-align: center;">
      <img src="https://avatars.githubusercontent.com/u/201066886?v=4" width="100"/>
    </td>
    <td style="text-align: center;">
      <img src="https://avatars.githubusercontent.com/u/201066874?v=4" width="100"/>
    </td>
    <td style="text-align: center;">
      <img src="https://avatars.githubusercontent.com/u/144764519?v=4" width="100"/>
    </td>
  </tr>
  <tr>
    <td style="text-align: center;">@brojelly</td>
    <td style="text-align: center;">@yeduen</td>
    <td style="text-align: center;">@yangjiun00</td>
  </tr>
</table>

## 회원 기능 및 회원 관리 어드민 (2팀)
## 📖 프로젝트 소개

단순한 교육을 넘어, 더 나은 학습 환경을 만드는 것
**OZ CodingSchool LMS**는 다양한 학습 콘텐츠를 제공하는 온라인 교육 플랫폼입니다.
그리고 그 중심에는 안정적이고 효율적인 회원 관리 시스템이 존재합니다.

백엔드 2조는 이 프로젝트에서
수강생, 조교, 운영자 등의 회원 권한 관리 및
프로필 수정, 회원 탈퇴, 활동 통계 조회 등
프로젝트의 전반적인 회원 관리 기능을 담당하고 있습니다.
---
## :link: 배포 링크

> ### [⛪ 배포 링크](https://api.ozcoding.site/api/schema/swagger-ui/)

---

## 🖥️ 서비스 소개
> **로그인 API**: 소셜 로그인(카카오, 네이버), 이메일 로그인 API를 통해 사용자에게 로그인 기능을 제공합니다. <br>
> **어드민 회원 관리 API**: 관리자 전용 회원 정보 조회, 수정, 삭제 등 전반적인 회원 관리 및 수강신청 관리 기능을 제공합니다. <br>
> **회원 대시보드 API**: 관리자에게 수강생 전환 추이, 회원가입 통계, 탈퇴율 등 다양한 회원 관련 지표를 그래프 형태로 제공합니다. <br>
> **회원가입 API**: Gmail 및 Twilio 기반 이메일·휴대폰 인증 기능을 통해 안전한 회원가입 프로세스를 지원합니다.
--- 

## 팀 동료

### BE

| <a href=https://github.com/somineda/><img src="https://avatars.githubusercontent.com/u/191089828?v=4" width=100px/><br/><sub><b>@somineda</b></sub></a><br/> | <a href=https://github.com/kyukyu300><img src="https://avatars.githubusercontent.com/u/201066910?v=4" width=100px/><br/><sub><b>@kyukyu300</b></sub></a><br/> | <a href=https://github.com/harry99990><img src="https://avatars.githubusercontent.com/u/199310256?v=4" width=100px/><br/><sub><b>@harry99990</b></sub></a><br/> | <a href=https://github.com/jee1021><img src="https://avatars.githubusercontent.com/u/201070374?v=4" width=100px/><br/><sub><b>@jee1021</b></sub></a><br/> |
|:----------------------------------:|:----------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------:|
|                윤소민                 |    김규진     |                                                                            김상협                                                                            |    임지원     |                                                                      박00                                                                             |                                                                            이00                                                                             |                                          한00                                           |

## 📑 프로젝트 규칙

### Code Convention
>BE
> - 패키지명 전체 소문자
> - 클래스명, 인터페이스명 CamelCase
> - 클래스 이름 명사 사용
> - 상수명 SNAKE_CASE

### Communication Rules
> - Discord 활용 
> - 데일리 스크럼


## :clipboard: Documents
> [📜 API 명세서](https://www.notion.so/API-209caf5650aa81788822c3094c8d4d80)
> 
> [📜 요구사항 정의서](https://docs.google.com/spreadsheets/d/160YZn8-2RPGI8gRJQiHObgKXF0VQn1DiIjJp6aPkFic/edit?gid=0#gid=0)
> 
> [📜 ERD](https://www.notion.so/ERD-209caf5650aa812a913ccc3aad08aba8)
> 
> [📜 테이블 명세서](https://www.notion.so/209caf5650aa8152a00cd26e4bb05f7a)


## 질의응답 기능 및 관리 어드민 (3팀)

## 📖 프로젝트 소개

**OZ CodingSchool LMS**의 질의응답 시스템은 수강생, 조교, 운영진, 관리자 간의 학습 커뮤니케이션을 지원합니다.  
3팀은 질문/답변 기능부터 카테고리 및 댓글 시스템, 관리자 전용 어드민 기능, AI 챗봇 기능까지 전반적인 **Q&A 관리 시스템**을 개발하였습니다.

---

## 🔗 배포 링크

> ### [📌 Swagger 문서 바로가기](https://api.ozcoding.site/api/schema/swagger-ui/)

---

## 🖥️ 서비스 소개

> **질문/답변 API**: 수강생은 질문을 등록하고, 수강생·조교·운영진은 답변을 작성할 수 있습니다. 질문자는 답변을 채택할 수 있으며, 댓글 기능도 지원합니다.  
> **카테고리 관리 API**: 관리자 및 스태프는 대·중·소분류의 Q&A 카테고리를 등록, 조회, 삭제할 수 있습니다.  
> **Q&A 어드민 API**: 관리자 및 스태프는 질문/답변을 조회 및 삭제하고, 상세 내역을 확인할 수 있습니다.  
> **AI 챗봇 API**: 사용자는 질문 상세 페이지에서 AI에게 답변을 요청하거나, 대화를 이어갈 수 있습니다.  

---

## 👨‍👩‍👧‍👦 팀 동료

| <a href="https://github.com/choismjames23"><img src="https://avatars.githubusercontent.com/u/200033221?v=4" width=100px/><br/><sub><b>@choismjames23</b></sub></a> | <a href="https://github.com/leejiyun1"><img src="https://avatars.githubusercontent.com/u/201066873?v=4" width=100px/><br/><sub><b>@leejiyun1</b></sub></a> | <a href="https://github.com/hoonii111"><img src="https://avatars.githubusercontent.com/u/201067127?v=4" width=100px/><br/><sub><b>@hoonii111</b></sub></a> | <a href="https://github.com/aidoneus9"><img src="https://avatars.githubusercontent.com/u/155718337?v=4" width=100px/><br/><sub><b>@aidoneus9</b></sub></a> |
|:------------------------------------------------------------:|:-------------------------------------------------------------:|:-------------------------------------------------------------:|:-------------------------------------------------------------:|
| 최승민 | 이지윤 | 정명훈 | 이동경 |

---

## 🧰 사용 스택

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <br>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Amazon_AWS_S3-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini-000000?style=for-the-badge&logo=gemini&logoColor=white" />
</div>


## 📑 프로젝트 규칙

### 📌 Branch 전략
- `main`, `develop` 브랜치에 직접 push 금지
- `develop` 브랜치로부터 `feat/qna_각자맡은기능` 브랜치를 분기하여 작업
- PR 시 최소 2인 이상 리뷰 승인 필수

### 📌 Git 커밋 컨벤션
- 커밋 메시지에 적절한 접두사 작성  
- 주요 접두사 및 설명

| 접두사   | 설명                   |
| -------- | ---------------------- |
| ✨ Feat     | 새로운 기능 구현       |
| 🐛 Fix      | 버그 수정             |
| 📝 Docs     | 문서 추가 및 수정      |
| ♻️ Refactor | 코드 리팩토링 (동작 변경 없음) |
| 💡 Chore    | 기타 작업(주석, 코드 포매팅 스크립트)|

### 📌 Code Convention

- 패키지명 전체 소문자 (ex. apps/qna/serializers/questions_serializers.py)
- 클래스명, 인터페이스명 CamelCase (ex. IsStudentOrStaffOrAdminPermission)
- 클래스 이름 명사 사용 (ex. AnswerCommentCreateView)
- 상수명 SNAKE_CASE (ex. AWS_STORAGE_BUCKET_NAME)
- service 계층 메서드명 create, update, get, delete로 CRUD 통일 (ex. get_minor_ids) 

### 📌 Communication Rules

- **주요 채널**: zep 채널 활용(화면공유)
- **정기 회의**: 매일 오전 10시 15분 스크럼 / 매주 금요일 주간 스프린트, KPT 회고 진행

---

## 📋 Documents

- [📜 API 명세서](https://www.notion.so/API-209caf5650aa81788822c3094c8d4d80)
- [📜 요구사항 정의서](https://docs.google.com/spreadsheets/d/160YZn8-2RPGI8gRJQiHObgKXF0VQn1DiIjJp6aPkFic/edit#gid=0)
- [📜 ERD](https://www.notion.so/ERD-209caf5650aa812a913ccc3aad08aba8)
- [📜 테이블 명세서](https://www.notion.so/209caf5650aa8152a00cd26e4bb05f7a)
- [📜 Figma - User 화면 정의서](https://www.figma.com/design/ZM6OVhYKhH30XTPKMC7BaC/%EC%9D%B5%EC%8A%A4%ED%84%B4%EC%8B%AD--user-design-?node-id=23-3&p=f&t=UeVTlWEtia0pJqTb-0)
- [📜 Figma - Admin 화면 정의서](https://www.figma.com/design/QmpoIuImIkAtVMHbH7HGg1/%EC%9D%B5%EC%8A%A4%ED%84%B4%EC%8B%AD--admin-design-?node-id=0-1&p=f&t=Elply8Zo81rjKsrs-0)

---

## 커뮤니티 기능 및 관리 어드민 (4팀)

## 📖 프로젝트 소개

지식은 나눌수록 커지는 법! 💬 OZ CodingSchool 커뮤니티는 다양한 학습자들이 자유롭게 소통하고, 함께 성장하는 온라인 커뮤니티 공간,
함께 나누고, 질문하고, 응원하는 분위기 속에서 스터디, 질문, 잡담, 정보공유, 피드백 등 학습과 관련된 모든 소통이 가능하도록 개발해보았습니다.

---

> ### [⛪ 배포 링크](https://api.ozcoding.site/api/schema/swagger-ui/)

---
## 📑 API 소개

- **📌 게시글 API**: 사용자가 게시글을 작성, 삭제, 수정, 조회, 좋아요 기능까지 구현해보았습니다.  
- **📌 댓글 API**: 사용자가 특정 게시글의 댓글 목록 조회, 댓글 작성, 삭제, 수정을 할 수 있습니다.  
- **📌 어드민 카테고리 관리 API**: 관리자가 카테고리 목록, 상세 조회, 카테고리 삭제, 수정, 생성, 상태 ON/OFF 기능을 관리 할 수 있습니다.  
- **📌 어드민 게시글 관리 API**: 관리자가 공지사항 등록 및 게시글 목록 조회, 상세 조회, 삭제, 수정, 게시물 노출 ON/OFF 기능을 구현했습니다.  
- **📌 어드민 댓글 관리 API**: 관리자가 사용자의 댓글을 삭제 할 수 있도록 구현했습니다.

---

## 팀 동료

### BE

| <a href=https://github.com/CJY9697/><img src="https://avatars.githubusercontent.com/u/199873650?v=4" width=100px/><br/><sub><b>@CJY9697</b></sub></a><br/> | <a href=https://github.com/yeontae519><img src="https://avatars.githubusercontent.com/u/201067110?s=400&u=bb9748af261a87d49c9cd231299d58a583beda03&v=4" width=100px/><br/><sub><b>@yeontae519</b></sub></a><br/> | <a href=https://github.com/jjustph121><img src="https://avatars.githubusercontent.com/u/201066875?v=4" width=100px/><br/><sub><b>@jjustph121</b></sub></a><br/> | <a href=https://github.com/enjore1201><img src="https://avatars.githubusercontent.com/u/186259196?v=4" width=100px/><br/><sub><b>@enjore1201</b></sub></a><br/> |
|:----------------------------------:|:----------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------:|
|                최재영                 |    김태연     |                                                                            박 현                                                                            |    손건화     |                                                                      
---

## 📑 프로젝트 규칙

### Code Convention
> - 패키지명 전체 소문자 (ex. apps/community/views/admin/category_serializers.py)
> - 클래스명, 인터페이스명 CamelCase
> - 클래스 이름 명사 사용
> - 상수명 SNAKE_CASE

### Communication Rules
> - zep 활용
> - discord 활용

## 기술 스택

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <br>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Amazon_AWS_S3-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini-000000?style=for-the-badge&logo=gemini&logoColor=white" />
</div>

## Documents

- [📜 API 명세서](https://www.notion.so/API-209caf5650aa81788822c3094c8d4d80)
- [📜 요구사항 정의서](https://docs.google.com/spreadsheets/d/160YZn8-2RPGI8gRJQiHObgKXF0VQn1DiIjJp6aPkFic/edit#gid=0)
- [📜 ERD](https://www.notion.so/ERD-209caf5650aa812a913ccc3aad08aba8)

## 쪽지시험 기능 및 관리 어드민 (5팀)

# 📖 프로젝트 소개: 쪽지 시험 관리 시스템

---

# **💡 효율적인 쪽지 시험 관리를 위한 백엔드 솔루션**

이 프로젝트는 **관리자와 수강생을 위한 쪽지 시험(Test/Quiz) 관리 시스템의 백엔드 솔루션**을 제공합니다. **시험 생성부터 배포, 응시, 채점, 그리고 결과 분석에 이르는 전 과정을 효율적으로 지원**하며, **유연한 RESTful API를 통해 다양한 클라이언트 애플리케이션(프론트엔드, 모바일 앱 등)과 원활하게 연동**됩니다.

---

## 🔗 **배포 링크**

### 🚀 **API 서버 배포 URL: [https://tomato-test.kro.kr](https://tomato-test.kro.kr)**

---

## 🗣️ 프로젝트 발표 영상 & 발표 문서

### 🗓️ **프로젝트 기간: 2025.06.19 - 2025.07.16**

📺 발표 영상 예시 - NONE
📑 발표 문서 예시 - NONE

---

## 🖥️ 서비스 소개

* **시험 및 문제 관리 API**: 관리자가 쪽지 시험과 문제를 생성, 조회, 수정, 삭제할 수 있는 API를 제공합니다. 다양한 문제 유형(객관식, OX, 단답형 등)을 지원하며, 문제별 배점 설정이 가능합니다.
* **시험 배포 API**: 특정 기수에게 시험을 배포하고 고유 참가 코드를 발급하는 API입니다. 시험 활성화 상태 및 오픈/마감 시간 설정 기능을 포함합니다.
* **시험 응시 및 제출 API**: 수강생이 참가 코드를 통해 시험에 접속하고 답안을 제출할 수 있는 API를 제공합니다. 시험 시간 초과 또는 부정행위 감지 시 자동 제출 처리 로직이 구현되어 있습니다.
* **채점 및 결과 조회 API**: 제출된 답안을 자동으로 채점하고, 수강생은 자신의 시험 결과를, 관리자는 모든 응시 내역과 상세 결과를 조회할 수 있는 API를 제공합니다.
* **대시보드 통계 API**: 관리자에게 시험 응시 결과에 대한 다양한 통계 데이터(기수별 평균 점수, 시간 경과에 따른 점수 변화, 과목별 점수 등)를 제공하는 API입니다.

---

## 🧰 **사용 스택**

### 🔧 **시스템 아키텍처 다이어그램**

BE (Backend)


## 팀 동료
### BE (Backend)
<table align="center">
  <tr>
    <th style="text-align: center;">구은재</th>
    <th style="text-align: center;">이정호</th>
    <th style="text-align: center;">이상인</th>
    <th style="text-align: center;">박석민</th>
    <th style="text-align: center;">류재학</th>
  </tr>
  <tr>
    <td style="text-align: center;"><img src="https://avatars.githubusercontent.com/u/166082905?v=4"width="100"/></td>
    <td style="text-align: center;"><img src="https://avatars.githubusercontent.com/u/201067201?v=4" width="100"/></td>
    <td style="text-align: center;"><img src="https://avatars.githubusercontent.com/u/201066934?v=1" width="100"/></td>
    <td style="text-align: center;"><img src="https://avatars.githubusercontent.com/u/201067629?v=4" width="100"/></td>
    <td style="text-align: center;"><img src="https://avatars.githubusercontent.com/u/201066888?v=4" width="100"/></td>
  </tr>
  <tr>
    <td style="text-align: center;">@eunjaegu</td>
    <td style="text-align: center;">@leemera</td>
    <td style="text-align: center;">@rainsos</td>
    <td style="text-align: center;">@seokmin0724</td>
    <td style="text-align: center;">@jhryu627</td>
  </tr>
</table>  

## 📑 프로젝트 규칙

## Code Convention
BE (백엔드)
**패키지명**: 전체 소문자를 사용합니다. (예: com.example.project.domain.member)

**클래스명, 인터페이스명**: CamelCase를 사용합니다.

**클래스 이름**: 역할이 명확한 명사를 사용합니다.

**상수명**: SNAKE_CASE (모두 대문자, 단어는 언더스코어 _로 연결)를 사용합니다.

**접미사 통일**: Controller, Service, Dto, Repository, Mapper와 같은 계층별 접미사를 클래스명 뒤에 일관성 있게 붙입니다. (예: MemberController, MemberService)

**Service 계층 메서드명**: create, update, find, delete 등 CRUD 작업에 맞는 동사로 통일합니다. (예: createMember, findMemberById)

**Test 클래스**: 클래스명 앞에 Test 접두사를 사용합니다. (예: TestMemberService)

## Communication Rules
**주요 소통 채널**: zep을 이용하여 원격으로 소통을 원활하게 합니다

**정기 회의**: 매주 주 5일 (월,화,수,목,금) 10시 15분에 간단한 회의 진행
## 📋 Documents
### 📜 **API 명세서**: https://www.notion.so/API-209caf5650aa81788822c3094c8d4d80

### 📜 **요구사항 정의서**: https://docs.google.com/spreadsheets/d/160YZn8-2RPGI8gRJQiHObgKXF0VQn1DiIjJp6aPkFic/edit?gid=0#gid=0

### 📜 **ERD (개체-관계 다이어그램)**: https://www.notion.so/ERD-209caf5650aa812a913ccc3aad08aba8

### 📜 **테이블 명세서**: https://www.notion.so/209caf5650aa8152a00cd26e4bb05f7a

### 📜 화면 정의서 
   ### **User** : https://www.figma.com/design/ZM6OVhYKhH30XTPKMC7BaC/%EC%9D%B5%EC%8A%A4%ED%84%B4%EC%8B%AD--user-design-?node-id=23-3&p=f&t=UeVTlWEtia0pJqTb-0
   ### **Admin** : https://www.figma.com/design/QmpoIuImIkAtVMHbH7HGg1/%EC%9D%B5%EC%8A%A4%ED%84%B4%EC%8B%AD--admin-design-?node-id=0-1&p=f&t=Elply8Zo81rjKsrs-0
