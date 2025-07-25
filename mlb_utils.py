import statsapi
import pandas as pd
from datetime import datetime, timedelta
import os
import numpy as np
import pytz
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# === MLB API 유틸 ===
def get_team_name_to_id(days_back=7):
    """최근 N일간 MLB 팀 이름→id 매핑 딕셔너리 생성 (pure)"""
    today = datetime.now()
    name_to_id = {}
    for i in range(days_back):
        day = today - timedelta(days=i)
        date_str = day.strftime('%Y-%m-%d')
        schedule = statsapi.schedule(sportId=1, start_date=date_str, end_date=date_str)
        for g in schedule:
            name_to_id[g['home_name']] = g['home_id']
            name_to_id[g['away_name']] = g['away_id']
    return name_to_id

def get_actual_results_for_date(date_str):
    """특정 날짜의 실제 경기 결과(MLB API) 반환 (pure)"""
    try:
        kst = pytz.timezone('Asia/Seoul')
        utc = pytz.UTC
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_obj = kst.localize(date_obj)
        else:
            date_obj = date_str
        utc_date = date_obj.astimezone(utc)
        date_str_utc = utc_date.strftime('%Y-%m-%d')
        schedule = statsapi.schedule(sportId=1, start_date=date_str_utc, end_date=date_str_utc)
        name_to_id = {}
        for g in schedule:
            name_to_id[g['home_name']] = g['home_id']
            name_to_id[g['away_name']] = g['away_id']
        actual_results = []
        for game in schedule:
            if game['status'] == 'Final':
                home_id = game.get('home_id') or name_to_id.get(game['home_name'])
                away_id = game.get('away_id') or name_to_id.get(game['away_name'])
                actual_results.append({
                    'home_team': game['home_name'],
                    'away_team': game['away_name'],
                    'home_id': home_id,
                    'away_id': away_id,
                    'home_score': game['home_score'],
                    'away_score': game['away_score'],
                    'winner': 'home' if game['home_score'] > game['away_score'] else 'away',
                    'game_date': game['game_date']
                })
        return actual_results
    except Exception:
        return []

def get_last_5games_result_str(team_id):
    """특정 팀의 최근 5경기 결과 문자열 (pure)"""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=10)
    schedule = statsapi.schedule(
        team=team_id,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    games = sorted(schedule, key=lambda x: x['game_date'], reverse=True)
    results = []
    for game in games:
        is_home = (game['home_id'] == team_id)
        team_score = game['home_score'] if is_home else game['away_score']
        opp_score = game['away_score'] if is_home else game['home_score']
        if game['status'] != 'Final':
            continue
        if team_score > opp_score:
            results.append('W')
        elif team_score < opp_score:
            results.append('L')
        else:
            results.append('T')
        if len(results) == 5:
            break
    return ', '.join(results[::-1])

def get_historical_game_data(start_date, end_date):
    """과거 경기 데이터(MLB API) 수집 (pure)"""
    schedule = statsapi.schedule(
        sportId=1,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    historical_data = []
    for game in schedule:
        if game['status'] != 'Final':
            continue
        game_id = game['game_id']
        game_date = game['game_date']
        try:
            time.sleep(0.1)
            box = statsapi.boxscore_data(game_id)
            # 홈팀 선발투수
            home_pitcher_name = home_pitcher_era = home_pitcher_whip = None
            for player in box['home']['players'].values():
                if player['position']['abbreviation'] == 'P':
                    stats = player['seasonStats']['pitching']
                    era = stats.get('era')
                    whip = stats.get('whip')
                    if era and era != '-.--':
                        home_pitcher_name = player['person']['fullName']
                        home_pitcher_era = float(era)
                        home_pitcher_whip = float(whip) if whip and whip != '-.--' else None
                        break
            # 원정팀 선발투수
            away_pitcher_name = away_pitcher_era = away_pitcher_whip = None
            for player in box['away']['players'].values():
                if player['position']['abbreviation'] == 'P':
                    stats = player['seasonStats']['pitching']
                    era = stats.get('era')
                    whip = stats.get('whip')
                    if era and era != '-.--':
                        away_pitcher_name = player['person']['fullName']
                        away_pitcher_era = float(era)
                        away_pitcher_whip = float(whip) if whip and whip != '-.--' else None
                        break
            # 팀 시즌 스탯
            home_batting = box['home']['teamStats']['batting']
            home_pitching = box['home']['teamStats']['pitching']
            away_batting = box['away']['teamStats']['batting']
            away_pitching = box['away']['teamStats']['pitching']
            home_ops = float(home_batting.get('ops')) if home_batting.get('ops') and home_batting.get('ops') != '-.--' else None
            home_era = float(home_pitching.get('era')) if home_pitching.get('era') and home_pitching.get('era') != '-.--' else None
            away_ops = float(away_batting.get('ops')) if away_batting.get('ops') and away_batting.get('ops') != '-.--' else None
            away_era = float(away_pitching.get('era')) if away_pitching.get('era') and away_pitching.get('era') != '-.--' else None
            historical_data.append({
                'date': game_date,
                'game_id': game_id,
                'home_team': game['home_name'],
                'away_team': game['away_name'],
                'home_score': game['home_score'],
                'away_score': game['away_score'],
                'home_win': 1 if game['home_score'] > game['away_score'] else 0,
                'total_runs': game['home_score'] + game['away_score'],
                'home_pitcher': home_pitcher_name,
                'home_pitcher_era': home_pitcher_era,
                'home_pitcher_whip': home_pitcher_whip,
                'home_ops': home_ops,
                'home_era': home_era,
                'away_pitcher': away_pitcher_name,
                'away_pitcher_era': away_pitcher_era,
                'away_pitcher_whip': away_pitcher_whip,
                'away_ops': away_ops,
                'away_era': away_era
            })
        except Exception:
            continue
    return pd.DataFrame(historical_data)

def get_today_boxscore_era_with_stats():
    """오늘 경기 데이터(MLB API) 수집 (pure)"""
    today = datetime.today().strftime('%Y-%m-%d')
    schedule = statsapi.schedule(sportId=1, start_date=today, end_date=today)
    game_data = []
    for game in schedule:
        game_id = game['game_id']
        home_id = game['home_id']
        away_id = game['away_id']
        game_time = game.get('game_datetime')
        game_time_kst = None
        if game_time:
            try:
                utc_time = datetime.fromisoformat(game_time.replace('Z', '+00:00'))
                kst = pytz.timezone('Asia/Seoul')
                game_time_kst = utc_time.astimezone(kst).strftime('%m/%d %H:%M')
            except Exception:
                game_time_kst = None
        try:
            time.sleep(0.1)
            box = statsapi.boxscore_data(game_id)
            home_pitcher_name = home_pitcher_era = None
            for player in box['home']['players'].values():
                if player['position']['abbreviation'] == 'P':
                    stats = player['seasonStats']['pitching']
                    era = stats.get('era')
                    if era and era != '-.--':
                        home_pitcher_name = player['person']['fullName']
                        home_pitcher_era = float(era)
                        break
            away_pitcher_name = away_pitcher_era = None
            for player in box['away']['players'].values():
                if player['position']['abbreviation'] == 'P':
                    stats = player['seasonStats']['pitching']
                    era = stats.get('era')
                    if era and era != '-.--':
                        away_pitcher_name = player['person']['fullName']
                        away_pitcher_era = float(era)
                        break
            home_batting = box['home']['teamStats']['batting']
            home_pitching = box['home']['teamStats']['pitching']
            away_batting = box['away']['teamStats']['batting']
            away_pitching = box['away']['teamStats']['pitching']
            home_ops = float(home_batting.get('ops')) if home_batting.get('ops') and home_batting.get('ops') != '-.--' else None
            home_era = float(home_pitching.get('era')) if home_pitching.get('era') and home_pitching.get('era') != '-.--' else None
            away_ops = float(away_batting.get('ops')) if away_batting.get('ops') and away_batting.get('ops') != '-.--' else None
            away_era = float(away_pitching.get('era')) if away_pitching.get('era') and away_pitching.get('era') != '-.--' else None
        except Exception:
            home_pitcher_name = away_pitcher_name = ''
            home_pitcher_era = away_pitcher_era = None
            home_ops = home_era = away_ops = away_era = None
        game_data.append({
            'game_id': game_id,
            'home_id': home_id,
            'away_id': away_id,
            'game_time_kst': game_time_kst,
            'home_team': game['home_name'],
            'home_pitcher': home_pitcher_name,
            'home_pitcher_era': home_pitcher_era,
            'home_ops': home_ops,
            'home_era': home_era,
            'away_team': game['away_name'],
            'away_pitcher': away_pitcher_name,
            'away_pitcher_era': away_pitcher_era,
            'away_ops': away_ops,
            'away_era': away_era
        })
    return pd.DataFrame(game_data)

def get_recent_data(days=30):
    """최근 N일간의 데이터를 수집 (pure)"""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    return get_historical_game_data(start_date, end_date)

# === CSV/파일 유틸 ===
def list_available_csv_files():
    """사용 가능한 CSV 파일 목록 반환 (list of dict)"""
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'mlb' in f.lower()]
    result = []
    for file in csv_files:
        file_size = os.path.getsize(file) / 1024  # KB
        mod_time = datetime.fromtimestamp(os.path.getmtime(file))
        result.append({
            'name': file,
            'size': f"{file_size:.1f}KB",
            'modified': mod_time.strftime('%Y-%m-%d %H:%M')
        })
    return result

def load_csv_data(filename=None):
    """CSV 파일에서 데이터 로드 (print/input 없이, 파일명 없으면 None)"""
    if filename is None:
        return None
    try:
        df = pd.read_csv(filename)
        return df
    except Exception:
        return None

def check_and_update_csv_data(filename, min_games=50, days_back=30, include_today=True):
    """CSV 파일 자동 업데이트 (print 없이, pure)"""
    try:
        df_existing = pd.read_csv(filename)
        if 'date' in df_existing.columns:
            latest_date = pd.to_datetime(df_existing['date'].max())
            days_since_latest = (datetime.today() - latest_date).days
        else:
            days_since_latest = days_back
        today = datetime.today()
        if len(df_existing) >= min_games and days_since_latest < 1:
            return df_existing
        # 최신 데이터 수집
        if days_since_latest >= 1:
            start_date = latest_date + timedelta(days=1) if 'date' in df_existing.columns else today - timedelta(days=days_back)
            end_date = today
            df_new = get_historical_game_data(start_date, end_date)
            if len(df_new) > 0:
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined = df_combined.drop_duplicates(subset=['game_id'], keep='first')
                df_combined = df_combined.sort_values('date', ascending=False)
                df_combined.to_csv(filename, index=False)
                return df_combined
            else:
                return df_existing
        elif len(df_existing) < min_games:
            end_date = today
            start_date = end_date - timedelta(days=days_back)
            df_additional = get_historical_game_data(start_date, end_date)
            if len(df_additional) > 0:
                df_combined = pd.concat([df_existing, df_additional], ignore_index=True)
                df_combined = df_combined.drop_duplicates(subset=['game_id'], keep='first')
                df_combined = df_combined.sort_values('date', ascending=False)
                df_combined.to_csv(filename, index=False)
                return df_combined
            else:
                return df_existing
        return df_existing
    except FileNotFoundError:
        return None
    except Exception:
        return None

# === 예측/성능 분석 유틸 ===
def compare_rf_xgb_decision_improved(df_historical, df_today, fast=False):
    """랜덤포레스트/XGBoost 예측 비교 (pure, 결과 리스트 반환)"""
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    # 특성 선택 (안정적인 특성만 사용)
    if fast:
        features = [
            'home_pitcher_era', 'home_ops', 'home_era',
            'away_pitcher_era', 'away_ops', 'away_era'
        ]
    else:
        features = [
            'home_pitcher_era', 'home_pitcher_whip', 'home_ops', 'home_avg', 'home_slg', 'home_era', 'home_whip',
            'away_pitcher_era', 'away_pitcher_whip', 'away_ops', 'away_avg', 'away_slg', 'away_era', 'away_whip'
        ]
    df_selected = df_historical[features + ['home_win', 'home_score', 'away_score', 'total_runs']]
    df_filled = df_selected.copy()
    df_filled[features] = df_filled[features].fillna(df_filled[features].mean())
    df_filled[features] = df_filled[features].replace([np.inf, -np.inf], np.nan)
    df_filled[features] = df_filled[features].fillna(df_filled[features].mean())
    df_filled[features] = df_filled[features].fillna(0)
    X = df_filled[features]
    y = df_filled['home_win']
    # 스케일링
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # 분류 모델
    rf_clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    xgb_clf = XGBClassifier(n_estimators=100, random_state=42, max_depth=6)
    rf_clf.fit(X_scaled, y)
    xgb_clf.fit(X_scaled, y)
    # 회귀 모델
    rf_reg_home = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    rf_reg_away = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    xgb_reg_home = XGBRegressor(n_estimators=100, random_state=42, max_depth=6)
    xgb_reg_away = XGBRegressor(n_estimators=100, random_state=42, max_depth=6)
    rf_reg_home.fit(X, df_filled['home_score'])
    rf_reg_away.fit(X, df_filled['away_score'])
    xgb_reg_home.fit(X_scaled, df_filled['home_score'])
    xgb_reg_away.fit(X_scaled, df_filled['away_score'])
    # 예측
    predictions = []
    for _, row in df_today.iterrows():
        missing_features = [f for f in features if pd.isna(row[f])]
        if missing_features:
            continue
        X_pred = row[features].values.reshape(1, -1)
        # DataFrame으로 변환하여 feature names 보장
        X_pred_df = pd.DataFrame(X_pred, columns=features)
        X_pred_scaled = scaler.transform(X_pred_df)
        rf_home_win_prob = rf_clf.predict_proba(X_pred_scaled)[0][1]
        xgb_home_win_prob = xgb_clf.predict_proba(X_pred_scaled)[0][1]
        rf_home_score = int(round(rf_reg_home.predict(X_pred_df)[0]))
        rf_away_score = int(round(rf_reg_away.predict(X_pred_df)[0]))
        xgb_home_score = int(round(xgb_reg_home.predict(X_pred_scaled)[0]))
        xgb_away_score = int(round(xgb_reg_away.predict(X_pred_scaled)[0]))
        pred = {
            'home_team': str(row['home_team']),
            'away_team': str(row['away_team']),
            'home_pitcher': str(row.get('home_pitcher', '미정')),
            'away_pitcher': str(row.get('away_pitcher', '미정')),
            'game_time_kst': row.get('game_time_kst', '시간 미정'),
            'rf_home_win_prob': float(max(0.05, min(0.95, rf_home_win_prob))),
            'rf_away_win_prob': float(max(0.05, min(0.95, 1 - rf_home_win_prob))),
            'rf_home_score': int(max(0, rf_home_score)),
            'rf_away_score': int(max(0, rf_away_score)),
            'xgb_home_win_prob': float(max(0.05, min(0.95, xgb_home_win_prob))),
            'xgb_away_win_prob': float(max(0.05, min(0.95, 1 - xgb_home_win_prob))),
            'xgb_home_score': int(max(0, xgb_home_score)),
            'xgb_away_score': int(max(0, xgb_away_score)),
            'mode': 'fast' if fast else 'full',
            'data_count': int(len(df_historical))
        }
        predictions.append(pred)
    return predictions

def analyze_and_report_performance(predictions, actual_results):
    """예측 성능 분석 및 보고서 생성 (pure, dict 반환)"""
    if not predictions or not actual_results:
        return None
    total_games = 0
    win_correct = 0
    total_home_error = 0
    total_away_error = 0
    total_error = 0
    for pred, actual in zip(predictions, actual_results):
        if pred['home_team'] == actual['home_team'] and pred['away_team'] == actual['away_team']:
            total_games += 1
            pred_winner = 'home' if pred['rf_home_win_prob'] > 0.5 else 'away'
            actual_winner = actual['winner']
            if pred_winner == actual_winner:
                win_correct += 1
            home_score_error = abs(pred['rf_home_score'] - actual['home_score'])
            away_score_error = abs(pred['rf_away_score'] - actual['away_score'])
            total_home_error += home_score_error
            total_away_error += away_score_error
            total_error += home_score_error + away_score_error
    if total_games == 0:
        return None
    return {
        'total_games': int(total_games),
        'win_accuracy': float(win_correct / total_games),
        'mean_home_error': float(total_home_error / total_games),
        'mean_away_error': float(total_away_error / total_games),
        'mean_total_error': float(total_error / total_games)
    }

def predict_score_with_margin(df_historical, df_today, fast_mode=False):
    """
    개선된 스코어 예측 함수 - 점수차와 승리 확률을 함께 예측
    """
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)

    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from xgboost import XGBRegressor
    import numpy as np

    # 특성 선택 (안정적인 특성만 사용)
    if fast_mode:
        features = [
            'home_pitcher_era', 'home_ops', 'home_era',
            'away_pitcher_era', 'away_ops', 'away_era'
        ]
    else:
        features = [
            'home_pitcher_era', 'home_pitcher_whip', 'home_ops', 'home_avg', 'home_slg', 'home_era', 'home_whip',
            'away_pitcher_era', 'away_pitcher_whip', 'away_ops', 'away_avg', 'away_slg', 'away_era', 'away_whip'
        ]

    # 데이터 검증
    if not validate_prediction_data(df_historical, df_today, features):
        return None, "데이터 검증 실패"

    # 데이터 전처리
    df_selected = df_historical[features + ['home_score', 'away_score', 'home_win']].copy()

    # NaN 값 처리
    df_selected[features] = df_selected[features].fillna(df_selected[features].mean())
    df_selected[features] = df_selected[features].replace([np.inf, -np.inf], np.nan)
    df_selected[features] = df_selected[features].fillna(df_selected[features].mean())
    df_selected[features] = df_selected[features].fillna(0)

    # 최종적으로 NaN이 있는 행 제거
    df_selected = df_selected.dropna()

    if len(df_selected) < 50:
        return None, "데이터가 부족합니다 (50개 미만)"

    # 점수차 계산
    df_selected['score_margin'] = df_selected['home_score'] - df_selected['away_score']

    # 특성 스케일링
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X = df_selected[features]
    X_scaled = scaler.fit_transform(X)

    # 모델 학습
    np.random.seed(42)

    # 1. 홈팀 점수 예측
    home_score_model = XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        subsample=0.8,
        colsample_bytree=0.8
    )
    home_score_model.fit(X_scaled, df_selected['home_score'])

    # 2. 원정팀 점수 예측
    away_score_model = XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        subsample=0.8,
        colsample_bytree=0.8
    )
    away_score_model.fit(X_scaled, df_selected['away_score'])

    # 3. 점수차 예측
    margin_model = XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        subsample=0.8,
        colsample_bytree=0.8
    )
    margin_model.fit(X_scaled, df_selected['score_margin'])

    # 4. 승리 확률 예측
    win_prob_model = XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        subsample=0.8,
        colsample_bytree=0.8
    )
    win_prob_model.fit(X_scaled, df_selected['home_win'])

    # 예측 실행
    predictions = []

    for _, row in df_today.iterrows():
        # 누락된 특성 처리
        missing_features = [f for f in features if pd.isna(row[f])]
        if missing_features:
            print(f"❌ 누락된 특성: {missing_features}")
            continue

        # 예측용 데이터 준비
        X_pred = row[features].values.reshape(1, -1)

        # NaN 값 처리
        X_pred = np.nan_to_num(X_pred, nan=0.0)

        # DataFrame으로 변환하여 feature names 보장
        X_pred_df = pd.DataFrame(X_pred, columns=features)
        X_pred_scaled = scaler.transform(X_pred_df)

        # 점수 예측
        try:
            home_score_raw = home_score_model.predict(X_pred_scaled)[0]
            away_score_raw = away_score_model.predict(X_pred_scaled)[0]
            margin_raw = margin_model.predict(X_pred_scaled)[0]
            win_prob_raw = win_prob_model.predict(X_pred_scaled)[0]

            # 예측값 검증
            if np.isnan(home_score_raw) or np.isnan(away_score_raw):
                print(f"❌ 예측값이 NaN입니다: home={home_score_raw}, away={away_score_raw}")
                continue

            # 점수 정수화 및 조정
            home_score = max(0, int(round(home_score_raw)))
            away_score = max(0, int(round(away_score_raw)))

            print(f"✅ 예측 완료: {row.get('away_team', 'N/A')} {away_score}-{home_score} {row.get('home_team', 'N/A')}")

        except Exception as e:
            print(f"❌ 예측 중 오류: {e}")
            continue

        # 점수차 계산
        score_margin = home_score - away_score

        # 야구 특성을 반영한 승리 확률 계산
        # 1. 기본 승리 확률 (모델 예측값)
        base_win_prob = win_prob_raw

        # 2. 야구 특성 반영: 무승부 방지 및 연장전 고려
        if abs(score_margin) == 0:
            # 점수가 같을 때는 연장전을 고려한 승리 확률 계산
            # 연장전에서는 홈팀이 약간 유리 (홈 어드밴티지)
            import random
            random.seed(42)  # 일관성 보장

            # 연장전 승리 확률 (홈팀 55%, 원정팀 45%)
            extra_inning_home_advantage = 0.55
            # 기본 확률과 연장전 확률을 가중 평균
            win_prob = (base_win_prob * 0.7) + (extra_inning_home_advantage * 0.3)
        else:
            # 점수차가 있을 때는 점수차에 따른 조정
            margin_factor = min(0.4, abs(score_margin) * 0.08)  # 최대 40% 조정
            if score_margin > 0:
                win_prob = min(0.95, base_win_prob + margin_factor)
            else:
                win_prob = max(0.05, base_win_prob - margin_factor)

        # 3. 팀 성능 차이 반영
        home_era = row.get('home_era', 4.0)
        away_era = row.get('away_era', 4.0)
        home_ops = row.get('home_ops', 0.7)
        away_ops = row.get('away_ops', 0.7)

        # ERA와 OPS 차이에 따른 미세 조정
        era_diff = away_era - home_era  # 홈팀 ERA가 낮을수록 유리
        ops_diff = home_ops - away_ops  # 홈팀 OPS가 높을수록 유리

        performance_factor = (era_diff * 0.02) + (ops_diff * 0.1)  # 성능 차이 반영
        win_prob = max(0.05, min(0.95, win_prob + performance_factor))

        # 4. 야구 특성 추가 고려사항
        # - 홈 어드밴티지 (약간의 추가 확률)
        home_advantage = 0.02
        win_prob = min(0.95, win_prob + home_advantage)

        # 5. 경기 상황별 예측
        game_situation = "연장전 가능성" if abs(score_margin) <= 1 else "일반 경기"

        # 베팅 관련 정보
        margin_category = "대승" if abs(score_margin) >= 5 else "소승" if abs(score_margin) >= 2 else "접전"

        # 신뢰도 계산 개선
        confidence = abs(win_prob - 0.5) * 2  # 0~1 사이의 신뢰도

        # 점수 기반 승리 예측 (점수와 일치하도록)
        if home_score > away_score:
            predicted_winner = 'home'
            # 점수차가 클수록 확률 차이도 커짐
            win_prob = min(0.95, 0.5 + (abs(score_margin) * 0.1))
        elif away_score > home_score:
            predicted_winner = 'away'
            # 점수차가 클수록 확률 차이도 커짐
            win_prob = max(0.05, 0.5 - (abs(score_margin) * 0.1))
        else:
            # 동점일 때는 확률 기반으로 결정하되, 점수와 일치하도록 조정
            predicted_winner = 'home' if win_prob > 0.5 else 'away'
            # 동점일 때는 확률 차이를 줄임
            win_prob = max(0.45, min(0.55, win_prob))

        prediction = {
            'home_score': int(home_score),
            'away_score': int(away_score),
            'score_margin': int(score_margin),
            'margin_category': str(margin_category),
            'home_win_prob': float(win_prob),
            'away_win_prob': float(1 - win_prob),
            'predicted_winner': str(predicted_winner),
            'confidence': float(confidence),
            'game_situation': str(game_situation)
        }

        predictions.append(prediction)

    return predictions, None

def analyze_betting_opportunities(predictions):
    """
    베팅 기회 분석 함수
    """
    betting_opportunities = []

    for pred in predictions:
        confidence = float(pred.get('confidence', 0))
        margin_category = str(pred.get('margin_category', '접전'))
        home_win_prob = float(pred.get('home_win_prob', 0.5))

        # 베팅 기회 판단 기준
        betting_score = 0
        betting_reason = []

        # 1. 높은 신뢰도 (70% 이상)
        if confidence >= 0.7:
            betting_score += 30
            betting_reason.append(f"높은 신뢰도 ({confidence:.1%})")

        # 2. 명확한 승리 예측 (60% 이상)
        if home_win_prob >= 0.6 or home_win_prob <= 0.4:
            betting_score += 25
            betting_reason.append(f"명확한 승리 예측 ({home_win_prob:.1%})")

        # 3. 점수차 분석
        if margin_category == "대승":
            betting_score += 20
            betting_reason.append("대승 예측")
        elif margin_category == "소승":
            betting_score += 15
            betting_reason.append("소승 예측")

        # 4. 야구 특성 분석
        game_situation = str(pred.get('game_situation', '일반 경기'))
        if game_situation == "연장전 가능성":
            betting_score += 10
            betting_reason.append("연장전 가능성")

        # 5. 홈 어드밴티지 고려
        if pred.get('predicted_winner') == 'home' and home_win_prob > 0.55:
            betting_score += 5
            betting_reason.append("홈 어드밴티지")

        # 6. 베팅 추천 등급
        if betting_score >= 60:
            recommendation = "강력 추천"
        elif betting_score >= 40:
            recommendation = "추천"
        elif betting_score >= 20:
            recommendation = "관심"
        else:
            recommendation = "관망"

        betting_opportunities.append({
            'game': f"{pred['away_team']} @ {pred['home_team']}",
            'predicted_winner': str(pred.get('predicted_winner', 'unknown')),
            'home_win_prob': home_win_prob,
            'confidence': confidence,
            'margin_category': margin_category,
            'betting_score': betting_score,
            'betting_reason': [str(r) for r in betting_reason],
            'recommendation': str(recommendation)
        })

    return betting_opportunities

def validate_prediction_data(df_historical, df_today, features):
    """
    예측 데이터 검증 함수
    """
    print("=== 데이터 검증 시작 ===")

    # 1. 과거 데이터 검증
    print(f"과거 데이터 크기: {len(df_historical)}")
    print(f"필요한 특성: {features}")

    # 누락된 특성 확인
    missing_features = [f for f in features if f not in df_historical.columns]
    if missing_features:
        print(f"❌ 누락된 특성: {missing_features}")
        return False

    # NaN 값 확인
    nan_counts = df_historical[features].isna().sum()
    print(f"NaN 값 개수:\n{nan_counts}")

    # 2. 오늘 데이터 검증
    print(f"\n오늘 데이터 크기: {len(df_today)}")

    for idx, row in df_today.iterrows():
        print(f"\n경기 {idx+1}: {row.get('away_team', 'N/A')} @ {row.get('home_team', 'N/A')}")
        for feature in features:
            value = row.get(feature)
            if pd.isna(value):
                print(f"  ❌ {feature}: NaN")
            else:
                print(f"  ✅ {feature}: {value}")

    # 3. 데이터 품질 확인
    df_clean = df_historical[features + ['home_score', 'away_score', 'home_win']].dropna()
    print(f"\n클린 데이터 크기: {len(df_clean)}")

    if len(df_clean) < 50:
        print("❌ 클린 데이터가 부족합니다 (50개 미만)")
        return False

    print("✅ 데이터 검증 완료")
    return True 