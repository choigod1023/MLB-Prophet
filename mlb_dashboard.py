from flask import Flask, render_template, jsonify, request, send_file
import os
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
import numpy as np
from datetime import datetime, timedelta
import json
import pytz
import flask

app = Flask(__name__)

# === numpy 타입 자동 변환을 위한 Flask 커스텀 인코더/Provider 버전별 적용 ===
flask_version = tuple(map(int, flask.__version__.split(".")[:2]))
if flask_version >= (2, 3):
    from flask.json.provider import DefaultJSONProvider
    class NumpyJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            elif isinstance(obj, (np.floating,)):
                return float(obj)
            elif isinstance(obj, (np.ndarray,)):
                return obj.tolist()
            elif hasattr(obj, 'item'):
                return obj.item()
            return super().default(obj)
    app.json = NumpyJSONProvider(app)
else:
    from flask.json import JSONEncoder
    class NumpyEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            elif isinstance(obj, (np.floating,)):
                return float(obj)
            elif isinstance(obj, (np.ndarray,)):
                return obj.tolist()
            elif hasattr(obj, 'item'):
                return obj.item()
            return super().default(obj)
    app.json_encoder = NumpyEncoder
# === 커스텀 인코더/Provider 끝 ===

# 디버그 모드 활성화
app.debug = True

# 전역 변수로 예측 결과 저장
current_predictions = []
performance_data = None

# 로깅 설정
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 예측 결과 저장 파일
PREDICTIONS_FILE = 'predictions_history.json'

def load_predictions_history():
    if os.path.exists(PREDICTIONS_FILE):
        try:
            with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"예측 기록 로드 오류: {e}")
    return []

def save_predictions_history(predictions_data):
    try:
        with open(PREDICTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(convert_np(predictions_data), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"예측 기록 저장 오류: {e}")

def save_predictions_to_csv(predictions, filename=None):
    """예측 결과를 CSV 파일로 저장"""
    try:
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'mlb_predictions_{timestamp}.csv'
        
        # 예측 결과를 DataFrame으로 변환
        df_predictions = []
        for pred in predictions:
            row = {
                '예측날짜': pred.get('prediction_date', ''),
                '예측시간': pred.get('prediction_time', ''),
                '경기시간': pred.get('game_time_kst', ''),
                '원정팀': pred.get('away_team', ''),
                '홈팀': pred.get('home_team', ''),
                '원정선발': pred.get('away_pitcher', ''),
                '홈선발': pred.get('home_pitcher', ''),
                'RF_홈승률': f"{float(pred.get('rf_home_win_prob', 0))*100:.1f}%",
                'RF_원정승률': f"{float(pred.get('rf_away_win_prob', 0))*100:.1f}%",
                'RF_홈점수': int(pred.get('rf_home_score', 0)),
                'RF_원정점수': int(pred.get('rf_away_score', 0)),
                'XGB_홈승률': f"{float(pred.get('xgb_home_win_prob', 0))*100:.1f}%",
                'XGB_원정승률': f"{float(pred.get('xgb_away_win_prob', 0))*100:.1f}%",
                'XGB_홈점수': int(pred.get('xgb_home_score', 0)),
                'XGB_원정점수': int(pred.get('xgb_away_score', 0)),
                '예측모드': pred.get('mode', ''),
                '데이터수': int(pred.get('data_count', 0))
            }
            
            # 실제 결과가 있으면 추가
            if pred.get('actual_result'):
                actual = pred['actual_result']
                row.update({
                    '실제_홈점수': int(actual.get('home_score', 0)),
                    '실제_원정점수': int(actual.get('away_score', 0)),
                    '실제_승자': actual.get('winner', ''),
                    '승패예측정확도': '적중' if pred.get('accuracy', {}).get('win_correct') else '실패'
                })
            
            df_predictions.append(row)
        
        df = pd.DataFrame(df_predictions)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
    except Exception as e:
        print(f"CSV 저장 오류: {e}")
        return None

def save_predictions_to_excel(predictions, filename=None):
    """예측 결과를 Excel 파일로 저장"""
    try:
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'mlb_predictions_{timestamp}.xlsx'
        
        # 예측 결과를 DataFrame으로 변환
        df_predictions = []
        for pred in predictions:
            row = {
                '예측날짜': pred.get('prediction_date', ''),
                '예측시간': pred.get('prediction_time', ''),
                '경기시간': pred.get('game_time_kst', ''),
                '원정팀': pred.get('away_team', ''),
                '홈팀': pred.get('home_team', ''),
                '원정선발': pred.get('away_pitcher', ''),
                '홈선발': pred.get('home_pitcher', ''),
                'RF_홈승률': f"{float(pred.get('rf_home_win_prob', 0))*100:.1f}%",
                'RF_원정승률': f"{float(pred.get('rf_away_win_prob', 0))*100:.1f}%",
                'RF_홈점수': int(pred.get('rf_home_score', 0)),
                'RF_원정점수': int(pred.get('rf_away_score', 0)),
                'XGB_홈승률': f"{float(pred.get('xgb_home_win_prob', 0))*100:.1f}%",
                'XGB_원정승률': f"{float(pred.get('xgb_away_win_prob', 0))*100:.1f}%",
                'XGB_홈점수': int(pred.get('xgb_home_score', 0)),
                'XGB_원정점수': int(pred.get('xgb_away_score', 0)),
                '예측모드': pred.get('mode', ''),
                '데이터수': int(pred.get('data_count', 0))
            }
            
            # 실제 결과가 있으면 추가
            if pred.get('actual_result'):
                actual = pred['actual_result']
                row.update({
                    '실제_홈점수': int(actual.get('home_score', 0)),
                    '실제_원정점수': int(actual.get('away_score', 0)),
                    '실제_승자': actual.get('winner', ''),
                    '승패예측정확도': '적중' if pred.get('accuracy', {}).get('win_correct') else '실패'
                })
            
            df_predictions.append(row)
        
        df = pd.DataFrame(df_predictions)
        
        # Excel 파일로 저장
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='예측결과', index=False)
            
            # 요약 시트 추가
            summary_data = {
                '항목': ['총 예측 경기', '예측 모드', '데이터 수집 기간', '생성 시간'],
                '값': [
                    len(predictions),
                    predictions[0].get('mode', '') if predictions else '',
                    f"{predictions[0].get('data_count', 0)}개 경기" if predictions else '',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='요약', index=False)
        
        return filename
    except Exception as e:
        print(f"Excel 저장 오류: {e}")
        return None

def create_prediction_report(predictions, filename=None):
    """예측 결과 요약 리포트 생성"""
    try:
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'mlb_prediction_report_{timestamp}.txt'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("MLB 예측 결과 리포트\n")
            f.write("=" * 60 + "\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"총 예측 경기: {len(predictions)}개\n")
            f.write(f"예측 모드: {predictions[0].get('mode', '') if predictions else ''}\n")
            f.write(f"데이터 수: {predictions[0].get('data_count', 0)}개 경기\n\n")
            
            f.write("경기별 예측 결과:\n")
            f.write("-" * 60 + "\n")
            
            for i, pred in enumerate(predictions, 1):
                f.write(f"\n{i}. {pred['away_team']} @ {pred['home_team']}\n")
                f.write(f"   경기시간: {pred.get('game_time_kst', '시간 미정')}\n")
                f.write(f"   선발투수: {pred.get('away_pitcher', '미정')} vs {pred.get('home_pitcher', '미정')}\n")
                f.write(f"   RF 예측: {pred['rf_away_score']}-{pred['rf_home_score']} (홈승률: {float(pred['rf_home_win_prob'])*100:.1f}%)\n")
                f.write(f"   XGB 예측: {pred['xgb_away_score']}-{pred['xgb_home_score']} (홈승률: {float(pred['xgb_home_win_prob'])*100:.1f}%)\n")
                
                if pred.get('actual_result'):
                    actual = pred['actual_result']
                    f.write(f"   실제 결과: {actual['away_score']}-{actual['home_score']}\n")
                    f.write(f"   예측 정확도: {'적중' if pred.get('accuracy', {}).get('win_correct') else '실패'}\n")
                else:
                    f.write(f"   실제 결과: 대기중\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("리포트 끝\n")
        
        return filename
    except Exception as e:
        print(f"리포트 생성 오류: {e}")
        return None

def calculate_prediction_accuracy(prediction, actual_result):
    """예측 정확도 계산"""
    if not actual_result:
        return None
    
    # 승패 예측 정확도
    pred_winner = 'home' if prediction['rf_home_win_prob'] > 0.5 else 'away'
    actual_winner = actual_result['winner']
    win_correct = pred_winner == actual_winner
    
    # 스코어 예측 오차
    home_score_error = abs(prediction['rf_home_score'] - actual_result['home_score'])
    away_score_error = abs(prediction['rf_away_score'] - actual_result['away_score'])
    total_score_error = home_score_error + away_score_error
    
    return {
        'win_correct': win_correct,
        'home_score_error': home_score_error,
        'away_score_error': away_score_error,
        'total_score_error': total_score_error,
        'predicted_winner': pred_winner,
        'actual_winner': actual_winner
    }

def convert_np(obj):
    import numpy as np
    if isinstance(obj, dict):
        return {k: convert_np(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return [convert_np(x) for x in obj.tolist()]
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif hasattr(obj, 'item'):
        return obj.item()
    else:
        return obj


@app.route('/')
def dashboard():
    """메인 대시보드"""
    # 서버 시작 시에는 빈 예측 리스트로 시작
    # 사용자가 웹에서 "예측 실행" 버튼을 클릭할 때만 데이터 수집 및 예측 수행
    return render_template('dashboard.html', predictions=[])

@app.route('/api/today-games')
def get_today_games():
    """
    오늘 경기 데이터 API
    ---
    responses:
      200:
        description: 오늘 경기 데이터 반환
    """
    try:
        df_today = get_today_boxscore_era_with_stats()
        if len(df_today) == 0:
            return jsonify({'success': False, 'error': '오늘 경기가 없습니다.'})
        
        games_data = []
        for _, row in df_today.iterrows():
            game_info = {
                'home_team': str(row['home_team']),
                'away_team': str(row['away_team']),
                'home_pitcher': str(row.get('home_pitcher', '미정')),
                'away_pitcher': str(row.get('away_pitcher', '미정')),
                'home_pitcher_era': float(row.get('home_pitcher_era')) if pd.notna(row.get('home_pitcher_era')) else None,
                'away_pitcher_era': float(row.get('away_pitcher_era')) if pd.notna(row.get('away_pitcher_era')) else None,
                'home_ops': float(row.get('home_ops')) if pd.notna(row.get('home_ops')) else None,
                'away_ops': float(row.get('away_ops')) if pd.notna(row.get('away_ops')) else None,
                'home_era': float(row.get('home_era')) if pd.notna(row.get('home_era')) else None,
                'away_era': float(row.get('away_era')) if pd.notna(row.get('away_era')) else None
            }
            games_data.append(game_info)
        
        return jsonify({
            'success': True,
            'games': games_data,
            'total_games': len(games_data)
        })
    except Exception as e:
        print(f"오늘 경기 API 오류: {e}")
        return jsonify({'success': False, 'error': f'데이터 수집 오류: {str(e)}'})

@app.route('/api/yesterday-results')
def get_yesterday_results():
    """어제 경기 결과 API"""
    try:
        # 어제 날짜 계산 (KST 기준)
        kst = pytz.timezone('Asia/Seoul')
        yesterday = datetime.now(kst) - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        # 어제 경기 결과 가져오기
        actual_results = get_actual_results_for_date(yesterday_str)
        
        if not actual_results:
            return jsonify({
                'success': False, 
                'error': f'{yesterday_str}의 경기 결과가 아직 없습니다.'
            })
        
        # 예측 기록에서 어제 예측 결과 가져오기
        predictions_history = load_predictions_history()
        yesterday_predictions = [p for p in predictions_history if p.get('prediction_date') == yesterday_str]
        
        # 예측 결과와 실제 결과 매칭
        matched_results = []
        for actual in actual_results:
            prediction = None
            for pred in yesterday_predictions:
                # 1. team_id 매칭
                if (
                    'home_id' in pred and 'away_id' in pred and 'home_id' in actual and 'away_id' in actual
                    and pred['home_id'] is not None and pred['away_id'] is not None
                    and actual['home_id'] is not None and actual['away_id'] is not None
                ):
                    try:
                        if int(pred['home_id']) == int(actual['home_id']) and int(pred['away_id']) == int(actual['away_id']):
                            prediction = pred
                            break
                    except Exception as e:
                        print(f"[team_id 매칭 오류] {e}")
                else:
                    def norm(x):
                        return str(x).lower().replace(' ', '').replace('.', '').replace('-', '')
                    # 2. 이름 완전 일치
                    if norm(pred['home_team']) == norm(actual['home_team']) and norm(pred['away_team']) == norm(actual['away_team']):
                        prediction = pred
                        break
                    # 3. in 매칭 (부분 문자열 포함)
                    if (
                        norm(pred['home_team']) in norm(actual['home_team']) or norm(actual['home_team']) in norm(pred['home_team'])
                    ) and (
                        norm(pred['away_team']) in norm(actual['away_team']) or norm(actual['away_team']) in norm(pred['away_team'])
                    ):
                        prediction = pred
                        break
            # 디버깅 로그
            if not prediction:
                print(f"[매칭실패] 예측: {[(p['home_team'], p.get('home_id'), p['away_team'], p.get('away_id')) for p in yesterday_predictions]}")
                print(f"[매칭실패] 실제: {actual['home_team']}({actual.get('home_id')}) vs {actual['away_team']}({actual.get('away_id')})")

            # 정확도 계산
            accuracy = None
            if prediction:
                accuracy = calculate_prediction_accuracy(prediction, actual)
            
            result_info = {
                'home_team': actual['home_team'],
                'away_team': actual['away_team'],
                'home_id': actual.get('home_id'),
                'away_id': actual.get('away_id'),
                'home_score': actual['home_score'],
                'away_score': actual['away_score'],
                'winner': actual['winner'],
                'game_date': actual['game_date'],
                'prediction': prediction,
                'accuracy': accuracy
            }
            matched_results.append(result_info)
        
        return jsonify({
            'success': True,
            'date': yesterday_str,
            'results': matched_results,
            'total_games': len(matched_results)
        })
        
    except Exception as e:
        print(f"어제 경기 결과 API 오류: {e}")
        return jsonify({'success': False, 'error': f'결과 조회 오류: {str(e)}'})

@app.route('/api/predict', methods=['POST'])
def make_prediction():
    """
    예측 실행 API
    ---
    parameters:
      - name: mode
        in: body
        type: string
        required: false
        description: '예측 모드 (fast/full)'
      - name: data_source
        in: body
        type: string
        required: false
        description: '데이터 소스 (recent/csv)'
      - name: csv_file
        in: body
        type: string
        required: false
        description: 'CSV 파일명 (data_source가 csv일 때)'
    responses:
      200:
        description: 예측 결과 반환
    """
    global current_predictions
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'})
        
        mode = data.get('mode', 'fast')  # fast 또는 full
        data_source = data.get('data_source', 'recent')  # recent 또는 csv
        
        logger.info(f"예측 요청 시작: mode={mode}, data_source={data_source}")
        print(f"예측 요청: mode={mode}, data_source={data_source}")
        
        # 기존 모드들 (fast, full)
        if data_source == 'recent':
            logger.info("최근 200경기 데이터 수집 시작...")
            print("최근 200경기 데이터 수집 중...")
            try:
                df_historical = get_recent_data(n_games=200)
                logger.info(f"데이터 수집 완료: {len(df_historical) if df_historical is not None else 0}개 경기")
            except Exception as e:
                logger.error(f"데이터 수집 실패: {e}")
                return jsonify({'success': False, 'error': f'데이터 수집 실패: {str(e)}'})
        else:
            csv_file = data.get('csv_file')
            # 항상 자동 업데이트 시도
            if not csv_file:
                # 기본 CSV 파일 자동 선택 (가장 최근 수정된 mlb*.csv)
                import glob
                csv_candidates = glob.glob('mlb*.csv')
                if csv_candidates:
                    csv_file = max(csv_candidates, key=os.path.getmtime)
                else:
                    logger.error("CSV 파일이 없습니다.")
                    print("CSV 파일이 없습니다.")
                    return jsonify({'success': False, 'error': 'CSV 파일이 없습니다.'})
            logger.info(f"CSV 파일 자동 업데이트 시작: {csv_file}")
            print(f"CSV 파일 자동 업데이트 중: {csv_file}")
            try:
                df_historical = check_and_update_csv_data(csv_file, min_games=50, days_back=30, include_today=True)
                logger.info(f"CSV 업데이트 완료: {len(df_historical) if df_historical is not None else 0}개 경기")
            except Exception as e:
                logger.error(f"CSV 업데이트 실패: {e}")
                return jsonify({'success': False, 'error': f'CSV 업데이트 실패: {str(e)}'})
        
        if df_historical is None or len(df_historical) == 0:
            return jsonify({'success': False, 'error': '과거 데이터를 수집할 수 없습니다.'})
        
        print(f"과거 데이터 수집 완료: {len(df_historical)}개 경기")
        
        # 오늘 경기 데이터
        print("오늘 경기 데이터 수집 중...")
        df_today = get_today_boxscore_era_with_stats()
        if len(df_today) == 0:
            return jsonify({'success': False, 'error': '오늘 경기가 없습니다.'})
        
        print(f"오늘 경기 데이터 수집 완료: {len(df_today)}개 경기")
        
        # 실제 예측 실행
        fast_mode = (mode == 'fast')
        
        # 개선된 예측 함수 사용
        from mlb_utils import predict_score_with_margin
        
        # 예측 결과를 캡처하기 위한 임시 함수
        def capture_prediction_results(df_hist, df_today, fast_mode):
            """예측 결과를 캡처하여 반환하는 함수"""
            predictions = []
            prediction_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            prediction_date = datetime.now().strftime('%Y-%m-%d')
            
            try:
                # 필요한 라이브러리 import
                import numpy as np
                from sklearn.model_selection import train_test_split
                from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
                from xgboost import XGBClassifier, XGBRegressor
                from sklearn.preprocessing import StandardScaler
                
                # 빠른모드 특성
                if fast_mode:
                    features = [
                        'home_pitcher_era', 'home_ops', 'home_era',
                        'away_pitcher_era', 'away_ops', 'away_era'
                    ]
                else:
                    features = [
                        'home_pitcher_era', 'home_pitcher_whip', 'home_bullpen_era',
                        'home_ops', 'home_avg', 'home_slg', 'home_era', 'home_whip',
                        'away_pitcher_era', 'away_pitcher_whip', 'away_bullpen_era',
                        'away_ops', 'away_avg', 'away_slg', 'away_era', 'away_whip'
                    ]
                
                # 데이터 전처리
                df_selected = df_hist[features + ['home_win', 'home_score', 'away_score', 'total_runs']]
                df_filled = df_selected.copy()
                df_filled[features] = df_filled[features].fillna(df_filled[features].mean())
                df_filled[features] = df_filled[features].replace([np.inf, -np.inf], np.nan)
                df_filled[features] = df_filled[features].fillna(df_filled[features].mean())
                df_filled[features] = df_filled[features].fillna(0)
                
                X = df_filled[features]
                y = df_filled['home_win']
                
                if len(X) < 20:
                    print("데이터가 부족합니다 (20개 미만)")
                    return predictions  # 데이터 부족
                
                # 모델 학습 (결정론적 결과를 위한 고정 시드)
                # 전역 시드 설정으로 완전한 재현성 보장
                np.random.seed(42)
                
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
                for _, row in df_today.iterrows():
                    missing_features = [f for f in features if pd.isna(row[f])]
                    if missing_features:
                        print(f"누락된 특성: {missing_features}")
                        continue
                    
                    X_pred = row[features].values.reshape(1, -1)
                    X_pred_scaled = scaler.transform(X_pred)
                    
                    # 분류 예측
                    rf_home_win_prob = rf_clf.predict_proba(X_pred_scaled)[0][1]
                    xgb_home_win_prob = xgb_clf.predict_proba(X_pred_scaled)[0][1]
                    
                    # 회귀 예측
                    rf_home_score = int(round(rf_reg_home.predict(X_pred)[0]))
                    rf_away_score = int(round(rf_reg_away.predict(X_pred)[0]))
                    xgb_home_score = int(round(xgb_reg_home.predict(X_pred_scaled)[0]))
                    xgb_away_score = int(round(xgb_reg_away.predict(X_pred_scaled)[0]))
                    
                    # 선발 투수 정보
                    home_pitcher = str(row.get('home_pitcher', '미정'))
                    away_pitcher = str(row.get('away_pitcher', '미정'))
                    
                    # 경기 시간 정보 (KST)
                    game_time_kst = row.get('game_time_kst', '시간 미정')

                    # --- home_id/away_id 보장 로직 추가 ---
                    home_id = int(row['home_id']) if 'home_id' in row and pd.notna(row['home_id']) else None
                    away_id = int(row['away_id']) if 'away_id' in row and pd.notna(row['away_id']) else None
                    if home_id is None or away_id is None:
                        # MLB API에서 오늘 경기 스케줄로 id 매핑
                        try:
                            from mlb import statsapi
                            today = datetime.now().strftime('%Y-%m-%d')
                            schedule = statsapi.schedule(sportId=1, start_date=today, end_date=today)
                            name_to_id = {}
                            for g in schedule:
                                name_to_id[g['home_name']] = g['home_id']
                                name_to_id[g['away_name']] = g['away_id']
                            if home_id is None:
                                home_id = name_to_id.get(str(row['home_team']))
                            if away_id is None:
                                away_id = name_to_id.get(str(row['away_team']))
                        except Exception as e:
                            print(f"[home_id/away_id 매핑 오류] {e}")
                    # --- home_id/away_id 보장 끝 ---

                                                # 개선된 예측 결과 사용
                    try:
                        print(f"🔍 예측 시작: {row.get('away_team', 'N/A')} @ {row.get('home_team', 'N/A')}")
                        score_prediction = predict_score_with_margin(df_hist, pd.DataFrame([row]), fast_mode)
                        
                        if score_prediction and len(score_prediction[0]) > 0:
                            pred_result = score_prediction[0][0]
                            print(f"✅ 예측 성공: {pred_result}")
                            
                            pred = {
                                'prediction_date': prediction_date,
                                'prediction_time': prediction_time,
                                'home_team': str(row['home_team']),
                                'away_team': str(row['away_team']),
                                'home_id': home_id,
                                'away_id': away_id,
                                'home_pitcher': home_pitcher,
                                'away_pitcher': away_pitcher,
                                'game_time_kst': game_time_kst,
                                # 새로운 예측 결과를 기존 구조로 매핑
                                'rf_home_win_prob': pred_result['home_win_prob'],
                                'rf_away_win_prob': pred_result['away_win_prob'],
                                'rf_home_score': pred_result['home_score'],
                                'rf_away_score': pred_result['away_score'],
                                'xgb_home_win_prob': pred_result['home_win_prob'],
                                'xgb_away_win_prob': pred_result['away_win_prob'],
                                'xgb_home_score': pred_result['home_score'],
                                'xgb_away_score': pred_result['away_score'],
                                # 추가 정보
                                'score_margin': pred_result['score_margin'],
                                'margin_category': pred_result['margin_category'],
                                'predicted_winner': pred_result['predicted_winner'],
                                'confidence': pred_result['confidence'],
                                'game_situation': pred_result.get('game_situation', '일반 경기'),
                                'mode': str(mode),
                                'data_count': len(df_hist),
                                'actual_result': None,  # 나중에 업데이트
                                'accuracy': None  # 나중에 업데이트
                            }
                        else:
                            print(f"❌ 예측 실패: {score_prediction}")
                            # 기존 방식으로 폴백
                            pred = {
                                'prediction_date': prediction_date,
                                'prediction_time': prediction_time,
                                'home_team': str(row['home_team']),
                                'away_team': str(row['away_team']),
                                'home_id': home_id,
                                'away_id': away_id,
                                'home_pitcher': home_pitcher,
                                'away_pitcher': away_pitcher,
                                'game_time_kst': game_time_kst,
                                'rf_home_win_prob': float(max(0.05, min(0.95, rf_home_win_prob))),
                                'rf_away_win_prob': float(max(0.05, min(0.95, 1 - rf_home_win_prob))),
                                'rf_home_score': int(max(0, rf_home_score)),
                                'rf_away_score': int(max(0, rf_away_score)),
                                'xgb_home_win_prob': float(max(0.05, min(0.95, xgb_home_win_prob))),
                                'xgb_away_win_prob': float(max(0.05, min(0.95, 1 - xgb_home_win_prob))),
                                'xgb_home_score': int(max(0, xgb_home_score)),
                                'xgb_away_score': int(max(0, xgb_away_score)),
                                'mode': str(mode),
                                'data_count': len(df_hist),
                                'actual_result': None,  # 나중에 업데이트
                                'accuracy': None  # 나중에 업데이트
                            }
                    except Exception as e:
                        print(f"개선된 예측 실패, 기존 방식 사용: {e}")
                        # 기존 방식으로 폴백
                        pred = {
                            'prediction_date': prediction_date,
                            'prediction_time': prediction_time,
                            'home_team': str(row['home_team']),
                            'away_team': str(row['away_team']),
                            'home_id': home_id,
                            'away_id': away_id,
                            'home_pitcher': home_pitcher,
                            'away_pitcher': away_pitcher,
                            'game_time_kst': game_time_kst,
                            'rf_home_win_prob': float(max(0.05, min(0.95, rf_home_win_prob))),
                            'rf_away_win_prob': float(max(0.05, min(0.95, 1 - rf_home_win_prob))),
                            'rf_home_score': int(max(0, rf_home_score)),
                            'rf_away_score': int(max(0, rf_away_score)),
                            'xgb_home_win_prob': float(max(0.05, min(0.95, xgb_home_win_prob))),
                            'xgb_away_win_prob': float(max(0.05, min(0.95, 1 - xgb_home_win_prob))),
                            'xgb_home_score': int(max(0, xgb_home_score)),
                            'xgb_away_score': int(max(0, xgb_away_score)),
                            'mode': str(mode),
                            'data_count': len(df_hist),
                            'actual_result': None,  # 나중에 업데이트
                            'accuracy': None  # 나중에 업데이트
                        }
                    predictions.append(pred)
                
                print(f"예측 완료: {len(predictions)}개 경기 (시간: {prediction_time})")
                
            except Exception as e:
                print(f"예측 중 오류: {e}")
                import traceback
                traceback.print_exc()
            
            return predictions
        
        # 실제 예측 실행
        predictions = capture_prediction_results(df_historical, df_today, fast_mode)
        print('DEBUG: predictions 구조:', predictions)
        for i, pred in enumerate(predictions):
            print(f"DEBUG: predictions[{i}] 타입:", {k: type(v) for k, v in pred.items()})
        predictions = convert_np(predictions)
        print('DEBUG: predictions(converted) 구조:', predictions)
        for i, pred in enumerate(predictions):
            print(f"DEBUG: predictions(converted)[{i}] 타입:", {k: type(v) for k, v in pred.items()})
        # 예측 결과를 파일에 저장
        predictions_history = load_predictions_history()
        predictions_history.extend(predictions)
        print('DEBUG: predictions_history 구조:', predictions_history)
        for i, pred in enumerate(predictions_history):
            print(f"DEBUG: predictions_history[{i}] 타입:", {k: type(v) for k, v in pred.items()})
        save_predictions_history(predictions_history)
        
        current_predictions = predictions
        
        # 베팅 기회 분석
        from mlb_utils import analyze_betting_opportunities
        betting_analysis = analyze_betting_opportunities(predictions)
        betting_analysis = convert_np(betting_analysis)
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'betting_analysis': betting_analysis,
            'data_count': len(df_historical),
            'mode': mode
        })
        
    except Exception as e:
        print(f"API 예측 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'예측 오류: {str(e)}'})

@app.route('/api/check-results', methods=['POST'])
def check_actual_results():
    """
    실제 결과 확인 및 정확도 계산 API
    ---
    parameters:
      - name: date
        in: body
        type: string
        required: false
        description: '조회할 날짜 (YYYY-MM-DD)'
    responses:
      200:
        description: 결과 반환
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'})
        
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 해당 날짜의 실제 결과 가져오기
        actual_results = get_actual_results_for_date(date_str)
        
        if not actual_results:
            return jsonify({
                'success': False, 
                'error': f'{date_str}의 경기 결과가 아직 없습니다.'
            })
        
        # 해당 날짜의 예측 결과 가져오기
        predictions_history = load_predictions_history()
        date_predictions = [p for p in predictions_history if p.get('prediction_date') == date_str]
        
        # 예측 결과와 실제 결과 매칭 (실제 경기 기준으로)
        matched_results = []
        for actual in actual_results:
            prediction = None
            accuracy = None
            for pred in date_predictions:
                if (actual['home_team'] == pred['home_team'] and actual['away_team'] == pred['away_team']):
                    prediction = pred
                    accuracy = calculate_prediction_accuracy(pred, actual)
                    break
            matched_results.append({
                'actual': actual,
                'prediction': prediction,
                'accuracy': accuracy
            })
        
        return jsonify({
            'success': True,
            'date': date_str,
            'matched_results': matched_results,
            'total_predictions': len(date_predictions),
            'total_actual': len(actual_results),
            'matched_count': len([r for r in matched_results if r['prediction']])
        })
        
    except Exception as e:
        print(f"실제 결과 확인 오류: {e}")
        return jsonify({'success': False, 'error': f'결과 확인 오류: {str(e)}'})

@app.route('/api/prediction-history')
def get_prediction_history():
    """
    예측 기록 조회 API
    ---
    responses:
      200:
        description: 예측 기록 반환
    """
    try:
        predictions_history = load_predictions_history()
        
        # 날짜별로 그룹화
        grouped_predictions = {}
        for pred in predictions_history:
            date = pred.get('prediction_date', 'unknown')
            if date not in grouped_predictions:
                grouped_predictions[date] = []
            grouped_predictions[date].append(pred)
        
        # 최근 7일간의 예측만 반환
        recent_dates = sorted(grouped_predictions.keys(), reverse=True)[:7]
        recent_predictions = {}
        
        for date in recent_dates:
            recent_predictions[date] = grouped_predictions[date]
        
        return jsonify({
            'success': True,
            'predictions': recent_predictions,
            'total_predictions': len(predictions_history)
        })
        
    except Exception as e:
        print(f"예측 기록 조회 오류: {e}")
        return jsonify({'success': False, 'error': f'기록 조회 오류: {str(e)}'})

@app.route('/api/performance')
def get_performance():
    """
    성능 분석 API
    ---
    responses:
      200:
        description: 성능 분석 결과 반환
    """
    global performance_data
    
    try:
        performance = analyze_and_report_performance()
        if performance:
            performance_data = {
                'total_games': int(performance['total_games']),
                'mean_total_error': float(performance['mean_total_error']),
                'win_accuracy': float(performance['win_accuracy']),
                'mean_home_error': float(performance['mean_home_error']),
                'mean_away_error': float(performance['mean_away_error'])
            }
            return jsonify({
                'success': True,
                'performance': performance_data
            })
        else:
            return jsonify({'success': False, 'error': '성능 데이터가 없습니다.'})
    except Exception as e:
        print(f"성능 분석 API 오류: {e}")
        return jsonify({'success': False, 'error': f'성능 분석 오류: {str(e)}'})

@app.route('/api/csv-files')
def get_csv_files():
    """
    CSV 파일 목록 API
    ---
    responses:
      200:
        description: CSV 파일 목록 반환
    """
    try:
        csv_files = []
        for file in os.listdir('.'):
            if file.endswith('.csv') and 'mlb' in file.lower():
                file_size = os.path.getsize(file) / 1024  # KB
                mod_time = datetime.fromtimestamp(os.path.getmtime(file))
                csv_files.append({
                    'name': file,
                    'size': f"{file_size:.1f}KB",
                    'modified': mod_time.strftime('%Y-%m-%d %H:%M')
                })
        
        return jsonify({
            'success': True,
            'files': csv_files
        })
    except Exception as e:
        print(f"CSV 파일 목록 API 오류: {e}")
        return jsonify({'success': False, 'error': f'파일 목록 오류: {str(e)}'})

@app.route('/api/current-predictions')
def get_current_predictions():
    """현재 예측 결과 조회"""
    return jsonify({
        'success': True,
        'predictions': current_predictions
    })

@app.route('/api/save-current-predictions', methods=['POST'])
def save_current_predictions():
    """
    현재 예측 결과를 다양한 형식으로 저장
    ---
    parameters:
      - name: format
        in: body
        type: string
        required: false
        description: '저장 형식 (csv/excel/report)'
    responses:
      200:
        description: 저장 결과 반환
    """
    global current_predictions
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'})
        
        save_format = data.get('format', 'csv')
        
        if not current_predictions:
            return jsonify({'success': False, 'error': '저장할 예측 결과가 없습니다.'})
        
        filename = None
        if save_format == 'csv':
            filename = save_predictions_to_csv(current_predictions)
        elif save_format == 'excel':
            filename = save_predictions_to_excel(current_predictions)
        elif save_format == 'report':
            filename = create_prediction_report(current_predictions)
        else:
            return jsonify({'success': False, 'error': '지원하지 않는 저장 형식입니다.'})
        
        if filename:
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'현재 예측 결과가 {filename}에 저장되었습니다.'
            })
        else:
            return jsonify({'success': False, 'error': '파일 저장에 실패했습니다.'})
            
    except Exception as e:
        print(f"현재 예측 결과 저장 오류: {e}")
        return jsonify({'success': False, 'error': f'저장 오류: {str(e)}'})

@app.route('/api/download-file/<filename>')
def download_file(filename):
    """
    파일 다운로드 API
    ---
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: '다운로드할 파일명'
    responses:
      200:
        description: 파일 다운로드
    """
    try:
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': '파일을 찾을 수 없습니다.'})
    except Exception as e:
        print(f"파일 다운로드 오류: {e}")
        return jsonify({'success': False, 'error': f'다운로드 오류: {str(e)}'})

if __name__ == '__main__':
    # templates 폴더 생성
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 MLB 예측 대시보드 시작 중...")
    print("📱 브라우저에서 http://localhost:5000 으로 접속하세요")
    print("🧑‍💻 Swagger UI: http://localhost:5000/apidocs")
    app.run(debug=True, host='0.0.0.0', port=5000) 