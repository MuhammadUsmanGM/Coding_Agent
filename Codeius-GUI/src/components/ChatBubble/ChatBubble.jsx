import React from 'react';
import './ChatBubble.css';

const ChatBubble = ({ text, sender, timestamp }) => {
  // Function to split text into regular text and code blocks
  const parseTextWithCode = (text) => {
    // Regular expression to match code blocks (both ``` and ` syntax)
    const codeBlockRegex = /(```[\s\S]*?```|`[^`\n]+`)/g;
    const parts = text.split(codeBlockRegex);

    return parts.map((part, index) => {
      // Check if this part is a code block
      if (part.startsWith('```') && part.endsWith('```')) {
        // Extract language if specified (after the first ```)
        const codeLines = part.slice(3, -3).split('\n');
        const language = codeLines[0].trim(); // First line could be the language
        let codeContent;

        // If first line is a language specifier, remove it from code content
        if (codeLines.length > 1) {
          codeContent = codeLines.slice(1).join('\n');
        } else {
          codeContent = codeLines[0]; // Just first line without language spec
        }

        return (
          <div key={index} className="code-block-container">
            <pre className="code-block">
              <code>{codeContent}</code>
            </pre>
          </div>
        );
      } else if (part.startsWith('`') && part.endsWith('`')) {
        // Inline code block
        const inlineCode = part.slice(1, -1);
        return <code key={index} className="inline-code">{inlineCode}</code>;
      } else {
        // Regular text
        return <span key={index}>{part}</span>;
      }
    });
  };

  return (
    <div className={`chat-bubble ${sender}-bubble`}>
      <div className="bubble-content">
        <div className="bubble-text">
          {parseTextWithCode(text)}
        </div>
        <div className="bubble-timestamp">{timestamp}</div>
      </div>
    </div>
  );
};

export default ChatBubble;