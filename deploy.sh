#!/bin/bash

echo "🚀 MLB Backend Docker 배포 시작..."

# 1. 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cd mlb-frontend
npm run build
cd ..

# 2. 필요한 디렉토리 생성
echo "📁 디렉토리 생성 중..."
mkdir -p data logs

# 3. 도커 이미지 빌드
echo "🐳 도커 이미지 빌드 중..."
docker build -t mlb-backend .

# 4. 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 정리 중..."
docker-compose down

# 5. 새 컨테이너 시작
echo "▶️ 새 컨테이너 시작 중..."
docker-compose up -d

# 6. 상태 확인
echo "✅ 배포 완료! 컨테이너 상태 확인 중..."
docker-compose ps

echo "🌐 서버가 http://localhost:5000 에서 실행 중입니다."
echo "📊 로그 확인: docker-compose logs -f mlb-backend"
echo "🛑 서버 중지: docker-compose down" 