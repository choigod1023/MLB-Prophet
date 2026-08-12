# MLB Prophet — AI-Powered Baseball Prediction Service

[한국어](README.md) · [日本語](README.ja.md) · **English**

A complete baseball prediction service built on MLB-StatsAPI and machine learning, with both a web dashboard and a CLI.

## 🚀 Features

- **Live data analysis**: collects live MLB data and manages CSVs automatically
- **AI prediction system**: RandomForest / XGBoost win-loss and score prediction
- **Web dashboard**: an intuitive Flask-based interface
- **CLI support**: every feature is available from the command line
- **Performance analysis**: predictions, actual results, and performance analysis in one place
- **API**: REST API testable through Swagger UI
- **Production deployment**: Docker + Nginx + Gunicorn

## 🗂️ Project structure

```
KBO/
├── mlb_utils.py                    # all shared logic (MLB API, prediction, analysis, CSV, …)
├── mlb_dashboard.py                # web dashboard (Flask, Swagger, API)
├── mlb_cli.py                      # CLI entry point (menu / I/O)
├── fix_predictions_history.py      # prediction-history correction utility (CLI)
├── mlb_collect_all.py              # full-season data collection (CLI)
├── *.csv                           # data / result files
├── predictions_history.json         # prediction history
├── requirements.txt                 # Python dependencies
├── Dockerfile                      # Docker image configuration
├── docker-compose.yml              # Docker Compose for development
├── gunicorn.conf.py                # production WSGI configuration
├── deploy-simple.sh                # development deployment script
├── deploy-production.sh             # production deployment script
├── webhook-receiver.py             # auto-deploy receiver driven by GitHub webhooks
├── webhook-receiver.service        # systemd unit for the receiver above
├── nginx/                          # Nginx configuration
│   ├── nginx.conf                  # Nginx proxy configuration
│   ├── nginx-proxy.yml             # production Docker Compose
│   └── index.html                  # landing page
├── templates/
│   └── dashboard.html               # Flask web dashboard template
└── mlb-frontend/                   # React (Vite + TS) frontend consuming the Flask API
    └── src/                        # components and api.ts (calls http://localhost:5000/api)
```

> Note: alongside the server-rendered dashboard (`templates/dashboard.html`), `mlb-frontend/` holds a
> React 19 + Vite + TypeScript SPA (`src/api.ts` calls the Flask API).

## ⚡️ Quick start

### 1. Development

```bash
# install dependencies
pip install -r requirements.txt

# run the web dashboard
python mlb_dashboard.py
```

- Open http://localhost:5000
- Swagger UI: http://localhost:5000/apidocs (API testing)

### 2. CLI

```bash
python mlb_cli.py
```

- Choose today's predictions, CSV predictions, result lookup, file listing, performance analysis, and more from the menu

### 3. Docker development environment

```bash
# development deployment
./deploy-simple.sh
```

### 4. Production deployment

```bash
# production deployment (Nginx + Gunicorn)
./deploy-production.sh
```

## 🐳 Docker deployment

### Development

```bash
docker-compose up -d --build
```

### Production

```bash
docker-compose -f nginx/nginx-proxy.yml up -d --build
```

## 🌐 Production environment

### Service layout

- **Nginx**: reverse proxy (port 80)
- **Gunicorn**: WSGI server (4 workers)
- **Flask**: the web application
- **Docker**: containerization

### URLs

- **Landing page**: http://your-domain.com
- **MLB service**: http://your-domain.com/mlb/
- **Health check**: http://your-domain.com/health

## 🧩 Structure and design

### Module separation

- **mlb_utils.py**: all shared logic (MLB API, team-id mapping, CSV loading/listing, prediction, performance analysis)
- **mlb_dashboard.py**: the Flask web dashboard, API/Swagger, and web-specific I/O
- **mlb_cli.py**: CLI menus, I/O, and progress; data, prediction, and analysis are imported from mlb_utils.py

### Production optimizations

- **Gunicorn**: multiple workers handle concurrent requests
- **Nginx**: static file serving and load balancing
- **Docker**: containerization for consistent deployments
- **Environment separation**: development and production kept apart

## 🖥️ Usage

### Web dashboard

- Today's predictions, CSV predictions, results by date, and performance analysis — all a click away
- Test the API directly from Swagger UI
- Live data updates and visualized prediction results

### CLI

- A menu-driven flow for today's predictions, CSV predictions, results, file listing, and performance analysis
- All data, prediction, and analysis logic lives in mlb_utils.py

## 📈 Example prediction output

```
=== 개선된 모델 예측 결과 ===

New York Yankees vs Boston Red Sox (KST 06/25 08:00)
선발: Gerrit Cole vs Chris Sale
[RF] 홈팀 승률: 65.2% → 홈팀 우세  예상 스코어: 4 - 2
[XGB] 홈팀 승률: 62.8% → 홈팀 우세  예상 스코어: 5 - 3
```

## 🧠 The prediction model

A machine-learning pipeline that predicts the winner (classification) and the score (regression) together.
All the core logic lives in `mlb_utils.py`, trained on per-game box scores collected from MLB-StatsAPI.

### 1. Data and features

Per-game metrics are collected from MLB-StatsAPI box scores (`boxscore_data`). For each of home and away,
the model uses the **starting pitcher's record plus team season batting/pitching metrics**.

| Category | Features |
|------|------|
| Starting pitcher | `pitcher_era`, `pitcher_whip` |
| Team batting | `ops`, `avg`, `slg` |
| Team pitching | `era`, `whip` |

- **Full mode** (14 features): the seven metrics above × home/away
- **Fast mode** (6 features): `pitcher_era`, `ops`, `era` × home/away — prioritizes response time
- Missing values are imputed with the column mean; `±inf` is corrected to the mean and then to 0
- Training requires at least 50 games of clean data (prediction aborts otherwise)
- Classification and regression inputs are standardized with `StandardScaler`

### 2. Win/loss prediction (classification)

**RandomForest and XGBoost are trained simultaneously** on the same features and their results presented
side by side (`compare_rf_xgb_decision_improved`). The target is `home_win` (home victory = 1).

- `RandomForestClassifier(n_estimators=100, max_depth=10)`
- `XGBClassifier(n_estimators=100, max_depth=6)`
- Output home win probabilities are **clipped to 0.05–0.95** to avoid overconfidence

### 3. Score prediction (regression)

Home and away runs are each predicted by regression. The basic comparison uses RF/XGB regressors, while the
refined `predict_score_with_margin` estimates score, margin, and win probability together with **four XGBoost regressors**.

- Model: `XGBRegressor(n_estimators=200, max_depth=8, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8)`
- Targets: `home_score`, `away_score`, `score_margin` (= home − away), `home_win`
- **Baseball-domain post-processing** corrects the raw model output:
  - On a predicted tie, weight-average in the extra-innings home advantage (home 55%)
  - Adjust the win probability in proportion to the margin (up to ±40%)
  - Fine-tune by the starters' ERA gap and the teams' OPS gap, plus a +2pp home advantage
  - Clip the final probability back into 0.05–0.95

### 4. Betting-opportunity analysis (for reference)

`analyze_betting_opportunities` scores confidence (|p − 0.5| × 2) together with the predicted margin and
labels each game `strong pick / pick / watch / pass` with reasoning. It is a way to interpret model
confidence, not a betting instrument.

### 5. Performance evaluation and reproducibility

- `analyze_and_report_performance`: computes the **win/loss hit rate** and **mean score error**
  (home/away/total) from accumulated predictions versus actual results.
- Every model fixes `random_state=42` so the same input yields the same output.

> ⚠️ **Limitations**: today this is a one-shot prediction from season-cumulative metrics. It does not use
> walk-forward temporal validation, nor game context such as lineups, park, or weather. Predictions are for
> reference and are a target for future improvement.

## 🔧 Tech stack

### Backend

- **Python 3.9**: the main language
- **Flask**: web framework
- **Gunicorn**: production WSGI server
- **Pandas, NumPy**: data processing
- **Scikit-learn, XGBoost**: machine learning

### Deployment & operations

- **Docker**: containerization
- **Docker Compose**: multi-service management
- **Nginx**: reverse proxy
- **Gunicorn**: production WSGI server

### Frontend

- **React 19 + Vite + TypeScript**: the `mlb-frontend/` SPA
- **Chart.js**: prediction and performance visualization
- **Bootstrap, react-datepicker**: UI

### Data & APIs

- **MLB-StatsAPI**: live data
- **CSV/JSON**: storage
- **Swagger**: API documentation

## 🔑 Environment variables

The variables the code actually reads (all have defaults, so it runs without them):

| Variable | Where | Description | Default |
|------|------|------|--------|
| `FLASK_ENV` | `mlb_dashboard.py` | Enables Flask debug mode when set to `development` | (unset) |
| `WEBHOOK_SECRET` | `webhook-receiver.py` | Secret for verifying GitHub webhook signatures | `your-webhook-secret` |
| `PROJECT_DIR` | `webhook-receiver.py` | Project path to pull/restart on auto-deploy | `/home/ubuntu/MLB-Proph` |

## 🚀 Deployment guide

### 1. Development

```bash
# local run
python mlb_dashboard.py

# Docker development
./deploy-simple.sh
```

### 2. Production

```bash
# production deployment
./deploy-production.sh

# or deploy manually
docker-compose -f nginx/nginx-proxy.yml up -d --build
```

### 3. Domain setup

- Set the DNS A record (domain → server IP)
- Update `server_name` in nginx/nginx.conf
- Configure an SSL certificate (optional)

## 📊 Performance and characteristics

### Accuracy improvements

- Continuous model refinement
- Data-quality management
- Tracking of prediction performance

### User experience

- An intuitive web interface
- Live data updates
- Multiple output formats (CSV, Excel, reports)

### Scalability

- Docker-based containerization
- Nginx load balancing
- Multi-worker architecture

## 🔧 Maintenance

### Checking logs

```bash
# all logs
docker-compose -f nginx/nginx-proxy.yml logs -f

# a specific service
docker-compose -f nginx/nginx-proxy.yml logs -f mlb-backend
docker-compose -f nginx/nginx-proxy.yml logs -f nginx-proxy
```

### Managing services

```bash
# stop
docker-compose -f nginx/nginx-proxy.yml down

# restart
docker-compose -f nginx/nginx-proxy.yml restart

# rebuild without cache
docker-compose -f nginx/nginx-proxy.yml up -d --build --no-cache
```

## 📝 License / contributing

- For education and research, in compliance with MLB-StatsAPI policy
- Bug reports, feature suggestions, and code improvements are welcome

---

**Last updated**: July 2025
**Version**: v7.0 (Docker + Nginx + production support)
**License**: MIT License

---

## 👤 Contribution & development environment

| Item | Detail |
|---|---|
| **Contribution share** | **100%** (solo development) |
| **Commits** | 59 / 59 (mine / all human commits) |
| **Contributors** | 1 |
| **AI coding tool** | Claude Code |

<sub>Counting basis (snapshot as of 2026-08-12): commits reachable from **every branch** on origin (merge commits and empty commits excluded), counted by commit author email with one person’s multiple addresses merged; bot and automation commits are excluded.</sub>
