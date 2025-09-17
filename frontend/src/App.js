import React, { useState } from 'react';

function App() {
  const [documentText, setDocumentText] = useState('');
  const [userRoleGoal, setUserRoleGoal] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  // Handle either text or file POST
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult('');

    let res, data;

    if (file) {
      const formData = new FormData();
      formData.append('user_role_goal', userRoleGoal);
      formData.append('file', file);

      res = await fetch('http://localhost:8000/api/v1/simplify-file', {
        method: 'POST',
        body: formData,
      });
    } else {
      res = await fetch('http://localhost:8000/api/v1/simplify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_text: documentText,
          user_role_goal: userRoleGoal,
        }),
      });
    }
    data = await res.json();
    setResult(data.simplified_document || data.detail || 'No result');
    setLoading(false);
  };

  return (
    <div>
      <h2>Legal Document Demystifier</h2>
      <form onSubmit={handleSubmit}>
        <label>Paste your document text:</label><br/>
        <textarea
          value={documentText}
          onChange={e => setDocumentText(e.target.value)}
          rows={8}
          cols={50}
          disabled={!!file}
          placeholder="Paste here or upload a file below"
        /><br/>
        <label>Upload PDF/DOCX/Image:</label>
        <input
          type="file"
          accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
          onChange={e => setFile(e.target.files[0])}
        /><br/>
        <label>Your role/goal:</label>
        <input
          type="text"
          value={userRoleGoal}
          onChange={e => setUserRoleGoal(e.target.value)}
          required
        /><br/>
        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Submit"}
        </button>
      </form>
      {result && (
        <div>
          <h3>Result:</h3>
          <pre style={{whiteSpace: 'pre-wrap'}}>{result}</pre>
          <em>Disclaimer: For information only, not legal advice.</em>
        </div>
      )}
    </div>
  );
}
export default App;
