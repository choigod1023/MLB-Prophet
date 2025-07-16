from mlb_utils import get_team_name_to_id
import json
from datetime import datetime, timedelta

PRED_FILE = 'predictions_history.json'
DAYS_BACK = 7  # 최근 7일간 경기로 매핑

def fix_predictions_file():
    with open(PRED_FILE, 'r', encoding='utf-8') as f:
        preds = json.load(f)
    name_to_id = get_team_name_to_id(DAYS_BACK)
    changed = 0
    for pred in preds:
        if 'home_id' not in pred or pred['home_id'] is None:
            pred['home_id'] = name_to_id.get(pred['home_team'])
            if pred['home_id'] is not None:
                changed += 1
        if 'away_id' not in pred or pred['away_id'] is None:
            pred['away_id'] = name_to_id.get(pred['away_team'])
            if pred['away_id'] is not None:
                changed += 1
    with open(PRED_FILE, 'w', encoding='utf-8') as f:
        json.dump(preds, f, ensure_ascii=False, indent=2)
    print(f"✅ home_id/away_id가 추가된 예측: {changed//2}건 (총 {changed}개 id)")

if __name__ == '__main__':
    fix_predictions_file() 