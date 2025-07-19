import React from "react";
type Props = { files: string[]; value: string; onChange: (v: string) => void };
const CsvSelector: React.FC<Props> = ({ files, value, onChange }) => (
  <select value={value} onChange={(e) => onChange(e.target.value)}>
    <option value="">CSV 파일 선택</option>
    {files.map((f) => (
      <option key={f} value={f}>
        {f}
      </option>
    ))}
  </select>
);
export default CsvSelector;
