# MLB Prophet - AI 기반 야구 예측 서비스

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
├── nginx/                          # Nginx 설정
│   ├── nginx.conf                  # Nginx 프록시 설정
│   ├── nginx-proxy.yml             # 프로덕션 Docker Compose
│   └── index.html                  # 소개 페이지
└── templates/
    └── dashboard.html               # 웹 대시보드 템플릿
```

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

### 데이터 & API

- **MLB-StatsAPI**: 실시간 데이터
- **CSV/JSON**: 데이터 저장
- **Swagger**: API 문서화

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
