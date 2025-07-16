# MLB 경기 예측 시스템

MLB-StatsAPI + 머신러닝 기반 예측 시스템 (웹/CLI 완전 분리, 공통 로직은 mlb_utils.py에 집중)

## 🚀 주요 기능

- MLB 실시간 데이터 수집 및 자동 CSV 관리
- RandomForest/XGBoost 기반 승패·스코어 예측
- 웹 대시보드(Flask) + CLI 메뉴 동시 지원
- 예측 결과/실제 결과/성능 분석 통합
- Swagger UI로 API 테스트 가능

## 🗂️ 파일 구조

```
KBO/
├── mlb_utils.py         # 모든 공통 로직 (MLB API, 예측, 분석, CSV 등)
├── mlb_dashboard.py     # 웹 대시보드 (Flask, Swagger, API)
├── mlb_cli.py           # CLI 진입점 (메뉴/입출력)
├── fix_predictions_history.py # 예측 기록 보정 유틸 (CLI)
├── mlb_collect_all.py   # 전체 시즌 데이터 수집 (CLI)
├── *.csv                # 데이터/결과 파일
├── predictions_history.json # 예측 기록
├── requirements.txt     # 의존성
└── templates/
    └── dashboard.html   # 웹 대시보드 템플릿
```

## ⚡️ 빠른 시작

### 1. 웹 대시보드 실행

```bash
pip install -r requirements.txt
python mlb_dashboard.py
```

- 브라우저에서 http://localhost:5000 접속
- Swagger UI: http://localhost:5000/apidocs (API 테스트)

### 2. CLI 실행

```bash
python mlb_cli.py
```

- 메뉴에서 오늘 예측, CSV 예측, 결과 조회, 파일 목록, 성능 분석 등 선택

### 3. 전체 시즌 데이터 수집 (CSV)

```bash
python mlb_collect_all.py
```

### 4. 예측 기록 보정

```bash
python fix_predictions_history.py
```

## 🧩 구조 및 설계

- **mlb_utils.py**: MLB API, 팀 id 매핑, CSV 로드/목록, 예측, 성능분석 등 모든 공통 함수만 존재 (입출력/웹/CLI 코드 없음)
- **mlb_dashboard.py**: Flask 기반 웹 대시보드, API/Swagger, 프론트엔드, 웹 전용 입출력만 담당
- **mlb_cli.py**: CLI 메뉴/입출력/진행률 등만 담당, 데이터/예측/분석은 전부 mlb_utils.py에서 import
- **기타 유틸**: fix_predictions_history.py, mlb_collect_all.py 등도 mlb_utils.py만 import해서 사용

## 🖥️ 주요 사용법

### 웹 대시보드

- 오늘 예측, CSV 예측, 날짜별 결과 조회, 성능 분석 등 모두 웹에서 클릭으로 가능
- Swagger UI에서 API 직접 테스트 가능

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

- Python 3.8+
- Flask, flasgger (Swagger UI)
- pandas, scikit-learn, xgboost, numpy
- MLB-StatsAPI

## 📝 라이선스/기여

- 교육/연구 목적, MLB-StatsAPI 정책 준수
- 버그/기능 제안/코드 개선 환영

---

**최종 업데이트**: 2025년 7월
**버전**: v6.0 (웹/CLI 완전 분리, mlb_utils.py 중심 구조)
