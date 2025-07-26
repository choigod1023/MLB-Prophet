#!/bin/bash

echo "Docker Compose 버전 문제 해결 중..."

# 1. 현재 Docker Compose 버전 확인
echo "1. 현재 Docker Compose 버전 확인..."
docker-compose --version
docker compose version

# 2. Docker Compose 최신 버전 설치 (선택사항)
echo ""
echo "2. Docker Compose 최신 버전 설치 (선택사항)..."
read -p "Docker Compose를 최신 버전으로 업데이트하시겠습니까? (y/n): " update_compose

if [ "$update_compose" = "y" ]; then
    echo "Docker Compose 최신 버전 설치 중..."
    
    # 기존 docker-compose 제거
    sudo rm -f /usr/local/bin/docker-compose
    
    # 최신 버전 다운로드 및 설치
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "Docker Compose 최신 버전 설치 완료!"
fi

# 3. docker-compose.yml 파일 수정
echo ""
echo "3. docker-compose.yml 파일 수정 중..."

# 백업 생성
cp docker-compose.yml docker-compose.yml.backup
echo "백업 파일 생성: docker-compose.yml.backup"

# 버전을 3.3으로 변경
sed -i 's/version: "3.8"/version: "3.3"/' docker-compose.yml
echo "Docker Compose 버전을 3.3으로 변경했습니다."

# 4. 테스트
echo ""
echo "4. Docker Compose 테스트..."
echo "구문 검사:"
docker-compose config

echo ""
echo "서비스 시작 테스트:"
docker-compose up -d

echo ""
echo "서비스 상태 확인:"
docker-compose ps

echo ""
echo "완료!"
echo "이제 다음 명령어로 서비스를 시작할 수 있습니다:"
echo "docker-compose up -d" 