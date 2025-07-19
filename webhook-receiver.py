#!/usr/bin/env python3
"""
GitHub Webhook Receiver for Auto Deployment
"""

import os
import hmac
import hashlib
import subprocess
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# GitHub Webhook Secret (GitHub 저장소 설정에서 설정)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your-webhook-secret')

# 프로젝트 디렉토리
PROJECT_DIR = os.environ.get('PROJECT_DIR', '/home/ubuntu/MLB-Proph')

@app.route('/webhook', methods=['POST'])
def webhook():
    """GitHub 웹훅 수신"""
    
    # GitHub 시그니처 확인
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return jsonify({'error': 'No signature'}), 401
    
    # 시그니처 검증
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # 이벤트 타입 확인
    event_type = request.headers.get('X-GitHub-Event')
    if event_type != 'push':
        return jsonify({'message': 'Ignored non-push event'}), 200
    
    # JSON 데이터 파싱
    try:
        payload = request.get_json()
    except Exception as e:
        return jsonify({'error': f'Invalid JSON: {e}'}), 400
    
    # main 브랜치 푸시 확인
    ref = payload.get('ref', '')
    if ref != 'refs/heads/main':
        return jsonify({'message': 'Ignored non-main branch'}), 200
    
    # 배포 실행
    try:
        deploy()
        return jsonify({'message': 'Deployment started successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Deployment failed: {e}'}), 500

def deploy():
    """실제 배포 실행"""
    print("🚀 자동 배포 시작...")
    
    # 1. 코드 업데이트
    subprocess.run(['git', 'pull', 'origin', 'main'], cwd=PROJECT_DIR, check=True)
    
    # 2. 배포 스크립트 실행
    deploy_script = os.path.join(PROJECT_DIR, 'deploy.sh')
    subprocess.run(['chmod', '+x', deploy_script], check=True)
    subprocess.run([deploy_script], cwd=PROJECT_DIR, check=True)
    
    print("✅ 배포 완료!")

@app.route('/health', methods=['GET'])
def health():
    """헬스체크 엔드포인트"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False) 