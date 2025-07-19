import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "@fortawesome/fontawesome-free/css/all.min.css";
import "./index.css";
import "./Dashboard.css";
import Header from "./components/Header";
import PredictionSettings from "./components/PredictionSettings";
import PerformancePanel from "./components/PerformancePanel";
import TodayPrediction from "./components/TodayPrediction";
import ResultsPanel from "./components/ResultsPanel";
import RefreshButton from "./components/RefreshButton";

const App: React.FC = () => {
  return (
    <div className="main-container ">
      <Header />
      <PredictionSettings />
      <PerformancePanel />
      <TodayPrediction />
      <ResultsPanel />
      <RefreshButton />
    </div>
  );
};

export default App;
