#!/bin/bash

echo "🚀 중앙 Nginx + 멀티 서비스 배포 시작..."

# 1. 필요한 디렉토리 생성
echo "📁 디렉토리 생성 중..."
mkdir -p data logs nginx/logs nginx/ssl web api

# 2. Docker 권한 확인
echo "🔐 Docker 권한 확인 중..."
if ! docker info &> /dev/null; then
    echo "⚠️ Docker 권한이 없습니다. sudo를 사용합니다."
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker-compose"
else
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker-compose"
fi

# 3. Docker 캐시/이미지/볼륨 완전 정리
echo "🧹 Docker 캐시/이미지/볼륨 정리 중..."
$DOCKER_CMD system prune -a --volumes -f

# 4. 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 정리 중..."
$COMPOSE_CMD -f nginx-proxy.yml down

# 5. 중앙 Nginx + 모든 서비스 시작
echo "▶️ 중앙 Nginx + 멀티 서비스 시작 중..."
$COMPOSE_CMD -f nginx-proxy.yml up -d --build

# 6. 상태 확인
echo "✅ 배포 완료! 컨테이너 상태 확인 중..."
$COMPOSE_CMD -f nginx-proxy.yml ps

# 7. 로그 확인
echo "📊 로그 확인 중..."
$COMPOSE_CMD -f nginx-proxy.yml logs --tail=10 nginx-proxy

echo ""
echo "🌐 중앙 Nginx가 http://localhost 에서 실행 중입니다."
echo ""
echo "📱 서비스 접속 URL:"
echo "   - MLB 서비스: http://localhost/mlb/"
echo ""
echo "📊 실시간 로그 확인:"
echo "   - 전체 로그: $COMPOSE_CMD -f nginx-proxy.yml logs -f"
echo "   - Nginx 로그: $COMPOSE_CMD -f nginx-proxy.yml logs -f nginx-proxy"
echo "   - MLB 로그: $COMPOSE_CMD -f nginx-proxy.yml logs -f mlb-backend"
echo ""
echo "🛑 서비스 중지: $COMPOSE_CMD -f nginx-proxy.yml down" 