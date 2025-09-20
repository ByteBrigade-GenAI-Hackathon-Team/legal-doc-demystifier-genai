import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_BASE}/simplify/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
};

export const askFollowUp = async (query) => {
  const res = await axios.post(`${API_BASE}/followup/`, { query });
  return res.data;
};
