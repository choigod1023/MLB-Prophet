#!/bin/bash

echo "🚀 리눅스 서버 초기 설정 시작..."

# OS 감지
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "OS 감지 실패"
    exit 1
fi

echo "📋 OS: $OS $VER"

# Ubuntu/Debian
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    echo "🔧 Ubuntu/Debian 패키지 설치 중..."
    
    # 시스템 업데이트
    sudo apt update && sudo apt upgrade -y
    
    # 필수 패키지 설치
    sudo apt install -y \
        curl \
        wget \
        git \
        unzip \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    # Docker 설치
    echo "🐳 Docker 설치 중..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Node.js 설치
    echo "📦 Node.js 설치 중..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # 방화벽 설정
    echo "🔥 방화벽 설정 중..."
    sudo ufw allow 22/tcp
    sudo ufw allow 5000/tcp
    sudo ufw --force enable

# CentOS/RHEL
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
    echo "🔧 CentOS/RHEL 패키지 설치 중..."
    
    # 시스템 업데이트
    sudo yum update -y
    
    # 필수 패키지 설치
    sudo yum install -y \
        curl \
        wget \
        git \
        unzip \
        gcc \
        gcc-c++ \
        make \
        yum-utils \
        epel-release
    
    # Docker 설치
    echo "🐳 Docker 설치 중..."
    sudo yum install -y yum-utils
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Node.js 설치
    echo "📦 Node.js 설치 중..."
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    sudo yum install -y nodejs
    
    # 방화벽 설정
    echo "🔥 방화벽 설정 중..."
    sudo firewall-cmd --permanent --add-port=22/tcp
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload

else
    echo "❌ 지원하지 않는 OS: $OS"
    exit 1
fi

# Docker 서비스 시작
echo "🚀 Docker 서비스 시작 중..."
sudo systemctl start docker
sudo systemctl enable docker

# 사용자를 docker 그룹에 추가
echo "👤 사용자를 docker 그룹에 추가 중..."
sudo usermod -aG docker $USER

# Git 설정
echo "📝 Git 설정 중..."
git config --global user.name "MLB Backend"
git config --global user.email "mlb@example.com"

# 설치 확인
echo "✅ 설치 확인 중..."
echo "Docker 버전:"
docker --version
echo "Node.js 버전:"
node --version
echo "npm 버전:"
npm --version
echo "Git 버전:"
git --version

echo "🎉 설치 완료!"
echo "⚠️  재로그인 후 docker 명령어를 사용할 수 있습니다."
echo "📋 다음 명령어로 배포하세요:"
echo "   ./deploy.sh" 