import sys
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
from datetime import datetime
import pandas as pd

def print_menu():
    print("\n=== MLB 예측 CLI ===")
    print("1. 오늘 경기 예측")
    print("2. CSV 파일로 예측")
    print("3. 날짜별 실제 결과 조회")
    print("4. 사용 가능한 CSV 파일 목록")
    print("5. 예측 성능 분석")
    print("0. 종료")

def cli_predict_today():
    print("[오늘 경기 예측]")
    df_today = get_today_boxscore_era_with_stats()
    df_hist = get_recent_data(days=30)
    preds = compare_rf_xgb_decision_improved(df_hist, df_today)
    print(pd.DataFrame(preds))

def cli_predict_csv():
    print("[CSV 파일로 예측]")
    files = list_available_csv_files()
    for i, f in enumerate(files):
        print(f"{i+1}. {f}")
    idx = int(input("파일 번호 선택: ")) - 1
    filename = files[idx]
    df = load_csv_data(filename)
    df_hist = get_recent_data(days=30)
    preds = compare_rf_xgb_decision_improved(df_hist, df)
    print(pd.DataFrame(preds))

def cli_check_results():
    date_str = input("조회할 날짜 (YYYY-MM-DD): ").strip()
    results = get_actual_results_for_date(date_str)
    print(pd.DataFrame(results))

def cli_list_csv():
    files = list_available_csv_files()
    print("[사용 가능한 CSV 파일]")
    for f in files:
        print(f)

def cli_performance():
    print("[예측 성능 분석]")
    # 예시: 최근 예측/실제 결과 불러와서 분석
    date_str = input("분석할 날짜 (YYYY-MM-DD, Enter시 오늘): ").strip()
    if not date_str:
        date_str = datetime.today().strftime('%Y-%m-%d')
    preds = []  # 실제로는 예측 결과 파일/DB에서 불러와야 함
    actuals = get_actual_results_for_date(date_str)
    if preds and actuals:
        report = analyze_and_report_performance(preds, actuals)
        print(report)
    else:
        print("예측/실제 결과 데이터가 부족합니다.")

def main():
    while True:
        print_menu()
        cmd = input("메뉴 선택: ").strip()
        if cmd == '1':
            cli_predict_today()
        elif cmd == '2':
            cli_predict_csv()
        elif cmd == '3':
            cli_check_results()
        elif cmd == '4':
            cli_list_csv()
        elif cmd == '5':
            cli_performance()
        elif cmd == '0':
            print("종료합니다.")
            sys.exit(0)
        else:
            print("잘못된 입력입니다.")

if __name__ == '__main__':
    main() 