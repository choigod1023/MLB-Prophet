const API_BASE = "http://localhost:5000/api";

export async function fetchCsvFiles() {
  const res = await fetch(`${API_BASE}/csv-files`);
  return res.json();
}

export async function predict(data: any) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function checkResults(date: string) {
  const res = await fetch(`${API_BASE}/check-results`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date }),
  });
  return res.json();
}

export async function getPerformance() {
  const res = await fetch(`${API_BASE}/performance`);
  return res.json();
}

export async function downloadFile(filename: string) {
  window.open(`${API_BASE}/download-file/${filename}`, "_blank");
}
