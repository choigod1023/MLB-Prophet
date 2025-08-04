# Python 3.9 기반 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir numpy==1.24.4
RUN pip install --no-cache-dir gunicorn==21.2.0

# 모든 파일을 한 번에 복사
COPY . .

# 파일 존재 확인
RUN ls -la /app/
RUN echo "=== 중요 파일들 확인 ==="
RUN ls -la /app/gunicorn.conf.py || echo "gunicorn.conf.py 없음"
RUN ls -la /app/mlb_dashboard.py || echo "mlb_dashboard.py 없음"
RUN ls -la /app/mlb_utils.py || echo "mlb_utils.py 없음"

# 포트 5000 노출
EXPOSE 5000

# 환경 변수 설정
ENV FLASK_APP=mlb_dashboard.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 애플리케이션 실행 (gunicorn 사용)
CMD ["sh", "-c", "pwd && ls -la && echo '=== gunicorn 실행 ===' && python -c 'import sys; print(sys.path)' && gunicorn --config gunicorn.conf.py mlb_dashboard:app"] 