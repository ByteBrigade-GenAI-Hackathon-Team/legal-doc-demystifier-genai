import React from "react";
import ReactMarkdown from "react-markdown";

function SimplifiedText({ text }) {
  if (!text) return null;

  return (
    <div className="p-4 mt-4 border rounded bg-white shadow">
      <h2 className="font-bold mb-2">Simplified Document</h2>
      <div className="prose max-w-none">
        <ReactMarkdown
          components={{
            span: ({ node, ...props }) => (
              <span
                {...props}
                style={{ color: props.className?.includes("red") ? "red" : "inherit" }}
              />
            ),
          }}
        >
          {text}
        </ReactMarkdown>
      </div>
    </div>
  );
}

export default SimplifiedText;
