# Python 3.9 기반 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir numpy==1.24.4
RUN pip install --no-cache-dir gunicorn==21.2.0

# 애플리케이션 파일들 복사
COPY . .
COPY *.csv .
COPY *.json .
COPY templates/ templates/
COPY gunicorn.conf.py .

# 포트 5000 노출
EXPOSE 5000

# 환경 변수 설정
ENV FLASK_APP=mlb_dashboard.py
ENV FLASK_ENV=production

# 애플리케이션 실행 (프로덕션용 gunicorn 사용)
CMD ["gunicorn", "-c", "gunicorn.conf.py", "mlb_dashboard:app"] 