import React from "react";
type Props = { files: string[]; onDownload: (filename: string) => void };
const FileDownloadPanel: React.FC<Props> = ({ files, onDownload }) => (
  <div>
    <h2>CSV 파일 다운로드</h2>
    <ul>
      {files.map((f) => (
        <li key={f}>
          {f} <button onClick={() => onDownload(f)}>다운로드</button>
        </li>
      ))}
    </ul>
  </div>
);
export default FileDownloadPanel;
