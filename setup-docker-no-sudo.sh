#!/bin/bash

echo "Docker 소켓 권한 문제 해결 중..."

# 현재 사용자 확인
echo "현재 사용자: $USER"

# 1. docker 그룹이 존재하는지 확인하고 생성
echo "1. docker 그룹 확인 및 생성..."
if ! getent group docker > /dev/null 2>&1; then
    echo "docker 그룹이 존재하지 않습니다. 생성 중..."
    sudo groupadd docker
else
    echo "docker 그룹이 이미 존재합니다."
fi

# 2. 현재 사용자를 docker 그룹에 추가
echo "2. 현재 사용자를 docker 그룹에 추가..."
sudo usermod -aG docker $USER

# 3. Docker 소켓 권한 확인 및 수정
echo "3. Docker 소켓 권한 확인..."
ls -la /var/run/docker.sock

echo "Docker 소켓 권한 수정 중..."
sudo chmod 666 /var/run/docker.sock

# 4. Docker 서비스 재시작
echo "4. Docker 서비스 재시작..."
sudo systemctl restart docker

# 5. 권한 재설정
echo "5. Docker 소켓 권한 재설정..."
sudo chown root:docker /var/run/docker.sock
sudo chmod 666 /var/run/docker.sock

# 6. 현재 그룹 확인
echo "6. 현재 사용자의 그룹 확인..."
groups $USER

# 7. 테스트
echo "7. Docker 테스트..."
echo "Docker 버전:"
docker --version

echo "Docker 정보:"
docker info

echo ""
echo "설정 완료!"
echo ""
echo "만약 여전히 권한 오류가 발생한다면:"
echo "1. 로그아웃 후 다시 로그인하세요: logout"
echo "2. 또는 다음 명령어를 실행하세요: newgrp docker"
echo "3. 또는 시스템을 재부팅하세요: sudo reboot" 