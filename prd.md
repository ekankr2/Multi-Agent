# Product Requirements Document (PRD)

## 프로젝트 개요

### 비전
AI Assistant 플랫폼 - 사용자가 다양한 AI 에이전트를 활용하여 작업을 수행할 수 있는 멀티 에이전트 시스템

### 최종 목표
- AI 기반 멀티 에이전트 시스템 구축
- 사용자별 맞춤형 AI Assistant 제공
- 문서 분석, 대화형 인터페이스 등 다양한 AI 기능 제공

---

## 기능 요구사항

### 1. 사용자 도메인 (User Domain)

#### 1.1 사용자 등록 및 관리
- **Google OAuth2 기반 자동 회원가입**
  - Google 계정으로 로그인 시 사용자 정보 자동 저장
  - 중복 사용자 체크 (Google ID 기반)

- **사용자 정보 관리**
  - Google 프로필 정보 저장: email, name, profile_picture
  - Google ID (sub claim) 저장
  - 가입일시, 최종 로그인 일시 기록

#### 1.2 사용자 조회 기능
- 현재 로그인한 사용자 정보 조회
- 사용자 프로필 업데이트 (이름 변경 등)

### 2. Anonymous Board (익명 게시판)

#### 2.1 기본 특성
- **인증 불필요** - 누구나 접근 가능
- 작성자 정보 없음
- 완전 익명 게시판

#### 2.2 익명 게시판 CRUD
- **게시글 작성 (Create)**
  - 제목 (최대 255자)
  - 내용 (최대 2000자)

- **게시글 목록 조회 (Read - List)**
  - 전체 게시글 목록
  - 작성일시, 수정일시 포함

- **게시글 상세 조회 (Read - Detail)**
  - 특정 게시글 상세 정보

- **게시글 삭제 (Delete)**
  - 누구나 삭제 가능

### 3. Board (인증 게시판)

#### 3.1 인증 요구사항
- **모든 API는 인증된 사용자만 접근 가능**
- 세션 검증을 통한 사용자 인증 확인

#### 3.2 인증 게시판 CRUD
- **게시글 작성 (Create)**
  - 제목 (최대 255자)
  - 내용 (최대 2000자)
  - 작성자 정보 (User ID) 자동 기록

- **게시글 목록 조회 (Read - List)**
  - 전체 게시글 목록
  - 작성자 정보 포함 (이름, 프로필 사진)
  - 작성일시, 수정일시 포함

- **게시글 상세 조회 (Read - Detail)**
  - 특정 게시글 상세 정보
  - 작성자 정보 포함

- **게시글 수정 (Update)**
  - 본인이 작성한 게시글만 수정 가능
  - 제목, 내용 수정
  - 수정일시 자동 업데이트

- **게시글 삭제 (Delete)**
  - 본인이 작성한 게시글만 삭제 가능

### 4. 인증/인가 시스템

#### 4.1 Google OAuth2 인증
- Google 로그인 리다이렉트
- Authorization Code 교환
- Access Token 발급 및 Redis 저장
- 세션 쿠키 발급 (HTTP-only, Secure)

#### 4.2 세션 관리
- Redis 기반 세션 저장 (1시간 TTL)
- 세션 검증 미들웨어
- 로그아웃 기능

#### 4.3 인가 (Authorization)
- 인증 게시판 작성자 검증
- 본인 게시글만 수정/삭제 가능

---

## 비기능 요구사항

### 1. 아키텍처
- **Hexagonal Architecture (Ports & Adapters) 패턴 준수**
  - Domain Layer: 순수 비즈니스 로직
  - Application Layer: Use Cases, Ports (인터페이스)
  - Adapter Layer: Web (REST API), Repository 구현
  - Infrastructure Layer: ORM, 외부 서비스 연동

### 2. 보안
- HTTP-only 쿠키를 통한 세션 관리
- CORS 설정 (Frontend: http://localhost:3000)
- SQL Injection 방지 (ORM 사용)
- XSS 방지 (Pydantic 검증)

### 3. 성능
- Redis 기반 세션 캐싱
- Database Connection Pooling
- 적절한 인덱싱 (user_id, created_at 등)

### 4. 확장성
- 도메인별 독립적인 모듈 구조
- Port/Adapter 패턴으로 구현체 교체 용이
- 향후 AI 에이전트 도메인 추가 용이

---

## 데이터 모델

### User (사용자)
```python
User:
  - id: int (PK, Auto Increment)
  - google_id: str (Unique, Google sub claim)
  - email: str (Unique)
  - name: str
  - profile_picture: str (URL)
  - created_at: datetime
  - last_login_at: datetime
  - updated_at: datetime
```

### AnonymousBoard (익명 게시판)
```python
AnonymousBoard:
  - id: int (PK, Auto Increment)
  - title: str (최대 255자)
  - content: str (최대 2000자)
  - created_at: datetime
  - updated_at: datetime
```

### Board (인증 게시판)
```python
Board:
  - id: int (PK, Auto Increment)
  - title: str (최대 255자)
  - content: str (최대 2000자)
  - user_id: int (FK -> User.id, NOT NULL)
  - created_at: datetime
  - updated_at: datetime
```

---

## API 엔드포인트

### Authentication API
- `GET /authentication/google` - Google 로그인 리다이렉트
- `GET /authentication/google/redirect` - OAuth2 콜백
- `GET /authentication/status` - 로그인 상태 확인
- `POST /authentication/logout` - 로그아웃

### User API
- `GET /user/me` - 현재 로그인 사용자 정보 조회 (인증 필요)
- `PATCH /user/me` - 사용자 정보 수정 (인증 필요)

### Anonymous Board API
- `POST /anonymous-board` - 익명 게시글 작성
- `GET /anonymous-board` - 익명 게시글 목록 조회
- `GET /anonymous-board/{board_id}` - 익명 게시글 상세 조회
- `DELETE /anonymous-board/{board_id}` - 익명 게시글 삭제

### Board API (인증 필요)
- `POST /board` - 게시글 작성 (인증 필요)
- `GET /board` - 게시글 목록 조회 (인증 필요)
- `GET /board/{board_id}` - 게시글 상세 조회 (인증 필요)
- `PATCH /board/{board_id}` - 게시글 수정 (작성자만)
- `DELETE /board/{board_id}` - 게시글 삭제 (작성자만)

---

## 기술 스택

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.x
- **ASGI Server**: Uvicorn

### Database & Caching
- **Database**: MySQL 8.x
- **ORM**: SQLAlchemy
- **Caching**: Redis 7.x

### Authentication
- **OAuth2 Provider**: Google OAuth2
- **Session Storage**: Redis

### AI/ML (향후 확장)
- LangChain
- OpenAI API
- Document Processing (pdfplumber, python-docx, BeautifulSoup4)

### Frontend (별도 프로젝트)
- Next.js (http://localhost:3000)

---

## 제약사항 및 가정

### 제약사항
1. 현재는 Google OAuth2만 지원 (향후 다른 Provider 추가 가능)
2. 게시판은 하나의 단일 게시판 (향후 카테고리 추가 가능)
3. 개발 환경에서는 DB 재시작 시 데이터 초기화 (lifespan에서 drop_all)

### 가정
1. 사용자는 Google 계정을 보유하고 있음
2. Frontend는 Next.js로 별도 개발 중
3. 세션 만료 시간은 1시간

---

## 향후 로드맵

### Phase 2: AI Agent 도메인
- AI Agent 실행 및 관리
- 문서 분석 기능 (PDF, Word, HTML)
- 대화형 챗봇 인터페이스

### Phase 3: Multi-Agent Orchestration
- 멀티 에이전트 오케스트레이션
- 에이전트 간 통신 및 협업
- 작업 히스토리 및 로깅
- 사용자별 Agent 설정 관리

---

## 개발 환경
```
APP_HOST=0.0.0.0
APP_PORT=33333

MySQL: localhost:3306
Redis: localhost:6379
Frontend: localhost:3000
```