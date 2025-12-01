import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import TypingIndicator from '../TypingIndicator/TypingIndicator';
import './ChatBubble.css';

const ChatBubble = ({ text, sender, timestamp, isLoading }) => {
  const [copiedCode, setCopiedCode] = useState(null);

  const copyToClipboard = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(index);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  // Custom renderer for code blocks with copy button
  const components = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const codeString = String(children).replace(/\n$/, '');
      const codeIndex = `${sender}-${timestamp}-${codeString.substring(0, 20)}`;

      return !inline && match ? (
        <div className="code-block-container">
          <div className="code-block-header">
            <span className="code-language">{match[1]}</span>
            <button
              className="copy-button"
              onClick={() => copyToClipboard(codeString, codeIndex)}
              title="Copy code"
            >
              {copiedCode === codeIndex ? '✓ Copied!' : '📋 Copy'}
            </button>
          </div>
          <SyntaxHighlighter
            style={vscDarkPlus}
            language={match[1]}
            PreTag="div"
            className="code-block"
            {...props}
          >
            {codeString}
          </SyntaxHighlighter>
        </div>
      ) : (
        <code className="inline-code" {...props}>
          {children}
        </code>
      );
    },
  };

  // System message styling
  if (sender === 'system') {
    const getIcon = () => {
      if (text.includes('✓') || text.toLowerCase().includes('success')) return '✓';
      if (text.includes('⚠️') || text.toLowerCase().includes('warning')) return '⚠️';
      if (text.includes('❌') || text.toLowerCase().includes('error') || text.toLowerCase().includes('failed')) return '❌';
      return 'ℹ️';
    };

    return (
      <div className="chat-bubble system-bubble">
        <div className="system-content">
          <span className="system-icon">{getIcon()}</span>
          <span className="system-text">{text}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`chat-bubble ${sender}-bubble`}>
      <div className="bubble-content">
        <div className="bubble-text">
          {isLoading ? (
            <TypingIndicator />
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={components}
            >
              {text}
            </ReactMarkdown>
          )}
        </div>
        <div className="bubble-timestamp">{timestamp}</div>
      </div>
    </div>
  );
};

export default ChatBubble;