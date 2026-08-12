# MLB Prophet - AI 기반 야구 예측 서비스

**한국어** · [日本語](README.ja.md) · [English](README.en.md)

MLB-StatsAPI + 머신러닝 기반 예측 시스템으로, 웹 대시보드와 CLI를 모두 지원하는 완전한 야구 예측 서비스입니다.

## 🚀 주요 기능

- **실시간 데이터 분석**: MLB 실시간 데이터 수집 및 자동 CSV 관리
- **AI 예측 시스템**: RandomForest/XGBoost 기반 승패·스코어 예측
- **웹 대시보드**: Flask 기반 직관적인 웹 인터페이스
- **CLI 지원**: 명령줄에서도 모든 기능 사용 가능
- **성능 분석**: 예측 결과/실제 결과/성능 분석 통합
- **API 제공**: Swagger UI로 REST API 테스트 가능
- **프로덕션 배포**: Docker + Nginx + Gunicorn 환경 지원

## 🗂️ 프로젝트 구조

```
KBO/
├── mlb_utils.py                    # 모든 공통 로직 (MLB API, 예측, 분석, CSV 등)
├── mlb_dashboard.py                # 웹 대시보드 (Flask, Swagger, API)
├── mlb_cli.py                      # CLI 진입점 (메뉴/입출력)
├── fix_predictions_history.py      # 예측 기록 보정 유틸 (CLI)
├── mlb_collect_all.py              # 전체 시즌 데이터 수집 (CLI)
├── *.csv                           # 데이터/결과 파일
├── predictions_history.json         # 예측 기록
├── requirements.txt                 # Python 의존성
├── Dockerfile                      # Docker 이미지 설정
├── docker-compose.yml              # 개발용 Docker Compose
├── gunicorn.conf.py                # 프로덕션 WSGI 설정
├── deploy-simple.sh                # 개발 배포 스크립트
├── deploy-production.sh             # 프로덕션 배포 스크립트
├── webhook-receiver.py             # GitHub webhook 기반 자동 배포 수신기
├── webhook-receiver.service        # 위 수신기 systemd 유닛
├── nginx/                          # Nginx 설정
│   ├── nginx.conf                  # Nginx 프록시 설정
│   ├── nginx-proxy.yml             # 프로덕션 Docker Compose
│   └── index.html                  # 소개 페이지
├── templates/
│   └── dashboard.html               # Flask 웹 대시보드 템플릿
└── mlb-frontend/                   # React(Vite + TS) 프론트엔드 (Flask API 소비)
    └── src/                        # 컴포넌트·api.ts (http://localhost:5000/api 호출)
```

> 참고: 대시보드는 서버 렌더링(`templates/dashboard.html`)과 별개로, `mlb-frontend/`에
> React 19 + Vite + TypeScript 기반 SPA도 함께 두고 있습니다(`src/api.ts`가 Flask API를 호출).

## ⚡️ 빠른 시작

### 1. 개발 환경 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 웹 대시보드 실행
python mlb_dashboard.py
```

- 브라우저에서 http://localhost:5000 접속
- Swagger UI: http://localhost:5000/apidocs (API 테스트)

### 2. CLI 실행

```bash
python mlb_cli.py
```

- 메뉴에서 오늘 예측, CSV 예측, 결과 조회, 파일 목록, 성능 분석 등 선택

### 3. Docker 개발 환경

```bash
# 개발용 배포
./deploy-simple.sh
```

### 4. 프로덕션 배포

```bash
# 프로덕션 배포 (Nginx + Gunicorn)
./deploy-production.sh
```

## 🐳 Docker 배포

### 개발 환경

```bash
docker-compose up -d --build
```

### 프로덕션 환경

```bash
docker-compose -f nginx/nginx-proxy.yml up -d --build
```

## 🌐 프로덕션 환경

### 서비스 구조

- **Nginx**: 리버스 프록시 (80번 포트)
- **Gunicorn**: WSGI 서버 (4 워커)
- **Flask**: 웹 애플리케이션
- **Docker**: 컨테이너화

### 접속 URL

- **소개 페이지**: http://your-domain.com
- **MLB 서비스**: http://your-domain.com/mlb/
- **헬스체크**: http://your-domain.com/health

## 🧩 구조 및 설계

### 모듈 분리

- **mlb_utils.py**: 모든 공통 로직 (MLB API, 팀 id 매핑, CSV 로드/목록, 예측, 성능분석)
- **mlb_dashboard.py**: Flask 기반 웹 대시보드, API/Swagger, 웹 전용 입출력
- **mlb_cli.py**: CLI 메뉴/입출력/진행률 등, 데이터/예측/분석은 mlb_utils.py에서 import

### 프로덕션 최적화

- **Gunicorn**: 멀티 워커로 동시 요청 처리
- **Nginx**: 정적 파일 서빙, 로드 밸런싱
- **Docker**: 컨테이너화로 배포 일관성
- **환경 분리**: 개발/프로덕션 환경 분리

## 🖥️ 주요 사용법

### 웹 대시보드

- 오늘 예측, CSV 예측, 날짜별 결과 조회, 성능 분석 등 모두 웹에서 클릭으로 가능
- Swagger UI에서 API 직접 테스트 가능
- 실시간 데이터 업데이트 및 예측 결과 시각화

### CLI

- 메뉴 기반으로 오늘 예측, CSV 예측, 결과 조회, 파일 목록, 성능 분석 등 가능
- 모든 데이터/예측/분석 로직은 mlb_utils.py에서 처리

## 📈 예측 결과 예시

```
=== 개선된 모델 예측 결과 ===

New York Yankees vs Boston Red Sox (KST 06/25 08:00)
선발: Gerrit Cole vs Chris Sale
[RF] 홈팀 승률: 65.2% → 홈팀 우세  예상 스코어: 4 - 2
[XGB] 홈팀 승률: 62.8% → 홈팀 우세  예상 스코어: 5 - 3
```

## 🧠 예측 모델

승패(분류)와 스코어(회귀)를 함께 예측하는 머신러닝 파이프라인입니다. 핵심 로직은
모두 `mlb_utils.py`에 있으며, MLB-StatsAPI에서 수집한 경기별 박스스코어를 학습
데이터로 사용합니다.

### 1. 데이터 & 피처

MLB-StatsAPI의 박스스코어(`boxscore_data`)에서 경기 단위로 다음 지표를 수집합니다.
홈/원정 각각에 대해 **선발투수 기록 + 팀 시즌 타격/투구 지표**를 사용합니다.

| 구분 | 피처 |
|------|------|
| 선발투수 | `pitcher_era`, `pitcher_whip` |
| 팀 타격 | `ops`, `avg`, `slg` |
| 팀 투구 | `era`, `whip` |

- **Full 모드** (14개 피처): 위 7개 지표 × 홈/원정
- **Fast 모드** (6개 피처): `pitcher_era`, `ops`, `era` × 홈/원정 — 응답 속도 우선
- 결측치는 컬럼 평균으로 대치하고, `±inf`는 평균 → 0 순으로 보정합니다.
- 학습에는 최소 50경기 이상의 클린 데이터가 필요합니다(부족 시 예측 중단).
- 분류·회귀 입력은 `StandardScaler`로 표준화합니다.

### 2. 승패 예측 (분류)

같은 피처로 **RandomForest와 XGBoost 두 모델을 동시에** 학습해 결과를 비교 제시합니다
(`compare_rf_xgb_decision_improved`). 타깃은 `home_win`(홈팀 승=1).

- `RandomForestClassifier(n_estimators=100, max_depth=10)`
- `XGBClassifier(n_estimators=100, max_depth=6)`
- 출력 홈 승률은 과신 방지를 위해 **0.05 ~ 0.95로 클리핑**합니다.

### 3. 스코어 예측 (회귀)

홈/원정 득점을 각각 회귀로 예측합니다. 기본 비교용은 RF/XGB Regressor를 사용하고,
정교화된 `predict_score_with_margin`은 **XGBoost 회귀 4종**으로 점수·점수차·승률을
함께 추정합니다.

- 모델: `XGBRegressor(n_estimators=200, max_depth=8, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8)`
- 타깃: `home_score`, `away_score`, `score_margin`(=홈−원정), `home_win`
- **야구 도메인 후처리**로 모델 출력을 보정합니다:
  - 동점 예측 시 연장전 홈 어드밴티지(홈 55%)를 가중 평균
  - 점수차에 비례한 승률 조정(최대 ±40%)
  - 선발 ERA 차·팀 OPS 차에 따른 미세 조정 + 홈 어드밴티지 +2%p
  - 최종 승률은 다시 0.05 ~ 0.95로 클리핑

### 4. 베팅 기회 분석 (참고용)

`analyze_betting_opportunities`가 신뢰도(|승률−0.5|×2)와 예상 점수차를 점수화해
`강력 추천 / 추천 / 관심 / 관망` 등급과 근거를 함께 제시합니다. 실제 베팅이 아닌
모델 신뢰도 해석을 위한 참고 지표입니다.

### 5. 성능 평가 & 재현성

- `analyze_and_report_performance`: 누적 예측 vs 실제 결과로 **승패 적중률**과
  **평균 스코어 오차**(홈/원정/합계)를 산출합니다.
- 모든 모델은 `random_state=42`로 고정해 동일 입력 → 동일 출력을 보장합니다.

> ⚠️ **한계**: 현재는 시즌 누적 지표 기반의 단판 예측으로, 시간 순서 분리(walk-forward)
> 검증이나 라인업·구장·날씨 등 경기 맥락은 반영하지 않습니다. 예측은 참고용이며 향후
> 개선 대상입니다.

## 🔧 기술 스택

### 백엔드

- **Python 3.9**: 메인 개발 언어
- **Flask**: 웹 프레임워크
- **Gunicorn**: 프로덕션 WSGI 서버
- **Pandas, NumPy**: 데이터 처리
- **Scikit-learn, XGBoost**: 머신러닝

### 배포 & 운영

- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 서비스 관리
- **Nginx**: 리버스 프록시
- **Gunicorn**: 프로덕션 WSGI 서버

### 프론트엔드

- **React 19 + Vite + TypeScript**: `mlb-frontend/` SPA
- **Chart.js**: 예측/성능 시각화
- **Bootstrap, react-datepicker**: UI

### 데이터 & API

- **MLB-StatsAPI**: 실시간 데이터
- **CSV/JSON**: 데이터 저장
- **Swagger**: API 문서화

## 🔑 환경변수

코드에서 실제로 참조하는 환경변수는 다음과 같습니다(모두 기본값이 있어 미설정 시에도 동작).

| 변수 | 위치 | 설명 | 기본값 |
|------|------|------|--------|
| `FLASK_ENV` | `mlb_dashboard.py` | `development`이면 Flask debug 모드 활성화 | (미설정) |
| `WEBHOOK_SECRET` | `webhook-receiver.py` | GitHub webhook 서명 검증용 시크릿 | `your-webhook-secret` |
| `PROJECT_DIR` | `webhook-receiver.py` | 자동 배포 시 pull/재시작할 프로젝트 경로 | `/home/ubuntu/MLB-Proph` |

## 🚀 배포 가이드

### 1. 개발 환경

```bash
# 로컬 실행
python mlb_dashboard.py

# Docker 개발
./deploy-simple.sh
```

### 2. 프로덕션 환경

```bash
# 프로덕션 배포
./deploy-production.sh

# 또는 수동 배포
docker-compose -f nginx/nginx-proxy.yml up -d --build
```

### 3. 도메인 설정

- DNS A 레코드 설정 (도메인 → 서버 IP)
- nginx/nginx.conf에서 server_name 수정
- SSL 인증서 설정 (선택사항)

## 📊 성능 및 특징

### 정확도 향상

- 지속적인 모델 개선
- 데이터 품질 관리
- 예측 성과 추적

### 사용자 경험

- 직관적인 웹 인터페이스
- 실시간 데이터 업데이트
- 다양한 결과 형식 제공 (CSV, Excel, 리포트)

### 확장성

- Docker 기반 컨테이너화
- Nginx 로드 밸런싱
- 멀티 워커 아키텍처

## 🔧 유지보수

### 로그 확인

```bash
# 전체 로그
docker-compose -f nginx/nginx-proxy.yml logs -f

# 특정 서비스 로그
docker-compose -f nginx/nginx-proxy.yml logs -f mlb-backend
docker-compose -f nginx/nginx-proxy.yml logs -f nginx-proxy
```

### 서비스 관리

```bash
# 서비스 중지
docker-compose -f nginx/nginx-proxy.yml down

# 서비스 재시작
docker-compose -f nginx/nginx-proxy.yml restart

# 캐시 없이 재빌드
docker-compose -f nginx/nginx-proxy.yml up -d --build --no-cache
```

## 📝 라이선스/기여

- 교육/연구 목적, MLB-StatsAPI 정책 준수
- 버그/기능 제안/코드 개선 환영

---

**최종 업데이트**: 2025년 7월  
**버전**: v7.0 (Docker + Nginx + 프로덕션 환경 지원)  
**라이선스**: MIT License

---

## 👤 기여도 & 개발 환경

| 항목 | 내용 |
|---|---|
| **기여 비율** | **100%** (단독 개발) |
| **커밋** | 59 / 59 (본인 / 전체 사람 커밋) |
| **참여 인원** | 1명 |
| **AI 코딩 도구** | Claude Code |

<sub>집계 기준(2026-08-12 스냅샷): origin의 **모든 브랜치**에서 도달 가능한 커밋(머지 커밋·빈 커밋 제외), 커밋 author 이메일 기준이며 동일인의 여러 이메일은 하나로 합산, 봇·자동화 커밋은 제외했습니다.</sub>
