import React from "react";
const PredictionSettings: React.FC = () => (
  <div className="control-panel">
    <div className="card-header">
      <h5>
        <i className="fas fa-cogs"></i> 예측 설정
      </h5>
    </div>
    <div className="card-body">
      <div className="row">
        <div className="col-12 col-sm-6 col-md-3 mb-3 mb-md-0">
          <label className="form-label">
            <i className="fas fa-tachometer-alt"></i> 예측 모드
          </label>
          <select className="form-select">
            <option value="fast">⚡ 빠른모드 (기본 특성)</option>
            <option value="full">🎯 일반모드 (상세 특성)</option>
          </select>
        </div>
        <div className="col-12 col-sm-6 col-md-3 mb-3 mb-md-0">
          <label className="form-label">
            <i className="fas fa-database"></i> 데이터 소스
          </label>
          <select className="form-select">
            <option value="recent">📊 최근 200경기</option>
            <option value="csv">💾 CSV 파일</option>
          </select>
        </div>
        <div className="col-12 col-sm-6 col-md-3 mb-3 mb-md-0">
          <label className="form-label">
            <i className="fas fa-file-csv"></i> CSV 파일 선택
          </label>
          <select className="form-select">
            <option value="">CSV 파일을 선택하세요</option>
          </select>
        </div>
        <div className="col-12 col-sm-6 col-md-3 mb-3 mb-md-0 d-flex align-items-end">
          <button className="btn btn-primary w-100">
            <i className="fas fa-magic"></i> 예측 실행
          </button>
        </div>
        <div className="col-12 col-sm-6 col-md-3 mb-3 mb-md-0 d-flex align-items-end">
          <div className="dropdown w-100">
            <button className="btn btn-success w-100 dropdown-toggle" disabled>
              <i className="fas fa-save"></i> 결과 저장
            </button>
            <ul className="dropdown-menu">
              <li>
                <a className="dropdown-item" href="#">
                  <i className="fas fa-file-csv"></i> CSV 파일로 저장
                </a>
              </li>
              <li>
                <a className="dropdown-item" href="#">
                  <i className="fas fa-file-excel"></i> Excel 파일로 저장
                </a>
              </li>
              <li>
                <a className="dropdown-item" href="#">
                  <i className="fas fa-file-text"></i> 리포트로 저장
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
);
export default PredictionSettings;
