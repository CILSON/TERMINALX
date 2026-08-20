/* ═══════════════════════════════════════════════════════
 * TerminalX — AI Panel
 * ═══════════════════════════════════════════════════════ */
'use client';

import type { AIAnalysis } from '@/types';
import { Badge } from '@/components/common/Badge';
import { ConfidenceBar } from './ConfidenceBar';

interface AIPanelProps {
  analysis: AIAnalysis;
}

export function AIPanel({ analysis }: AIPanelProps) {
  return (
    <div className="ai-panel">
      {/* Header */}
      <div className="panel-header">
        <span className="panel-header-title">AI Intelligence</span>
      </div>

      <div className="scrollable">
        {/* What Happened */}
        <div className="ai-panel-section">
          <div className="ai-panel-label">What Happened</div>
          <div className="ai-panel-text">{analysis.what_happened}</div>
        </div>

        {/* Why It Matters */}
        <div className="ai-panel-section">
          <div className="ai-panel-label">Why It Matters</div>
          <div className="ai-panel-text">{analysis.why_it_matters}</div>
        </div>

        {/* Affected Assets */}
        {analysis.affected_assets.length > 0 && (
          <div className="ai-panel-section">
            <div className="ai-panel-label">Affected Assets</div>
            <div className="ai-panel-badges">
              {analysis.affected_assets.map((asset) => (
                <Badge key={asset} text={asset} variant="info" />
              ))}
            </div>
          </div>
        )}

        {/* Bullish For */}
        {analysis.bullish_for.length > 0 && (
          <div className="ai-panel-section">
            <div className="ai-panel-label">Bullish For</div>
            <div className="ai-panel-badges">
              {analysis.bullish_for.map((asset) => (
                <Badge key={asset} text={`▲ ${asset}`} variant="bullish" />
              ))}
            </div>
          </div>
        )}

        {/* Bearish For */}
        {analysis.bearish_for.length > 0 && (
          <div className="ai-panel-section">
            <div className="ai-panel-label">Bearish For</div>
            <div className="ai-panel-badges">
              {analysis.bearish_for.map((asset) => (
                <Badge key={asset} text={`▼ ${asset}`} variant="bearish" />
              ))}
            </div>
          </div>
        )}

        {/* Confidence */}
        <div className="ai-panel-section">
          <div className="ai-panel-label">Confidence</div>
          <ConfidenceBar value={analysis.confidence} />
        </div>
      </div>
    </div>
  );
}
