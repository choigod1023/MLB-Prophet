# Gunicorn 설정 파일
import multiprocessing
import os
import sys

# Python 경로 설정 - 현재 디렉토리를 명시적으로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

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

# 모듈 로딩 디버깅
def when_ready(server):
    print(f"=== Gunicorn 서버 준비됨 ===")
    print(f"현재 디렉토리: {os.getcwd()}")
    print(f"Python 경로: {sys.path}")
    print(f"사용 가능한 파일들: {os.listdir('.')}")
    
    # mlb_dashboard.py 파일 존재 확인
    if os.path.exists('mlb_dashboard.py'):
        print("✅ mlb_dashboard.py 파일 존재")
        with open('mlb_dashboard.py', 'r') as f:
            first_line = f.readline().strip()
            print(f"첫 번째 줄: {first_line}")
    else:
        print("❌ mlb_dashboard.py 파일 없음")
    
    try:
        import mlb_dashboard
        print("✅ mlb_dashboard 모듈 import 성공")
        print(f"모듈 위치: {mlb_dashboard.__file__}")
    except ImportError as e:
        print(f"❌ mlb_dashboard 모듈 import 실패: {e}")
        import traceback
        traceback.print_exc() 