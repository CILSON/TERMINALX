/* ═══════════════════════════════════════════════════════
 * TerminalX — Market Brief (AI-generated daily overview)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useState, useEffect } from 'react';
import { Badge } from '@/components/common/Badge';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface MarketBrief {
  title: string;
  summary: string;
  top_movers: Array<{ symbol: string; direction: string; reason: string }>;
  watchlist: Array<{ symbol: string; reason: string }>;
  risk_radar: string;
}

export function MarketBriefPanel() {
  const [brief, setBrief] = useState<MarketBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBrief();
  }, []);

  const fetchBrief = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/api/ai/market-brief`);
      const data = await res.json();
      setBrief(data.brief);
    } catch (e) {
      setError('Failed to generate market brief');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="market-brief">
        <div className="panel-header">
          <span className="panel-header-title">📋 Market Brief</span>
          <span className="panel-header-count" style={{ color: 'var(--accent-cyan)' }}>AI</span>
        </div>
        <div className="market-brief-loading">
          <div className="ai-chat-typing" style={{ justifyContent: 'center', padding: '40px' }}>
            <span></span><span></span><span></span>
          </div>
          <div style={{ color: 'var(--text-secondary)', textAlign: 'center', fontSize: '12px' }}>
            Generating market intelligence...
          </div>
        </div>
      </div>
    );
  }

  if (error || !brief) {
    return (
      <div className="market-brief">
        <div className="panel-header">
          <span className="panel-header-title">📋 Market Brief</span>
        </div>
        <div style={{ padding: '20px', color: 'var(--text-secondary)', textAlign: 'center' }}>
          {error || 'No brief available'}
          <button className="ai-chat-suggestion" onClick={fetchBrief} style={{ marginTop: '12px' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="market-brief">
      <div className="panel-header">
        <span className="panel-header-title">📋 Market Brief</span>
        <span className="panel-header-count" style={{ color: 'var(--accent-cyan)' }}>AI</span>
      </div>

      <div className="scrollable">
        {/* Title */}
        <div className="market-brief-title">{brief.title}</div>

        {/* Summary */}
        <div className="market-brief-section">
          <div className="market-brief-text">{brief.summary}</div>
        </div>

        {/* Top Movers */}
        {brief.top_movers && brief.top_movers.length > 0 && (
          <div className="market-brief-section">
            <div className="ai-panel-label">Top Movers</div>
            {brief.top_movers.map((m, i) => (
              <div key={i} className="market-brief-mover">
                <Badge
                  text={`${m.direction === 'up' ? '▲' : '▼'} ${m.symbol}`}
                  variant={m.direction === 'up' ? 'bullish' : 'bearish'}
                />
                <span className="market-brief-mover-reason">{m.reason}</span>
              </div>
            ))}
          </div>
        )}

        {/* Watchlist */}
        {brief.watchlist && brief.watchlist.length > 0 && (
          <div className="market-brief-section">
            <div className="ai-panel-label">Watch Today</div>
            {brief.watchlist.map((w, i) => (
              <div key={i} className="market-brief-watch">
                <span className="market-brief-watch-symbol">{typeof w === 'string' ? w : w.symbol}</span>
                <span className="market-brief-watch-reason">{typeof w === 'string' ? '' : w.reason}</span>
              </div>
            ))}
          </div>
        )}

        {/* Risk Radar */}
        {brief.risk_radar && (
          <div className="market-brief-section">
            <div className="ai-panel-label">Risk Radar</div>
            <div className="market-brief-text" style={{ color: 'var(--accent-yellow)', fontSize: '12px' }}>
              ⚠ {brief.risk_radar}
            </div>
          </div>
        )}

        {/* Refresh */}
        <button className="market-brief-refresh" onClick={fetchBrief}>
          ↻ Refresh Brief
        </button>
      </div>
    </div>
  );
}
