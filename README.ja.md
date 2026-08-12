# MLB Prophet - AI ベースの野球予測サービス

[한국어](README.md) · **日本語** · [English](README.en.md)

MLB-StatsAPI + 機械学習ベースの予測システムで、Web ダッシュボードと CLI の両方をサポートする完全な野球予測サービスです。

## 🚀 主な機能

- **リアルタイムデータ分析**: MLB のリアルタイムデータ収集と CSV の自動管理
- **AI 予測システム**: RandomForest / XGBoost による勝敗・スコア予測
- **Web ダッシュボード**: Flask ベースの直感的な Web インターフェース
- **CLI 対応**: コマンドラインからも全機能を利用可能
- **パフォーマンス分析**: 予測結果／実際の結果／パフォーマンス分析を統合
- **API 提供**: Swagger UI で REST API をテスト可能
- **本番デプロイ**: Docker + Nginx + Gunicorn 環境に対応

## 🗂️ プロジェクト構成

```
KBO/
├── mlb_utils.py                    # すべての共通ロジック (MLB API, 予測, 分析, CSV など)
├── mlb_dashboard.py                # Web ダッシュボード (Flask, Swagger, API)
├── mlb_cli.py                      # CLI エントリポイント (メニュー/入出力)
├── fix_predictions_history.py      # 予測履歴の補正ユーティリティ (CLI)
├── mlb_collect_all.py              # シーズン全体のデータ収集 (CLI)
├── *.csv                           # データ/結果ファイル
├── predictions_history.json         # 予測履歴
├── requirements.txt                 # Python 依存関係
├── Dockerfile                      # Docker イメージ設定
├── docker-compose.yml              # 開発用 Docker Compose
├── gunicorn.conf.py                # 本番 WSGI 設定
├── deploy-simple.sh                # 開発デプロイスクリプト
├── deploy-production.sh             # 本番デプロイスクリプト
├── webhook-receiver.py             # GitHub webhook による自動デプロイ受信機
├── webhook-receiver.service        # 上記受信機の systemd ユニット
├── nginx/                          # Nginx 設定
│   ├── nginx.conf                  # Nginx プロキシ設定
│   ├── nginx-proxy.yml             # 本番用 Docker Compose
│   └── index.html                  # 紹介ページ
├── templates/
│   └── dashboard.html               # Flask Web ダッシュボードのテンプレート
└── mlb-frontend/                   # React(Vite + TS) フロントエンド (Flask API を利用)
    └── src/                        # コンポーネント・api.ts (http://localhost:5000/api を呼び出し)
```

> 注: ダッシュボードはサーバーレンダリング（`templates/dashboard.html`）とは別に、`mlb-frontend/` に
> React 19 + Vite + TypeScript ベースの SPA も置いています（`src/api.ts` が Flask API を呼び出します）。

## ⚡️ クイックスタート

### 1. 開発環境での実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# Web ダッシュボードの起動
python mlb_dashboard.py
```

- ブラウザで http://localhost:5000 にアクセス
- Swagger UI: http://localhost:5000/apidocs（API のテスト）

### 2. CLI の実行

```bash
python mlb_cli.py
```

- メニューから今日の予測、CSV 予測、結果の照会、ファイル一覧、パフォーマンス分析などを選択

### 3. Docker 開発環境

```bash
# 開発用デプロイ
./deploy-simple.sh
```

### 4. 本番デプロイ

```bash
# 本番デプロイ (Nginx + Gunicorn)
./deploy-production.sh
```

## 🐳 Docker デプロイ

### 開発環境

```bash
docker-compose up -d --build
```

### 本番環境

```bash
docker-compose -f nginx/nginx-proxy.yml up -d --build
```

## 🌐 本番環境

### サービス構成

- **Nginx**: リバースプロキシ（80 番ポート）
- **Gunicorn**: WSGI サーバー（4 ワーカー）
- **Flask**: Web アプリケーション
- **Docker**: コンテナ化

### アクセス URL

- **紹介ページ**: http://your-domain.com
- **MLB サービス**: http://your-domain.com/mlb/
- **ヘルスチェック**: http://your-domain.com/health

## 🧩 構造と設計

### モジュールの分離

- **mlb_utils.py**: すべての共通ロジック（MLB API、チーム id のマッピング、CSV の読み込み/一覧、予測、パフォーマンス分析）
- **mlb_dashboard.py**: Flask ベースの Web ダッシュボード、API/Swagger、Web 専用の入出力
- **mlb_cli.py**: CLI のメニュー/入出力/進捗など。データ・予測・分析は mlb_utils.py から import

### 本番向けの最適化

- **Gunicorn**: マルチワーカーで同時リクエストを処理
- **Nginx**: 静的ファイルの配信、ロードバランシング
- **Docker**: コンテナ化によるデプロイの一貫性
- **環境の分離**: 開発／本番環境の分離

## 🖥️ 主な使い方

### Web ダッシュボード

- 今日の予測、CSV 予測、日付別の結果照会、パフォーマンス分析などをすべて Web 上のクリックで実行可能
- Swagger UI から API を直接テスト可能
- リアルタイムのデータ更新と予測結果の可視化

### CLI

- メニュー形式で今日の予測、CSV 予測、結果照会、ファイル一覧、パフォーマンス分析などが可能
- データ・予測・分析のロジックはすべて mlb_utils.py で処理

## 📈 予測結果の例

```
=== 개선된 모델 예측 결과 ===

New York Yankees vs Boston Red Sox (KST 06/25 08:00)
선발: Gerrit Cole vs Chris Sale
[RF] 홈팀 승률: 65.2% → 홈팀 우세  예상 스코어: 4 - 2
[XGB] 홈팀 승률: 62.8% → 홈팀 우세  예상 스코어: 5 - 3
```

## 🧠 予測モデル

勝敗（分類）とスコア（回帰）を同時に予測する機械学習パイプラインです。中核ロジックは
すべて `mlb_utils.py` にあり、MLB-StatsAPI から収集した試合ごとのボックススコアを学習
データとして使用します。

### 1. データ & 特徴量

MLB-StatsAPI のボックススコア（`boxscore_data`）から、試合単位で以下の指標を収集します。
ホーム／アウェイそれぞれについて **先発投手成績 + チームのシーズン打撃/投球指標** を使用します。

| 区分 | 特徴量 |
|------|------|
| 先発投手 | `pitcher_era`, `pitcher_whip` |
| チーム打撃 | `ops`, `avg`, `slg` |
| チーム投球 | `era`, `whip` |

- **Full モード**（14 特徴量）: 上記 7 指標 × ホーム/アウェイ
- **Fast モード**（6 特徴量）: `pitcher_era`, `ops`, `era` × ホーム/アウェイ — 応答速度を優先
- 欠損値は列平均で補完し、`±inf` は平均 → 0 の順に補正します。
- 学習には最低 50 試合以上のクリーンなデータが必要です（不足時は予測を中止）。
- 分類・回帰の入力は `StandardScaler` で標準化します。

### 2. 勝敗予測（分類）

同じ特徴量で **RandomForest と XGBoost の 2 モデルを同時に** 学習し、結果を比較提示します
（`compare_rf_xgb_decision_improved`）。ターゲットは `home_win`（ホーム勝ち=1）。

- `RandomForestClassifier(n_estimators=100, max_depth=10)`
- `XGBClassifier(n_estimators=100, max_depth=6)`
- 出力するホーム勝率は過信を防ぐため **0.05 〜 0.95 にクリッピング** します。

### 3. スコア予測（回帰）

ホーム／アウェイの得点をそれぞれ回帰で予測します。基本の比較には RF/XGB Regressor を使い、
精緻化した `predict_score_with_margin` は **XGBoost 回帰 4 種** で得点・得点差・勝率を
併せて推定します。

- モデル: `XGBRegressor(n_estimators=200, max_depth=8, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8)`
- ターゲット: `home_score`, `away_score`, `score_margin`(=ホーム−アウェイ), `home_win`
- **野球ドメインの後処理** でモデル出力を補正します:
  - 同点予測時は延長戦のホームアドバンテージ（ホーム 55%）で加重平均
  - 得点差に比例した勝率の調整（最大 ±40%）
  - 先発 ERA 差・チーム OPS 差による微調整 + ホームアドバンテージ +2%p
  - 最終的な勝率を再び 0.05 〜 0.95 にクリッピング

### 4. ベッティング機会の分析（参考用）

`analyze_betting_opportunities` が信頼度（|勝率−0.5|×2）と予想得点差をスコア化し、
`強く推奨 / 推奨 / 注目 / 様子見` の等級と根拠を併せて提示します。実際のベッティングではなく、
モデルの信頼度を解釈するための参考指標です。

### 5. パフォーマンス評価 & 再現性

- `analyze_and_report_performance`: 累積した予測 vs 実際の結果から **勝敗の的中率** と
  **平均スコア誤差**（ホーム/アウェイ/合計）を算出します。
- すべてのモデルは `random_state=42` に固定し、同じ入力 → 同じ出力を保証します。

> ⚠️ **限界**: 現状はシーズン累積指標に基づく単発予測であり、時間順の分離（walk-forward）
> 検証や、ラインナップ・球場・天候などの試合コンテキストは反映していません。予測は参考であり、
> 今後の改善対象です。

## 🔧 技術スタック

### バックエンド

- **Python 3.9**: メインの開発言語
- **Flask**: Web フレームワーク
- **Gunicorn**: 本番 WSGI サーバー
- **Pandas, NumPy**: データ処理
- **Scikit-learn, XGBoost**: 機械学習

### デプロイ & 運用

- **Docker**: コンテナ化
- **Docker Compose**: マルチサービス管理
- **Nginx**: リバースプロキシ
- **Gunicorn**: 本番 WSGI サーバー

### フロントエンド

- **React 19 + Vite + TypeScript**: `mlb-frontend/` の SPA
- **Chart.js**: 予測／パフォーマンスの可視化
- **Bootstrap, react-datepicker**: UI

### データ & API

- **MLB-StatsAPI**: リアルタイムデータ
- **CSV/JSON**: データ保存
- **Swagger**: API ドキュメント化

## 🔑 環境変数

コードが実際に参照する環境変数は次のとおりです（すべてデフォルト値があるため未設定でも動作します）。

| 変数 | 場所 | 説明 | デフォルト |
|------|------|------|--------|
| `FLASK_ENV` | `mlb_dashboard.py` | `development` なら Flask の debug モードを有効化 | （未設定） |
| `WEBHOOK_SECRET` | `webhook-receiver.py` | GitHub webhook の署名検証用シークレット | `your-webhook-secret` |
| `PROJECT_DIR` | `webhook-receiver.py` | 自動デプロイ時に pull/再起動するプロジェクトのパス | `/home/ubuntu/MLB-Proph` |

## 🚀 デプロイガイド

### 1. 開発環境

```bash
# ローカル実行
python mlb_dashboard.py

# Docker 開発
./deploy-simple.sh
```

### 2. 本番環境

```bash
# 本番デプロイ
./deploy-production.sh

# または手動デプロイ
docker-compose -f nginx/nginx-proxy.yml up -d --build
```

### 3. ドメイン設定

- DNS の A レコード設定（ドメイン → サーバー IP）
- nginx/nginx.conf の server_name を修正
- SSL 証明書の設定（任意）

## 📊 パフォーマンスと特徴

### 精度の向上

- 継続的なモデル改善
- データ品質の管理
- 予測成績のトラッキング

### ユーザー体験

- 直感的な Web インターフェース
- リアルタイムのデータ更新
- 多様な結果フォーマットの提供（CSV, Excel, レポート）

### 拡張性

- Docker ベースのコンテナ化
- Nginx によるロードバランシング
- マルチワーカーアーキテクチャ

## 🔧 メンテナンス

### ログの確認

```bash
# 全体のログ
docker-compose -f nginx/nginx-proxy.yml logs -f

# 特定サービスのログ
docker-compose -f nginx/nginx-proxy.yml logs -f mlb-backend
docker-compose -f nginx/nginx-proxy.yml logs -f nginx-proxy
```

### サービス管理

```bash
# サービスの停止
docker-compose -f nginx/nginx-proxy.yml down

# サービスの再起動
docker-compose -f nginx/nginx-proxy.yml restart

# キャッシュ無しで再ビルド
docker-compose -f nginx/nginx-proxy.yml up -d --build --no-cache
```

## 📝 ライセンス / コントリビュート

- 教育・研究目的、MLB-StatsAPI のポリシーを遵守
- バグ報告・機能提案・コード改善を歓迎します

---

**最終更新**: 2025 年 7 月
**バージョン**: v7.0（Docker + Nginx + 本番環境対応）
**ライセンス**: MIT License

---

## 👤 コントリビューションと開発環境

| 項目 | 内容 |
|---|---|
| **貢献比率** | **100%**（単独開発） |
| **コミット** | 59 / 59（本人 / 全人力コミット） |
| **参加人数** | 1 名 |
| **AI コーディングツール** | Claude Code |

<sub>集計基準（2026-08-12 時点のスナップショット）: origin の **すべてのブランチ** から到達可能なコミット（マージコミット・空コミットは除外）を対象とし、コミットの author メールアドレス基準で、同一人物の複数のメールアドレスは合算、ボット・自動化コミットは除外しています。</sub>
