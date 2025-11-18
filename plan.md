# TDD Implementation Plan

## Sprint Goal
구글 인증 기반 헥사고날 아키텍처에서 사용자 도메인(User Domain)과 인증된 사용자가 사용할 게시판 도메인(Board Domain) 구현

## Test Implementation Order

### Phase 1: User Domain (사용자 도메인)

#### 1.1 User Domain Entity
- [x] test_user_creation_with_google_info: User 엔티티 생성 시 Google 정보(google_id, email, name, profile_picture) 저장 AIS-2
- [x] test_user_has_timestamps: User 엔티티 생성 시 created_at, updated_at, last_login_at 자동 설정 AIS-3
- [x] test_user_update_name: User 이름 업데이트 시 updated_at 갱신 AIS-4
- [x] test_user_update_last_login: 로그인 시 last_login_at 갱신 AIS-5

#### 1.2 User Repository Port & Implementation
- [x] test_user_repository_save: UserRepository가 User를 데이터베이스에 저장 AIS-6
- [x] test_user_repository_find_by_google_id: google_id로 User 조회 AIS-7
- [x] test_user_repository_find_by_id: id로 User 조회 AIS-8
- [x] test_user_repository_update: User 정보 업데이트 AIS-9

#### 1.3 User Use Cases
- [x] test_register_or_login_user_new_user: 새로운 Google 사용자 자동 회원가입 AIS-10
- [x] test_register_or_login_user_existing_user: 기존 사용자 로그인 시 last_login_at 갱신 AIS-11
- [x] test_get_user_by_id: ID로 사용자 조회 AIS-12
- [x] test_get_user_by_id_not_found: 존재하지 않는 ID 조회 시 예외 발생 AIS-13
- [x] test_update_user_profile: 사용자 프로필 업데이트 (이름 변경) AIS-14

#### 1.4 User Web Adapter (REST API)

**GET /user/me API 구현**
- [x] test_get_me_endpoint_authenticated: GET /user/me - 인증된 사용자 정보 조회 성공 AIS-15
- [x] test_get_me_endpoint_unauthenticated: GET /user/me - 인증되지 않은 요청 시 401 에러

**PATCH /user/me API 구현**
- [x] test_patch_me_endpoint: PATCH /user/me - 사용자 정보 수정 성공 AIS-16
- [x] test_patch_me_endpoint_unauthenticated: PATCH /user/me - 인증되지 않은 요청 시 401 에러 AIS-16

#### 1.5 User Domain Integration with OAuth

**Google OAuth 콜백 처리**
- [x] test_google_oauth_callback_creates_user: Google OAuth 콜백 시 User 자동 생성 AIS-17
- [x] test_google_oauth_callback_updates_last_login: 기존 User의 경우 last_login_at 갱신 AIS-17

---

### Phase 2: Board Domain (인증 게시판 도메인)

> **백로그 정책 변경**: Phase 2부터는 기능 단위(Vertical Slice)로 백로그를 통합합니다.
> - Phase 1 (User Domain)은 이미 개별 백로그로 진행 중이므로 그대로 유지
> - Phase 2부터는 **기능별**(생성/조회/수정/삭제)로 하나의 백로그로 통합
> - 각 백로그 안에 Domain + Use Case + Repository + Adapter가 모두 포함

#### 2.1 게시글 생성 기능
**[백로그 AIS-18] Board 생성 기능 전체 구현 (Domain → Use Case → Repository → API)**

- [x] test_board_creation_with_user_id: Board 엔티티 생성 시 user_id 포함
- [x] test_board_has_title_and_content: Board는 title(최대 255자), content(최대 2000자) 포함
- [x] test_board_has_timestamps: Board 생성 시 created_at, updated_at 자동 설정
- [x] test_board_title_max_length_validation: title이 255자 초과 시 예외 발생
- [x] test_board_content_max_length_validation: content가 2000자 초과 시 예외 발생
- [x] test_board_repository_save: BoardRepository가 Board를 데이터베이스에 저장
- [x] test_create_board_authenticated: 인증된 사용자가 게시글 작성
- [x] test_create_board_unauthenticated: 인증되지 않은 사용자는 게시글 작성 불가
- [x] test_create_board_endpoint: POST /board - 게시글 작성 성공
- [x] test_create_board_endpoint_unauthenticated: POST /board - 인증 안 된 요청 시 401 에러
- [x] test_create_board_endpoint_validation_error: POST /board - 유효성 검증 실패 시 422 에러

#### 2.2 게시글 목록 조회 기능
**[백로그 AIS-19] Board 목록 조회 기능 전체 구현**

- [x] test_board_repository_find_all: 전체 Board 목록 조회 (최신순 정렬)
- [x] test_get_board_list_authenticated: 인증된 사용자가 게시글 목록 조회
- [x] test_get_board_list_unauthenticated: 인증되지 않은 사용자는 목록 조회 불가
- [x] test_board_list_response_includes_author_info: Board 목록 응답 각 항목에 작성자 정보 포함
- [x] test_get_board_list_endpoint: GET /board - 게시글 목록 조회 성공
- [x] test_get_board_list_endpoint_unauthenticated: GET /board - 인증 안 된 요청 시 401 에러

#### 2.3 게시글 상세 조회 기능
**[백로그 AIS-20] Board 상세 조회 기능 전체 구현**

- [x] test_board_repository_find_by_id: id로 Board 조회
- [x] test_board_repository_find_by_id_not_found: 존재하지 않는 Board 조회 시 None 반환
- [x] test_get_board_detail_authenticated: 인증된 사용자가 게시글 상세 조회
- [x] test_get_board_detail_not_found: 존재하지 않는 게시글 조회 시 예외 발생
- [x] test_board_response_includes_author_info: Board 응답에 작성자 정보(name, profile_picture) 포함
- [x] test_get_board_detail_endpoint: GET /board/{board_id} - 게시글 상세 조회 성공
- [x] test_get_board_detail_endpoint_not_found: GET /board/{board_id} - 없는 게시글 조회 시 404 에러

#### 2.4 게시글 수정 기능
**[백로그 AIS-21] Board 수정 기능 전체 구현 (권한 검증 포함)**

- [x] test_board_update_title_and_content: Board 수정 시 updated_at 갱신
- [x] test_board_repository_update: Board 업데이트
- [x] test_update_board_by_author: 작성자가 본인 게시글 수정 성공
- [x] test_update_board_by_non_author: 다른 사용자가 수정 시도 시 403 에러
- [x] test_update_board_endpoint: PATCH /board/{board_id} - 게시글 수정 성공
- [x] test_update_board_endpoint_forbidden: PATCH /board/{board_id} - 작성자 아닌 경우 403 에러

#### 2.5 게시글 삭제 기능
**[백로그 AIS-22] Board 삭제 기능 전체 구현 (권한 검증 포함)**

- [x] test_board_repository_delete: Board 삭제
- [x] test_delete_board_by_author: 작성자가 본인 게시글 삭제 성공
- [x] test_delete_board_by_non_author: 다른 사용자가 삭제 시도 시 403 에러
- [x] test_delete_board_endpoint: DELETE /board/{board_id} - 게시글 삭제 성공
- [x] test_delete_board_endpoint_forbidden: DELETE /board/{board_id} - 작성자 아닌 경우 403 에러

---

### Phase 3: Session-Based Authentication

> **백로그 정책**: Phase 3도 기능 단위로 백로그 통합

#### 3.1 Get Current User Dependency (Session-Based)
**[백로그 AIS-24] Get Current User Dependency 구현**

- [x] test_get_current_user_from_session: 세션에서 현재 사용자 조회
- [x] test_get_current_user_session_user_not_found: 세션은 있지만 User가 DB에 없는 경우 예외 발생

#### 3.2 Session-Based Authentication Integration
**[백로그 AIS-28] 세션 기반 인증으로 전체 엔드포인트 통합 (Refactoring)**

- [x] get_current_user_from_session을 self-contained로 리팩터링 (미들웨어 제거)
- [x] Board 엔드포인트 전체를 세션 기반 인증으로 전환
- [x] User 엔드포인트 전체를 세션 기반 인증으로 전환
- [x] 테스트 인프라 구축 (mock_redis, create_session_cookie fixtures)
- [x] 모든 테스트를 쿠키 기반으로 업데이트

---

### Phase 4: Integration & E2E Tests

> **백로그 정책**: Phase 4도 기능 단위로 백로그 통합

#### 4.1 User Domain Integration
**[백로그 AIS-25] User Domain Integration Tests**

- [x] test_user_full_workflow: 사용자 등록 → 조회 → 프로필 수정 전체 플로우
- [x] test_google_oauth_to_user_creation_flow: Google OAuth 콜백 → User 생성 → 세션 생성 플로우

#### 4.2 Board Domain Integration
**[백로그 AIS-26] Board Domain Integration Tests**

- [x] test_board_full_workflow_single_user: 게시글 작성 → 조회 → 수정 → 삭제 전체 플로우
- [x] test_board_authorization_workflow: 사용자 A가 작성, 사용자 B가 수정/삭제 시도 시 403 에러

#### 4.3 End-to-End Scenarios
**[백로그 AIS-27] E2E Scenarios**

- [x] test_e2e_google_login_and_create_board: Google 로그인 → 게시글 작성 → 목록 조회
- [x] test_e2e_multiple_users_board_interaction: 여러 사용자가 게시글 작성 및 각자 게시글 수정/삭제

---

## Notes
- 각 테스트는 독립적으로 실행 가능해야 함
- 테스트는 작은 단위로 나누어 하나씩 구현
- Red → Green → Refactor 사이클 엄격히 준수
- 구조적 변경(Tidy)과 기능적 변경(Behavioral)은 별도 커밋으로 분리
- 모든 테스트가 통과한 후에만 커밋

## 백로그 정책
- **AIS 번호**: 개별 테스트 단위 트래킹 번호 (Git 커밋에 사용)
- **Phase 1 (User Domain, AIS-2~17)**: 개별 백로그 유지 (이미 진행 중)
  - 각 AIS 번호 = 1개 Notion 백로그
- **Phase 2~4 (Board/Session/Integration, AIS-18~27)**: **기능 단위(Vertical Slice)**로 백로그 통합
  - ✅ 올바른 예: "Board 생성 기능" = Domain + Use Case + Repository + API 모두 포함
  - ❌ 잘못된 예: "Board Entity 전체", "Board Repository 전체" (레이어별 분리)
  - 기능별 CRUD 단위로 백로그 생성:
    - Board 생성 (1개 백로그)
    - Board 목록 조회 (1개 백로그)
    - Board 상세 조회 (1개 백로그)
    - Board 수정 (1개 백로그)
    - Board 삭제 (1개 백로그)
- **커밋 메시지**: 계속 AIS 번호 사용 (예: [AIS-18], [AIS-19])
- **Notion 백로그**: Phase 2부터는 기능(CRUD)별로 그룹핑하여 생성