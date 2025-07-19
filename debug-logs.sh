#!/bin/bash

echo "🔍 Docker 컨테이너 디버깅 시작..."

# 1. 컨테이너 상태 확인
echo "📊 컨테이너 상태:"
docker-compose ps

echo ""
echo "📋 컨테이너 목록:"
docker ps -a

echo ""
echo "📄 실시간 로그 확인 (Ctrl+C로 종료):"
echo "=================================="
docker-compose logs -f mlb-backend

echo ""
echo "🔧 추가 디버깅 명령어들:"
echo "1. 컨테이너 내부 접속: docker exec -it mlb-backend bash"
echo "2. 특정 로그만 확인: docker-compose logs mlb-backend | grep ERROR"
echo "3. 최근 100줄 로그: docker-compose logs --tail=100 mlb-backend"
echo "4. 컨테이너 재시작: docker-compose restart mlb-backend"
echo "5. 컨테이너 재빌드: docker-compose up -d --build mlb-backend" 