/* ═══════════════════════════════════════════════════════
 * TerminalX — Right Panel (AI Analysis + Market Snapshot)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useNewsStore } from '@/stores/newsStore';
import { AIPanel } from '@/components/ai/AIPanel';
import { MarketSnapshot } from '@/components/market/MarketSnapshot';

export function RightPanel() {
  const selectedArticle = useNewsStore((s) => s.selectedArticle);

  return (
    <aside className="panel right-panel">
      {selectedArticle && selectedArticle.ai_analysis ? (
        <AIPanel analysis={selectedArticle.ai_analysis} />
      ) : (
        <div className="right-panel-default">
          <div className="ai-panel">
            <div className="panel-header">
              <span className="panel-header-title">AI Analysis</span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="icon-btn" title="Refresh" onClick={() => alert('AI Analysis refreshed.')}>[R]</button>
                <button className="icon-btn" title="Expand" onClick={() => alert('Expansion view not available in this demo.')}>[X]</button>
              </div>
            </div>
            <div className="ai-panel-placeholder">
              <div style={{ padding: '20px', color: 'var(--text-secondary)', fontSize: '12px' }}>
                Select an asset or article to view AI analysis.
              </div>
            </div>
          </div>
          <MarketSnapshot />
        </div>
      )}
    </aside>
  );
}
