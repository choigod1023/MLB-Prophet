import React from "react";
const PerformancePanel: React.FC = () => (
  <div className="control-panel">
    <div className="card-header">
      <h5>
        <i className="fas fa-chart-line"></i> 성능 분석
      </h5>
    </div>
    <div className="card-body">
      <button className="btn btn-success w-100">
        <i className="fas fa-analytics"></i> 성능 분석
      </button>
      <div className="mt-3"></div>
    </div>
  </div>
);
export default PerformancePanel;
