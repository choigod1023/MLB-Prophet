import React from "react";
const RefreshButton: React.FC = () => (
  <button
    className="refresh-btn"
    title="페이지 새로고침"
    onClick={() => window.location.reload()}
  >
    <i className="fas fa-sync-alt"></i>
  </button>
);
export default RefreshButton;
