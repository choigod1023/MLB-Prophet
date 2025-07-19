#!/bin/bash

echo "🚀 MLB Backend Docker 배포 시작..."

# 1. 프론트엔드 빌드 (TypeScript 컴파일러 확인 후)
echo "📦 프론트엔드 빌드 중..."
cd mlb-frontend

# TypeScript가 설치되어 있는지 확인
if ! command -v tsc &> /dev/null; then
    echo "⚠️ TypeScript가 설치되지 않았습니다. npm으로 설치 중..."
    npm install -g typescript
fi

# 빌드 실행
npm run build
cd ..

# 2. 필요한 디렉토리 생성
echo "📁 디렉토리 생성 중..."
mkdir -p data logs

# 3. Docker 권한 확인
echo "🔐 Docker 권한 확인 중..."
if ! docker info &> /dev/null; then
    echo "⚠️ Docker 권한이 없습니다. sudo를 사용합니다."
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker-compose"
else
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker-compose"
fi

# 4. 도커 이미지 빌드
echo "🐳 도커 이미지 빌드 중..."
$DOCKER_CMD build -t mlb-backend .

# 5. 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 정리 중..."
$COMPOSE_CMD down

# 6. 새 컨테이너 시작
echo "▶️ 새 컨테이너 시작 중..."
$COMPOSE_CMD up -d

# 7. 상태 확인
echo "✅ 배포 완료! 컨테이너 상태 확인 중..."
$COMPOSE_CMD ps

echo "🌐 서버가 http://localhost:5000 에서 실행 중입니다."
echo "📊 로그 확인: $COMPOSE_CMD logs -f mlb-backend"
echo "🛑 서버 중지: $COMPOSE_CMD down" 