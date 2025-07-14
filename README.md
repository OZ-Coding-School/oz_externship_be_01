# OZ CodingSchool LMS - 백엔드

## 과정 관리 어드민 (1팀)

## 회원 기능 및 회원 관리 어드민 (2팀)

## 질의응답 기능 및 관리 어드민 (3팀)

## 커뮤니티 기능 및 관리 어드민 (4팀)

## 쪽지시험 기능 및 관리 어드민 (5팀)

📖 프로젝트 소개: 쪽지 시험 관리 시스템
이 프로젝트는 관리자와 수강생을 위한 쪽지 시험(Test/Quiz) 관리 시스템의 백엔드 솔루션을 제공합니다. 시험 생성부터 배포, 응시, 채점, 그리고 결과 분석에 이르는 전 과정을 효율적으로 지원하며, 유연한 RESTful API를 통해 다양한 클라이언트 애플리케이션(프론트엔드, 모바일 앱 등)과 원활하게 연동됩니다.

🔗 배포 링크
⛪ 배포 링크  - API 서버 배포 URL "https://tomato-test.kro.kr"

🗣️ 프로젝트 발표 영상 & 발표 문서
🗓️ 2025.06.19 - 2025.07.16

📺 발표 영상 예시 - NONE
📑 발표 문서 예시 - NONE

🖥️ 서비스 소개
(백엔드 프로젝트이므로, 직접적인 사용자 화면보다는 API가 제공하는 핵심 기능과 데이터 흐름을 중심으로 설명합니다. 필요하다면 API 응답 예시나 주요 데이터 모델 구조를 간략하게 설명할 수 있습니다.)

시험 및 문제 관리 API: 관리자가 쪽지 시험과 문제를 생성, 조회, 수정, 삭제할 수 있는 API를 제공합니다. 다양한 문제 유형(객관식, OX, 단답형 등)을 지원하며, 문제별 배점 설정이 가능합니다.

시험 배포 API: 특정 기수에게 시험을 배포하고 고유 참가 코드를 발급하는 API입니다. 시험 활성화 상태 및 오픈/마감 시간 설정 기능을 포함합니다.

시험 응시 및 제출 API: 수강생이 참가 코드를 통해 시험에 접속하고 답안을 제출할 수 있는 API를 제공합니다. 시험 시간 초과 또는 부정행위 감지 시 자동 제출 처리 로직이 구현되어 있습니다.

채점 및 결과 조회 API: 제출된 답안을 자동으로 채점하고, 수강생은 자신의 시험 결과를, 관리자는 모든 응시 내역과 상세 결과를 조회할 수 있는 API를 제공합니다.

대시보드 통계 API: 관리자에게 시험 응시 결과에 대한 다양한 통계 데이터(기수별 평균 점수, 시간 경과에 따른 점수 변화, 과목별 점수 등)를 제공하는 API입니다.

🧰 사용 스택
🔧 System Architecture
(여기에 백엔드 시스템 아키텍처 다이어그램 이미지를 삽입하거나, 간략한 설명을 추가할 수 있습니다.)

코드 스니펫

graph TD
    A[클라이언트 앱] --> B(Nginx - 웹 서버/프록시)
    B --> C(백엔드 서버 - Django)
    C -- 데이터 영속성 --> D(PostgreSQL)
    C -- 파일 저장 --> E(로컬 Docker 볼륨)
    C -- 캐싱/메시징 --> F(Redis)

BE (Backend)

언어: Python

프레임워크: Django

데이터베이스: PostgreSQL (PgAdmin4는 PostgreSQL을 관리하는 도구)

ORM: Django ORM (Django의 내장 ORM)

보안: JWT (토큰 기반 인증/인가)

클라우드: AWS (Amazon Web Services)

- 애플리케이션 배포: AWS EC2
    
- 파일 저장: AWS S3
    
- 데이터베이스: AWS RDS (PostgreSQL)
    
- DNS 관리: AWS Route 53

API 문서화: Django REST Swagger / drf-spectacular (Swagger UI를 통해 API 명세 제공)

테스트: Pytest, unittest (단위 및 통합 테스트)

빌드 도구: Pip, Poetry (Python 패키지 관리 및 빌드)

유틸리티: Django Crispy Forms, Django Debug Toolbar 등 (Django 생태계 유틸리티)

CI/CD: GitHub Actions (예시)

👥 팀 동료
BE (Backend)
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
📑 프로젝트 규칙 
Branch Strategy
main / dev 브랜치를 기본으로 생성합니다.

main과 dev 브랜치로의 직접 push는 제한됩니다.

Pull Request (PR)를 생성하기 전에 최소 1인 이상의 코드 리뷰 승인이 필수입니다.

Git Convention
적절한 커밋 접두사를 사용하여 커밋 목적을 명확히 합니다.

커밋 메시지 내용은 변경 사항에 대한 구체적인 설명을 포함합니다.

메시지 내용 뒤에 관련 **이슈 번호(#이슈 번호)**를 명시하여 이슈 트래킹 시스템과 연결합니다.

접두사

설명

Feat

새로운 기능 구현

Add

에셋 파일, 리소스 등 추가

Fix

버그 수정

Docs

문서 추가 및 수정 (README, 주석 등)

Style

코드 포맷팅, 스타일 변경 (동작 변경 없음)

Refactor

코드 구조 개선 (동작 변경 없음)

Test

테스트 코드 추가 또는 수정

Deploy

배포 관련 작업

Conf

빌드, 환경 설정 변경

Chore

기타 작업 (위 분류에 해당하지 않는 작업)


Sheets로 내보내기
Pull Request (PR)
Title: [Feat] 홈 페이지 구현과 같이 [접두사] 작업 내용 형식으로 작성합니다.

PR Type: 위 Git Convention의 접두사 중 하나를 선택합니다.

Description: 해당 PR에서 수행한 구체적인 작업 내용을 상세히 작성합니다. 필요하다면 관련 스크린샷이나 GIF 이미지를 첨부하면 이해도를 높일 수 있습니다. 👍

Discussion: PR 승인 전 논의가 필요한 사항이나 질문을 작성합니다.

Code Convention
BE (백엔드)
패키지명: 전체 소문자를 사용합니다. (예: com.example.project.domain.member)

클래스명, 인터페이스명: CamelCase를 사용합니다.

클래스 이름: 역할이 명확한 명사를 사용합니다.

상수명: SNAKE_CASE (모두 대문자, 단어는 언더스코어 _로 연결)를 사용합니다.

접미사 통일: Controller, Service, Dto, Repository, Mapper와 같은 계층별 접미사를 클래스명 뒤에 일관성 있게 붙입니다. (예: MemberController, MemberService)

Service 계층 메서드명: create, update, find, delete 등 CRUD 작업에 맞는 동사로 통일합니다. (예: createMember, findMemberById)

Test 클래스: 클래스명 앞에 Test 접두사를 사용합니다. (예: TestMemberService)

Communication Rules
주요 소통 채널: Discord를 통해 실시간 소통 및 중요 공지를 진행합니다.

정기 회의: 매주 주 5일 (월,화,수,목,금) 10시 15분에 간단한 회의 진행
📋 Documents
📜 API 명세서: https://www.notion.so/API-209caf5650aa81788822c3094c8d4d80

📜 요구사항 정의서: https://docs.google.com/spreadsheets/d/160YZn8-2RPGI8gRJQiHObgKXF0VQn1DiIjJp6aPkFic/edit?gid=0#gid=0

📜 ERD (개체-관계 다이어그램): https://www.notion.so/ERD-209caf5650aa812a913ccc3aad08aba8

📜 테이블 명세서: https://www.notion.so/209caf5650aa8152a00cd26e4bb05f7a

📜 화면 정의서 
   User : https://www.figma.com/design/ZM6OVhYKhH30XTPKMC7BaC/%EC%9D%B5%EC%8A%A4%ED%84%B4%EC%8B%AD--user-design-?node-id=23-3&p=f&t=UeVTlWEtia0pJqTb-0
   Admin : https://www.figma.com/design/QmpoIuImIkAtVMHbH7HGg1/%EC%9D%B5%EC%8A%A4%ED%84%B4%EC%8B%AD--admin-design-?node-id=0-1&p=f&t=Elply8Zo81rjKsrs-0