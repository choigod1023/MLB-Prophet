import React, { useState } from "react";
import * as DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

const ResultsPanel: React.FC = () => {
  const [date, setDate] = useState<Date | null>(null);

  return (
    <div className="control-panel">
      <div className="card-header">
        <h5>
          <i className="fas fa-calendar-check"></i> 경기 결과 및 예측 정확도
        </h5>
      </div>
      <div className="card-body">
        <div className="row mb-4">
          <div className="col-12 col-md-4 mb-2 mb-md-0">
            <label className="form-label">
              <i className="fas fa-calendar"></i> 날짜 선택
            </label>
            <br />
            <DatePicker.default
              selected={date}
              onChange={(d: Date | null) => setDate(d)}
              className="form-control wide-datepicker"
              dateFormat="yyyy-MM-dd"
              placeholderText="날짜를 선택하세요"
              maxDate={new Date()}
              popperPlacement="bottom"
              popperClassName="datepicker-popper"
            />
          </div>
          <div className="col-12 col-md-2 d-flex align-items-end">
            <button className="btn btn-primary w-100">
              <i className="fas fa-search"></i> 결과 조회
            </button>
          </div>
        </div>
        <div>
          <p className="text-muted text-center">
            <i className="fas fa-spinner fa-spin"></i> 경기 결과를 불러오는
            중...
          </p>
        </div>
      </div>
    </div>
  );
};
export default ResultsPanel;
