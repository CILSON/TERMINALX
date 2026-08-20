/* ═══════════════════════════════════════════════════════
 * TerminalX — Asset Intelligence Page
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect, useState } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { useCommandStore } from '@/stores/commandStore';
import { useNewsStore } from '@/stores/newsStore';
import { PriceChange } from './PriceChange';
import { Badge } from '@/components/common/Badge';
import { LoadingPulse } from '@/components/common/LoadingPulse';
import { fetchAssetIntelligence } from '@/lib/api';
import type { AssetIntelligence as AssetIntelType } from '@/types';

export function AssetIntelligence() {
  const assetSymbol = useCommandStore((s) => s.assetSymbol);
  const setActiveView = useCommandStore((s) => s.setActiveView);
  const selectArticle = useNewsStore((s) => s.selectArticle);
  const quotes = useMarketStore((s) => s.quotes);
  const [intel, setIntel] = useState<AssetIntelType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!assetSymbol) return;
    setLoading(true);
    fetchAssetIntelligence(assetSymbol)
      .then((data) => setIntel(data))
      .catch(() => setIntel(null))
      .finally(() => setLoading(false));
  }, [assetSymbol]);

  if (!assetSymbol) return null;
  if (loading) {
    return (
      <div className="asset-intel">
        <LoadingPulse count={6} />
      </div>
    );
  }

  const quote = quotes[assetSymbol] || intel?.quote;

  return (
    <div className="asset-intel">
      {/* Back button */}
      <button className="article-reader-back" onClick={() => setActiveView('market')}>
        ← Back to Market
      </button>

      {/* Header */}
      <div className="asset-intel-header">
        <div>
          <div className="asset-intel-symbol">{assetSymbol}</div>
          <div className="asset-intel-name">{quote?.name || assetSymbol}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="asset-intel-price">
            {quote ? quote.price.toLocaleString('en-IN', { maximumFractionDigits: 2 }) : '—'}
          </div>
          {quote && <PriceChange change={quote.change} changePct={quote.change_pct} size="lg" />}
        </div>
      </div>

      {/* Chart placeholder */}
      <div className="asset-intel-chart">
        <div className="empty-state" style={{ height: '100%' }}>
          <div className="empty-state-icon">📈</div>
          <div className="empty-state-text">TradingView chart — Phase 2</div>
        </div>
      </div>

      {/* Metrics */}
      {quote && (
        <div className="asset-intel-metrics">
          <div className="asset-intel-metric">
            <div className="asset-intel-metric-label">Open</div>
            <div className="asset-intel-metric-value">{quote.open?.toFixed(2) || '—'}</div>
          </div>
          <div className="asset-intel-metric">
            <div className="asset-intel-metric-label">High</div>
            <div className="asset-intel-metric-value">{quote.high?.toFixed(2) || '—'}</div>
          </div>
          <div className="asset-intel-metric">
            <div className="asset-intel-metric-label">Low</div>
            <div className="asset-intel-metric-value">{quote.low?.toFixed(2) || '—'}</div>
          </div>
          <div className="asset-intel-metric">
            <div className="asset-intel-metric-label">Prev Close</div>
            <div className="asset-intel-metric-value">{quote.prev_close?.toFixed(2) || '—'}</div>
          </div>
        </div>
      )}

      {/* AI Summary */}
      {intel?.ai_summary && (
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <div className="section-header">AI Summary</div>
          <div style={{ padding: 'var(--space-lg)', fontSize: '13px', lineHeight: 1.7 }}>
            {intel.ai_summary}
          </div>
          {intel.sentiment && (
            <div style={{ padding: '0 var(--space-lg)', marginBottom: 'var(--space-md)' }}>
              <Badge
                text={intel.sentiment.toUpperCase()}
                variant={intel.sentiment === 'bullish' ? 'bullish' : intel.sentiment === 'bearish' ? 'bearish' : 'neutral'}
              />
            </div>
          )}
        </div>
      )}

      {/* Related News */}
      {intel?.related_news && intel.related_news.length > 0 && (
        <div>
          <div className="section-header">Related News</div>
          {intel.related_news.map((article: any, i: number) => (
            <div
              key={i}
              className="news-card"
              onClick={() => {
                selectArticle(article);
                setActiveView('news');
              }}
            >
              <div className="news-card-headline">{article.headline}</div>
              <div className="news-card-meta">
                <span className="news-card-source">{article.publisher}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
