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

# 필수 파일들을 개별적으로 복사
COPY mlb_dashboard.py ./
COPY mlb_utils.py ./
COPY gunicorn.conf.py ./
COPY __init__.py ./
COPY templates/ ./templates/

# CSV 및 JSON 파일들 복사
COPY *.csv ./ 2>/dev/null || echo "No CSV files found"
COPY *.json ./ 2>/dev/null || echo "No JSON files found"

# 파일 존재 확인
RUN echo "=== 복사 후 파일 목록 확인 ===" && ls -la /app/
RUN echo "=== mlb_dashboard.py 확인 ===" && ls -la /app/mlb_dashboard.py || echo "mlb_dashboard.py 파일이 없습니다!"
RUN echo "=== 파일 내용 확인 ===" && head -5 /app/mlb_dashboard.py || echo "파일을 읽을 수 없습니다!"

# 포트 5000 노출
EXPOSE 5000

# 환경 변수 설정
ENV FLASK_APP=mlb_dashboard.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 애플리케이션 실행 (디버깅을 위해 Python으로 직접 실행)
CMD ["python", "mlb_dashboard.py"] 