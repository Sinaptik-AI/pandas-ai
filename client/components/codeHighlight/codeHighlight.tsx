import React, { useState } from "react";
import { MdOutlineContentCopy } from "react-icons/md";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { nightOwl } from "react-syntax-highlighter/dist/esm/styles/prism";

interface CodeHighlight {
  code: string;
  codeExecution: string;
}

const CodeHighlight = ({ code, codeExecution }: CodeHighlight) => {
  const [copySuccess, setCopySuccess] = useState(false);
  const copyToClipboard = () => {
    const codeElement = document.createElement("textarea");
    codeElement.value = code;
    document.body.appendChild(codeElement);
    codeElement.select();
    document.execCommand("copy");
    document.body.removeChild(codeElement);
    setCopySuccess(true);
    setTimeout(() => {
      setCopySuccess(false);
    }, 2000);
  };
  const styles = {
    container: {
      backgroundColor: "#011627",
      color: "#ABB2BF",
      fontFamily: "monospace",
      padding: "10px",
    },
  };
  return (
    <pre
      className="code-content code-syntax-highlight"
      style={
        codeExecution == "Code Execution" ||
        codeExecution == "Parse Output" ||
        codeExecution == "Validating Output"
          ? {}
          : styles.container
      }
    >
      <div
        className="copy-btn-logs flex justify-end bg-darkViolet "
        style={{ backgroundColor: "#011627" }}
      >
        <span className="copy-btn-logs mr-5 mt-3 flex justify-end  text-white ">
          <MdOutlineContentCopy
            onClick={copyToClipboard}
            className="cursor-pointer"
          />
        </span>
        {copySuccess && <span className="copied-text">Copied</span>}
      </div>
      <SyntaxHighlighter
        className="SyntaxHighlighter"
        language="python"
        style={nightOwl}
      >
        {code}
      </SyntaxHighlighter>
    </pre>
  );
};
export default CodeHighlight;
