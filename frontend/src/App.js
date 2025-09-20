import React, { useState } from "react";
import "./App.css";

function App() {
  const [documentText, setDocumentText] = useState("");
  const [userRoleGoal, setUserRoleGoal] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [docId, setDocId] = useState("");
  const [query, setQuery] = useState("");
  const [queryResults, setQueryResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult("");
    setDocId("");
    setQueryResults([]);

    let res, data;
    if (file) {
      const formData = new FormData();
      formData.append("user_role_goal", userRoleGoal);
      formData.append("file", file);

      res = await fetch("http://localhost:8000/api/v1/simplify-file", {
        method: "POST",
        body: formData,
      });
    } else {
      res = await fetch("http://localhost:8000/api/v1/simplify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_text: documentText,
          user_role_goal: userRoleGoal,
        }),
      });
    }
    data = await res.json();
    setResult(data.simplified_document || data.detail || "No result");
    setDocId(data.doc_id || "");
    setLoading(false);
  };

  const handleQuery = async () => {
    if (!query.trim() || !docId) return;

    const res = await fetch("http://localhost:8000/api/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, doc_id: docId }),
    });
    const data = await res.json();
    setQueryResults([...queryResults, data.answer]);
    setQuery("");
  };

  return (
    <div className="app-container">
      <h2 className="title">Legal Document Demystifier</h2>

      <form className="input-section" onSubmit={handleSubmit}>
        <div className="card dark-card">
          <label>Document Input</label>
          <textarea
            className="input-box"
            value={documentText}
            onChange={(e) => setDocumentText(e.target.value)}
            rows={4}
            disabled={!!file}
            placeholder="Paste your legal document..."
          />
          <label>Your Role/Goal</label>
          <input
            className="input-box"
            type="text"
            value={userRoleGoal}
            onChange={(e) => setUserRoleGoal(e.target.value)}
            placeholder="Tenant, Freelancer..."
            required
          />
        </div>

        <div className="card upload-box">
          <h4>Upload File / Image</h4>
          <input
            type="file"
            className="file-input"
            accept=".txt,.pdf,.docx,.jpg,.jpeg,.png"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <button type="submit" className="btn" disabled={loading}>
            {loading ? "Processing..." : "Submit"}
          </button>
        </div>
      </form>

      {result && (
        <div className="card result-box">
          <h3>Result:</h3>
          <pre
            className="result-text"
            dangerouslySetInnerHTML={{ __html: result }}
          />
          <em className="disclaimer">
            IMPORTANT DISCLAIMER: This is for educational purposes only, not
            legal advice.
          </em>

          <div className="query-section">
            <input
              className="input-box"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a follow-up question..."
            />
            <button className="btn" onClick={handleQuery}>
              Ask
            </button>
          </div>
        </div>
      )}

      {queryResults.map((ans, idx) => (
        <div key={idx} className="card result-box">
          <h3>Follow-up Answer:</h3>
          <pre
            className="result-text"
            dangerouslySetInnerHTML={{ __html: ans }}
          />
          <em className="disclaimer">
            IMPORTANT DISCLAIMER: This is for educational purposes only, not
            legal advice.
          </em>
        </div>
      ))}
    </div>
  );
}

export default App;
