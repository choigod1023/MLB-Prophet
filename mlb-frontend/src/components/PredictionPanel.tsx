import React from "react";
const PredictionPanel: React.FC<{ prediction: any }> = ({ prediction }) => {
  if (!prediction) return null;
  if (Array.isArray(prediction)) {
    return (
      <div>
        <h2>예측 결과</h2>
        <table>
          <thead>
            <tr>
              {Object.keys(prediction[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {prediction.map((row: any, i: number) => (
              <tr key={i}>
                {Object.values(row).map((v, j) => (
                  <td key={j}>{String(v)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  return <pre>{JSON.stringify(prediction, null, 2)}</pre>;
};
export default PredictionPanel;
