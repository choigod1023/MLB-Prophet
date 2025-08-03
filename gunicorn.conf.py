# Gunicorn 설정 파일
import multiprocessing
import os
import sys

# Python 경로 설정
sys.path.insert(0, '/app')

# 바인딩할 주소와 포트
bind = "0.0.0.0:5000"

# 워커 프로세스 수 (CPU 코어 수 * 2 + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# 워커 타입
worker_class = "sync"

# 타임아웃 설정 (초)
timeout = 120
keepalive = 2

# 로그 설정
accesslog = "-"  # stdout으로 출력
errorlog = "-"   # stderr로 출력
loglevel = "info"

# 프로세스 이름
proc_name = "mlb-dashboard"

# 최대 요청 수 (메모리 누수 방지)
max_requests = 1000
max_requests_jitter = 50

# 워커 재시작 전 대기 시간
graceful_timeout = 30

# 환경 변수
raw_env = [
    "FLASK_APP=mlb_dashboard.py",
    "FLASK_ENV=production",
    "PYTHONUNBUFFERED=1",
    "PYTHONPATH=/app"
]

# 보안 설정
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 디버깅을 위한 설정
preload_app = False
reload = False 