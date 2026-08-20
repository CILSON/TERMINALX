/* ═══════════════════════════════════════════════════════
 * TerminalX — AI Chat Panel (Ask AI about markets)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useState, useRef, useEffect } from 'react';

interface ChatMessage {
  role: 'user' | 'ai';
  content: string;
  relatedAssets?: string[];
  sentiment?: string;
  timestamp: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function AIChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput('');

    const userMsg: ChatMessage = {
      role: 'user',
      content: question,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/ai/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();

      const aiMsg: ChatMessage = {
        role: 'ai',
        content: data.answer || 'Unable to process your question.',
        relatedAssets: data.related_assets || [],
        sentiment: data.sentiment,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: 'Error connecting to AI service. Check if backend is running.',
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestedQuestions = [
    "What's driving NIFTY today?",
    "Is gold a buy right now?",
    "USDINR outlook this week?",
    "Bitcoin analysis",
  ];

  return (
    <div className="ai-chat-panel">
      <div className="panel-header">
        <span className="panel-header-title">🤖 Ask AI</span>
        <span className="panel-header-count" style={{ color: 'var(--accent-cyan)' }}>GEMINI</span>
      </div>

      <div className="ai-chat-messages scrollable" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="ai-chat-welcome">
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>🧠</div>
            <div style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: '8px' }}>
              Market Intelligence AI
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '16px' }}>
              Ask any question about markets, stocks, crypto, or macro.
            </div>
            <div className="ai-chat-suggestions">
              {suggestedQuestions.map((q) => (
                <button
                  key={q}
                  className="ai-chat-suggestion"
                  onClick={() => { setInput(q); inputRef.current?.focus(); }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`ai-chat-msg ai-chat-msg-${msg.role}`}>
            <div className="ai-chat-msg-header">
              <span>{msg.role === 'user' ? '👤 You' : '🤖 AI'}</span>
              <span className="ai-chat-msg-time">{msg.timestamp}</span>
            </div>
            <div className="ai-chat-msg-body">{msg.content}</div>
            {msg.relatedAssets && msg.relatedAssets.length > 0 && (
              <div className="ai-chat-msg-assets">
                {msg.relatedAssets.map((a) => (
                  <span key={a} className="ai-chat-asset-tag">{a}</span>
                ))}
              </div>
            )}
            {msg.sentiment && (
              <span className={`ai-chat-sentiment ai-chat-sentiment-${msg.sentiment}`}>
                {msg.sentiment === 'bullish' ? '▲' : msg.sentiment === 'bearish' ? '▼' : '●'} {msg.sentiment}
              </span>
            )}
          </div>
        ))}

        {loading && (
          <div className="ai-chat-msg ai-chat-msg-ai">
            <div className="ai-chat-msg-header">
              <span>🤖 AI</span>
            </div>
            <div className="ai-chat-typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
      </div>

      <div className="ai-chat-input-area">
        <input
          ref={inputRef}
          className="ai-chat-input"
          placeholder="Ask about markets, assets, strategy..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="ai-chat-send"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
        >
          ↵
        </button>
      </div>
    </div>
  );
}
