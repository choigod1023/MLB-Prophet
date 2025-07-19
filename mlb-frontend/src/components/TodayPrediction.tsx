import React from "react";
const TodayPrediction: React.FC = () => (
  <div className="control-panel">
    <div className="card-header">
      <h5>
        <i className="fas fa-bullseye"></i> 오늘 경기 예측
      </h5>
    </div>
    <div className="card-body">
      <div>
        <div className="alert alert-info">
          <h6>
            <i className="fas fa-info-circle"></i> 예측 시스템 안내
          </h6>
          <ul className="mb-0">
            <li>
              <strong>실시간 예측:</strong> 오늘 경기에 대한 실시간 예측을
              제공합니다
            </li>
            <li>
              <strong>일관성 보장:</strong> 같은 데이터로 예측하면 항상 동일한
              결과가 나옵니다
            </li>
            <li>
              <strong>시차 고려:</strong> 한국 시간 기준으로 예측합니다
              (미국에서는 내일 경기)
            </li>
          </ul>
        </div>
        <p className="text-muted text-center px-2">
          <i className="fas fa-magic"></i> "예측 실행" 버튼을 클릭하여 오늘 경기
          예측을 확인하세요
        </p>
      </div>
    </div>
  </div>
);
export default TodayPrediction;
