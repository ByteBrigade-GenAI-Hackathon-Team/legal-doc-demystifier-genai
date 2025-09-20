import React, { useState } from "react";
import { askFollowUp } from "../api";

function QueryBox({ setAnswer }) {
  const [query, setQuery] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const data = await askFollowUp(query);
    setAnswer(data.answer);
    setQuery("");
  };

  return (
    <div className="p-4 mt-4 border rounded bg-gray-50 shadow">
      <h2 className="font-bold mb-2">Ask a Follow-up Question</h2>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 border p-2 rounded"
          placeholder="Ask something about the document..."
        />
        <button
          type="submit"
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Ask
        </button>
      </form>
    </div>
  );
}

export default QueryBox;
