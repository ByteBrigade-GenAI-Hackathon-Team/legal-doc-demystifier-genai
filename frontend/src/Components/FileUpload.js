import React, { useState } from "react";
import { uploadFile } from "../api";

function FileUpload({ setSimplifiedText }) {
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a file");

    const data = await uploadFile(file);
    setSimplifiedText(data.simplified_text);
  };

  return (
    <div className="p-4 border rounded shadow bg-gray-50">
      <h2 className="font-bold mb-2">Upload Document</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="mb-2"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Simplify
        </button>
      </form>
    </div>
  );
}

export default FileUpload;
