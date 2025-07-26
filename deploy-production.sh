#!/bin/bash

echo "🚀 MLB Backend 프로덕션 배포 시작..."

# 1. 필요한 디렉토리 생성
echo "📁 디렉토리 생성 중..."
mkdir -p data logs

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

# 4. 프로덕션 환경 변수 설정
echo "⚙️ 프로덕션 환경 설정..."
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# 5. 도커 이미지 빌드 (프로덕션용)
echo "🐳 프로덕션 도커 이미지 빌드 중..."
$DOCKER_CMD build --no-cache -t mlb-backend:production .

# 6. 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 정리 중..."
$COMPOSE_CMD down

# 7. 새 컨테이너 시작 (프로덕션 모드)
echo "▶️ 프로덕션 컨테이너 시작 중..."
$COMPOSE_CMD up -d

# 8. 상태 확인
echo "✅ 프로덕션 배포 완료! 컨테이너 상태 확인 중..."
$COMPOSE_CMD ps

# 9. 로그 확인
echo "📊 로그 확인 중..."
$COMPOSE_CMD logs --tail=20 mlb-backend

echo ""
echo "🌐 프로덕션 서버가 http://localhost:5000 에서 실행 중입니다."
echo "📊 실시간 로그 확인: $COMPOSE_CMD logs -f mlb-backend"
echo "🛑 서버 중지: $COMPOSE_CMD down"
echo "🔍 헬스체크: curl http://localhost:5000/" 