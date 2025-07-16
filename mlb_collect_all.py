import time
from datetime import datetime
import pandas as pd
from mlb_utils import get_historical_game_data


def save_all_mlb_games_since(year_start, sleep_sec=0.2):
    """
    year_start부터 올해까지 모든 MLB 경기 데이터 수집해서 CSV로 저장
    - 진행률, 예상 남은 시간, 요청 속도조절 포함
    - CSV 포맷은 mlb_utils.py와 동일
    """
    year_end = datetime.today().year
    all_dfs = []
    total_games_est = (year_end - year_start + 1) * 2400  # rough estimate
    games_processed = 0
    start_time = time.time()
    for year in range(year_start, year_end + 1):
        print(f"\n{year} 시즌 데이터 수집 중...")
        try:
            start = datetime(year, 3, 1)
            end = datetime(year, 11, 30)
            df = get_historical_game_data(start, end)
        except Exception as e:
            print(f"[오류] {year} 시즌 수집 실패: {e}")
            continue
        all_dfs.append(df)
        games_processed += len(df)
        # 진행률 및 예상 시간
        elapsed = time.time() - start_time
        progress = games_processed / total_games_est
        if progress > 0:
            est_total = elapsed / progress
            est_left = est_total - elapsed
            print(f"진행률: {games_processed}/{total_games_est} ({progress*100:.1f}%)")
            print(f"경과: {elapsed/60:.1f}분, 예상 남은 시간: {est_left/60:.1f}분")
        time.sleep(sleep_sec)
    if not all_dfs:
        print("수집된 데이터가 없습니다.")
        return
    df_all = pd.concat(all_dfs, ignore_index=True)
    today_str = datetime.today().strftime('%Y%m%d')
    filename = f"mlb_{year_start}to{year_end}_{today_str}.csv"
    df_all.to_csv(filename, index=False)
    print(f"\n✅ 전체 {len(df_all)}개 경기 데이터가 {filename}에 저장되었습니다.")

if __name__ == "__main__":
    print("=== MLB 전체 시즌 데이터 수집기 ===")
    try:
        year_start = int(input("수집 시작 연도(예: 2022): ").strip())
    except Exception:
        print("잘못된 입력입니다. 2022년부터 시작합니다.")
        year_start = 2022
    save_all_mlb_games_since(year_start) 