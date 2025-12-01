import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';
import './SharedSessionView.css';

const SharedSessionView = () => {
  const { sessionId } = useParams();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/sessions/${sessionId}/public`);
        if (!response.ok) throw new Error('Failed to load session');
        const data = await response.json();
        setMessages(data.messages || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [sessionId]);

  if (loading) return <div className="shared-loading"><LoadingSpinner /></div>;
  if (error) return <div className="shared-error">Error: {error}</div>;

  return (
    <div className="shared-session-container">
      <header className="shared-header">
        <div className="logo">
          <img src="/logo.png" alt="Codeius" />
          <span>Codeius Shared Session</span>
        </div>
        <a href="/" className="try-btn">Try Codeius</a>
      </header>

      <div className="shared-chat-content">
        {messages.map((msg, index) => (
          <div key={index} className={`shared-bubble ${msg.sender === 'user' ? 'user' : 'ai'}`}>
            <div className="bubble-header">
              <span className="sender-name">{msg.sender === 'user' ? 'User' : 'Codeius AI'}</span>
              <span className="timestamp">{new Date(msg.timestamp).toLocaleString()}</span>
            </div>
            <div className="markdown-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {msg.text}
              </ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SharedSessionView;
