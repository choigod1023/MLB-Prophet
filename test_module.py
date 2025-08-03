#!/usr/bin/env python3
"""
도커 컨테이너 내부에서 모듈 테스트용 스크립트
"""

import sys
import os

print("=== Python 경로 확인 ===")
for path in sys.path:
    print(f"  {path}")

print("\n=== 현재 디렉토리 ===")
print(f"  {os.getcwd()}")

print("\n=== 디렉토리 내용 ===")
for file in os.listdir('.'):
    print(f"  {file}")

print("\n=== 모듈 import 테스트 ===")
try:
    import mlb_dashboard
    print("✅ mlb_dashboard 모듈 import 성공")
    print(f"  앱 객체: {mlb_dashboard.app}")
except ImportError as e:
    print(f"❌ mlb_dashboard 모듈 import 실패: {e}")

try:
    import mlb_utils
    print("✅ mlb_utils 모듈 import 성공")
except ImportError as e:
    print(f"❌ mlb_utils 모듈 import 실패: {e}")

print("\n=== 환경 변수 확인 ===")
print(f"  FLASK_APP: {os.environ.get('FLASK_APP', 'Not set')}")
print(f"  PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}") 