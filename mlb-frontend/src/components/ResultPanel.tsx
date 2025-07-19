import React from "react";
const ResultPanel: React.FC<{ result: any }> = ({ result }) => {
  if (!result) return null;
  if (Array.isArray(result)) {
    return (
      <div>
        <h2>실제 결과</h2>
        <table>
          <thead>
            <tr>
              {Object.keys(result[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.map((row: any, i: number) => (
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
  return <pre>{JSON.stringify(result, null, 2)}</pre>;
};
export default ResultPanel;
