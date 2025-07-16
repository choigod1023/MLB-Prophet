from mlb_utils import (
    get_today_boxscore_era_with_stats,
    get_recent_data,
    compare_rf_xgb_decision_improved,
    analyze_and_report_performance,
    load_csv_data,
    list_available_csv_files,
    check_and_update_csv_data,
    get_actual_results_for_date
)
import pandas as pd
from datetime import datetime

# 이하 CLI 입출력(print/input/진행률 등)만 남기고, 데이터/예측/분석/MLB API/CSV 관련은 전부 mlb_utils.py 함수 호출로 대체
# 예: df = load_csv_data(filename), predictions = compare_rf_xgb_decision_improved(...), 등
# 기존 중복 함수/로직/print/input 전부 제거됨

