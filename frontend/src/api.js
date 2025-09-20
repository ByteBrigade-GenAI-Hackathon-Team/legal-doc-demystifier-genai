import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_BASE}/simplify/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
};

export async function askFollowUp(query, context) {
  const response = await fetch("http://localhost:8000/app/api/v1/followup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, context }),
  });
  return await response.json();
}
