import React, { memo, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import MessageActions from '../MessageActions/MessageActions';
import { useToast } from '../Toast/ToastContainer';
import { getRelativeTime, formatFullTime } from '../../utils/timeUtils';
import CodeRunner from '../CodeRunner/CodeRunner';
import './ChatBubble.css';

const ChatBubble = memo(({ 
  text, 
  sender, 
  timestamp, 
  isLoading, 
  message,
  onCopy, 
  onRegenerate, 
  onDelete,
  onEdit 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(text);
  const [copiedCode, setCopiedCode] = useState(null);
  const toast = useToast();

  const relativeTime = useMemo(() => getRelativeTime(timestamp), [timestamp]);
  const fullTime = useMemo(() => formatFullTime(timestamp), [timestamp]);

  const handleSaveEdit = () => {
    onEdit(message.id, editValue);
    setIsEditing(false);
  };

  const copyToClipboard = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(index);
    toast.success('Code copied to clipboard!');
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const components = useMemo(() => ({
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      const codeContent = String(children).replace(/\n$/, '');
      const codeIndex = `${sender}-${timestamp}-${codeContent.substring(0, 20)}`;
      
      return !inline && match ? (
        <div className="code-block-wrapper">
          <div className="code-block-header">
            <span className="code-language">{language}</span>
            <button
              className="copy-button"
              onClick={() => copyToClipboard(codeContent, codeIndex)}
              title="Copy code"
            >
              {copiedCode === codeIndex ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '4px'}}>
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Copied!
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '4px'}}>
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                  Copy
                </>
              )}
            </button>
          </div>
          <SyntaxHighlighter
            style={vscDarkPlus}
            language={language}
            PreTag="div"
            className="code-block"
            {...props}
          >
            {codeContent}
          </SyntaxHighlighter>
          <CodeRunner code={codeContent} language={language} />
        </div>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    }
  }), [copiedCode, sender, timestamp]);

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
    <div className={`chat-bubble ${sender === 'user' ? 'user-bubble' : 'ai-bubble'} ${message?.isStreaming ? 'streaming' : ''}`}>
      <div className="bubble-content">
        <div className="bubble-text">
          {isLoading ? (
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={components}
            >
              {text}
            </ReactMarkdown>
          )}
          {message?.isStreaming && <span className="streaming-cursor">▊</span>}
        </div>
      </div>
      
      <div className="chat-bubble-footer">
        <span 
          className="timestamp" 
          title={fullTime}
        >
          {relativeTime}
        </span>
      </div>

      {!isLoading && message && message.sender !== 'system' && (
        <MessageActions
          message={message}
          onCopy={onCopy}
          onRegenerate={onRegenerate}
          onDelete={onDelete}
          onEdit={onEdit}
        />
      )}
    </div>
  );
});

export default ChatBubble;