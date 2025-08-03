#!/bin/bash

echo "🚀 MLB Backend 통합 배포 스크립트"
echo "=================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. 필요한 디렉토리 생성
print_status "디렉토리 생성 중..."
mkdir -p data logs

# 2. Docker 권한 확인
print_status "Docker 권한 확인 중..."
if ! docker info &> /dev/null; then
    print_warning "Docker 권한이 없습니다. sudo를 사용합니다."
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker-compose"
else
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker-compose"
fi

# # 3. 프론트엔드 빌드 (선택사항)
# print_status "프론트엔드 빌드 확인 중..."
# if [ -d "mlb-frontend" ]; then
#     print_status "프론트엔드 빌드 중..."
#     cd mlb-frontend
    
#     # TypeScript가 설치되어 있는지 확인
#     if ! command -v tsc &> /dev/null; then
#         print_warning "TypeScript가 설치되지 않았습니다. npm으로 설치 중..."
#         npm install -g typescript
#     fi
    
#     # 빌드 실행
#     npm run build
#     cd ..
#     print_success "프론트엔드 빌드 완료"
# else
#     print_warning "프론트엔드 디렉토리가 없습니다. 백엔드만 배포합니다."
# fi

# 4. Docker 캐시/이미지/볼륨 정리 (선택사항)
read -p "Docker 캐시를 정리하시겠습니까? (y/n): " clean_cache
if [ "$clean_cache" = "y" ]; then
    print_status "Docker 캐시/이미지/볼륨 정리 중..."
    $DOCKER_CMD system prune -a --volumes -f
    print_success "Docker 캐시 정리 완료"
fi

# 5. 프로덕션 환경 변수 설정
print_status "프로덕션 환경 설정..."
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# 6. 도커 이미지 빌드
print_status "프로덕션 도커 이미지 빌드 중..."
$DOCKER_CMD build --no-cache -t mlb-backend:production .

# 6-1. 현재 컨테이너 상태 확인
print_status "현재 컨테이너 상태 확인 중..."
$COMPOSE_CMD ps
echo ""

# 기존 컨테이너가 실행 중인지 확인
if $COMPOSE_CMD ps | grep -q "mlb-backend"; then
    print_warning "기존 컨테이너가 실행 중입니다. 정리 후 재시작합니다."
    read -p "계속하시겠습니까? (y/n): " continue_deploy
    if [ "$continue_deploy" != "y" ]; then
        print_error "배포가 취소되었습니다."
        exit 1
    fi
fi

# 7. 기존 컨테이너 중지 및 제거
print_status "기존 컨테이너 정리 중..."

# 모든 컨테이너 중지
$COMPOSE_CMD down

# 강제로 컨테이너 제거 (이름 충돌 해결)
print_status "기존 컨테이너 강제 제거 중..."
$DOCKER_CMD rm -f mlb-backend 2>/dev/null || true
$DOCKER_CMD rm -f mlb-nginx 2>/dev/null || true

# 모든 중지된 컨테이너 제거
$DOCKER_CMD container prune -f

# 네트워크 정리 (선택사항)
read -p "네트워크도 정리하시겠습니까? (y/n): " clean_network
if [ "$clean_network" = "y" ]; then
    print_status "네트워크 정리 중..."
    $DOCKER_CMD network prune -f
fi

# 8. 새 컨테이너 시작
print_status "프로덕션 컨테이너 시작 중..."
$COMPOSE_CMD up -d

# 9. 상태 확인
print_success "프로덕션 배포 완료! 컨테이너 상태 확인 중..."
$COMPOSE_CMD ps

# 10. 헬스체크
print_status "서버 헬스체크 중..."
sleep 10
if curl -f http://localhost:5000/ &> /dev/null; then
    print_success "서버가 정상적으로 실행 중입니다!"
else
    print_warning "서버 응답이 느립니다. 로그를 확인해주세요."
fi

# 11. 로그 확인
print_status "최근 로그 확인 중..."
$COMPOSE_CMD logs --tail=20 mlb-backend

# 12. 디버깅 옵션
echo ""
print_status "디버깅 옵션:"
echo "🔍 컨테이너 내부 접속: $DOCKER_CMD exec -it mlb-backend bash"
echo "📄 모듈 테스트: $DOCKER_CMD exec -it mlb-backend python test_module.py"
echo "📁 파일 목록 확인: $DOCKER_CMD exec -it mlb-backend ls -la"
echo "🐍 Python 경로 확인: $DOCKER_CMD exec -it mlb-backend python -c 'import sys; print(sys.path)'"

echo ""
echo "🌐 프로덕션 서버가 http://localhost:5000 에서 실행 중입니다."
echo ""
echo "📋 유용한 명령어들:"
echo "📊 실시간 로그 확인: $COMPOSE_CMD logs -f mlb-backend"
echo "🛑 서버 중지: $COMPOSE_CMD down"
echo "🔄 서버 재시작: $COMPOSE_CMD restart mlb-backend"
echo "🔍 컨테이너 내부 접속: $DOCKER_CMD exec -it mlb-backend bash"
echo "📁 파일 시스템 디버깅: curl http://localhost:5000/api/debug/filesystem"
echo "📄 CSV 파일 목록: curl http://localhost:5000/api/csv-files" 