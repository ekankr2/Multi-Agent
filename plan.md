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
- [ ] test_user_repository_find_by_google_id_not_found: 존재하지 않는 google_id 조회 시 None 반환 AIS-9
- [ ] test_user_repository_update: User 정보 업데이트 AIS-10

#### 1.3 User Use Cases
- [ ] test_register_or_login_user_new_user: 새로운 Google 사용자 자동 회원가입
- [ ] test_register_or_login_user_existing_user: 기존 사용자 로그인 시 last_login_at 갱신
- [ ] test_get_user_by_id: ID로 사용자 조회
- [ ] test_get_user_by_id_not_found: 존재하지 않는 ID 조회 시 예외 발생
- [ ] test_update_user_profile: 사용자 프로필 업데이트 (이름 변경)

#### 1.4 User Web Adapter (REST API)
- [ ] test_get_me_endpoint_authenticated: GET /user/me - 인증된 사용자 정보 조회 성공
- [ ] test_get_me_endpoint_unauthenticated: GET /user/me - 인증되지 않은 요청 시 401 에러
- [ ] test_patch_me_endpoint: PATCH /user/me - 사용자 정보 수정 성공
- [ ] test_patch_me_endpoint_unauthenticated: PATCH /user/me - 인증되지 않은 요청 시 401 에러

#### 1.5 User Domain Integration with OAuth
- [ ] test_google_oauth_callback_creates_user: Google OAuth 콜백 시 User 자동 생성
- [ ] test_google_oauth_callback_updates_last_login: 기존 User의 경우 last_login_at 갱신

---

### Phase 2: Board Domain (인증 게시판 도메인)

#### 2.1 Board Domain Entity
- [ ] test_board_creation_with_user_id: Board 엔티티 생성 시 user_id 포함
- [ ] test_board_has_title_and_content: Board는 title(최대 255자), content(최대 2000자) 포함
- [ ] test_board_has_timestamps: Board 생성 시 created_at, updated_at 자동 설정
- [ ] test_board_update_title_and_content: Board 수정 시 updated_at 갱신
- [ ] test_board_title_max_length_validation: title이 255자 초과 시 예외 발생
- [ ] test_board_content_max_length_validation: content가 2000자 초과 시 예외 발생

#### 2.2 Board Repository Port & Implementation
- [ ] test_board_repository_save: BoardRepository가 Board를 데이터베이스에 저장
- [ ] test_board_repository_find_by_id: id로 Board 조회
- [ ] test_board_repository_find_by_id_not_found: 존재하지 않는 Board 조회 시 None 반환
- [ ] test_board_repository_find_all: 전체 Board 목록 조회 (최신순 정렬)
- [ ] test_board_repository_update: Board 업데이트
- [ ] test_board_repository_delete: Board 삭제

#### 2.3 Board Use Cases with Authorization
- [ ] test_create_board_authenticated: 인증된 사용자가 게시글 작성
- [ ] test_create_board_unauthenticated: 인증되지 않은 사용자는 게시글 작성 불가
- [ ] test_get_board_list_authenticated: 인증된 사용자가 게시글 목록 조회
- [ ] test_get_board_list_unauthenticated: 인증되지 않은 사용자는 목록 조회 불가
- [ ] test_get_board_detail_authenticated: 인증된 사용자가 게시글 상세 조회
- [ ] test_get_board_detail_not_found: 존재하지 않는 게시글 조회 시 예외 발생
- [ ] test_update_board_by_author: 작성자가 본인 게시글 수정 성공
- [ ] test_update_board_by_non_author: 다른 사용자가 수정 시도 시 403 에러
- [ ] test_delete_board_by_author: 작성자가 본인 게시글 삭제 성공
- [ ] test_delete_board_by_non_author: 다른 사용자가 삭제 시도 시 403 에러

#### 2.4 Board Response with User Information
- [ ] test_board_response_includes_author_info: Board 응답에 작성자 정보(name, profile_picture) 포함
- [ ] test_board_list_response_includes_author_info: Board 목록 응답 각 항목에 작성자 정보 포함

#### 2.5 Board Web Adapter (REST API)
- [ ] test_create_board_endpoint: POST /board - 게시글 작성 성공
- [ ] test_create_board_endpoint_unauthenticated: POST /board - 인증 안 된 요청 시 401 에러
- [ ] test_create_board_endpoint_validation_error: POST /board - 유효성 검증 실패 시 422 에러
- [ ] test_get_board_list_endpoint: GET /board - 게시글 목록 조회 성공
- [ ] test_get_board_list_endpoint_unauthenticated: GET /board - 인증 안 된 요청 시 401 에러
- [ ] test_get_board_detail_endpoint: GET /board/{board_id} - 게시글 상세 조회 성공
- [ ] test_get_board_detail_endpoint_not_found: GET /board/{board_id} - 없는 게시글 조회 시 404 에러
- [ ] test_update_board_endpoint: PATCH /board/{board_id} - 게시글 수정 성공
- [ ] test_update_board_endpoint_forbidden: PATCH /board/{board_id} - 작성자 아닌 경우 403 에러
- [ ] test_delete_board_endpoint: DELETE /board/{board_id} - 게시글 삭제 성공
- [ ] test_delete_board_endpoint_forbidden: DELETE /board/{board_id} - 작성자 아닌 경우 403 에러

---

### Phase 3: Session & Authentication Middleware

#### 3.1 Session Validation Middleware
- [ ] test_session_middleware_valid_session: 유효한 세션으로 요청 시 user_id 컨텍스트에 주입
- [ ] test_session_middleware_invalid_session: 유효하지 않은 세션 토큰 시 401 에러
- [ ] test_session_middleware_missing_session: 세션 쿠키 없이 요청 시 401 에러
- [ ] test_session_middleware_expired_session: 만료된 세션 시 401 에러

#### 3.2 Get Current User Dependency
- [ ] test_get_current_user_from_session: 세션에서 현재 사용자 조회
- [ ] test_get_current_user_session_user_not_found: 세션은 있지만 User가 DB에 없는 경우 예외 발생

---

### Phase 4: Integration & E2E Tests

#### 4.1 User Domain Integration
- [ ] test_user_full_workflow: 사용자 등록 → 조회 → 프로필 수정 전체 플로우
- [ ] test_google_oauth_to_user_creation_flow: Google OAuth 콜백 → User 생성 → 세션 생성 플로우

#### 4.2 Board Domain Integration
- [ ] test_board_full_workflow_single_user: 게시글 작성 → 조회 → 수정 → 삭제 전체 플로우
- [ ] test_board_authorization_workflow: 사용자 A가 작성, 사용자 B가 수정/삭제 시도 시 403 에러

#### 4.3 End-to-End Scenarios
- [ ] test_e2e_google_login_and_create_board: Google 로그인 → 게시글 작성 → 목록 조회
- [ ] test_e2e_multiple_users_board_interaction: 여러 사용자가 게시글 작성 및 각자 게시글 수정/삭제

---

## Notes
- 각 테스트는 독립적으로 실행 가능해야 함
- 테스트는 작은 단위로 나누어 하나씩 구현
- Red → Green → Refactor 사이클 엄격히 준수
- 구조적 변경(Tidy)과 기능적 변경(Behavioral)은 별도 커밋으로 분리
- 모든 테스트가 통과한 후에만 커밋