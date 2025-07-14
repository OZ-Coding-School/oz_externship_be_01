# OZ CodingSchool LMS - 백엔드

## 과정 관리 어드민 (1팀)

## 회원 기능 및 회원 관리 어드민 (2팀)

## 질의응답 기능 및 관리 어드민 (3팀)

## 커뮤니티 기능 및 관리 어드민 (4팀)

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