/* ═══════════════════════════════════════════════════════
 * TerminalX — Asset Detail (Bloomberg-style centerpiece)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect, useState, useMemo } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { useCommandStore } from '@/stores/commandStore';
import { useNewsStore } from '@/stores/newsStore';
import { Badge } from '@/components/common/Badge';
import { LoadingPulse } from '@/components/common/LoadingPulse';
import { fetchAssetIntelligence } from '@/lib/api';
import type { AssetIntelligence, NewsItem } from '@/types';

const CHART_PERIODS = ['1D', '5D', '1M', '6M', 'YTD', '1Y', '5Y', 'Max'] as const;
const DETAIL_TABS = ['OVERVIEW', 'NEWS', 'EARNINGS', 'TECHNICALS', 'PEERS', 'HOLDINGS', 'FII/DII FLOW'] as const;

function formatPrice(value: number | undefined | null): string {
  if (value == null) return '—';
  return value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatVolume(value: number | undefined | null): string {
  if (value == null) return '—';
  if (value >= 1_00_00_000) return `${(value / 1_00_00_000).toFixed(2)} Cr`;
  if (value >= 1_00_000) return `${(value / 1_00_000).toFixed(2)} L`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString('en-IN');
}

function timeAgo(dateStr: string | undefined): string {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function AssetDetail() {
  const assetSymbol = useCommandStore((s) => s.assetSymbol);
  const setActiveView = useCommandStore((s) => s.setActiveView);
  const selectArticle = useNewsStore((s) => s.selectArticle);
  const quotes = useMarketStore((s) => s.quotes);

  const [intel, setIntel] = useState<AssetIntelligence | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activePeriod, setActivePeriod] = useState<string>('1D');
  const [activeTab, setActiveTab] = useState<string>('OVERVIEW');
  const [starred, setStarred] = useState(false);

  useEffect(() => {
    if (!assetSymbol) return;
    setLoading(true);
    setError(null);
    fetchAssetIntelligence(assetSymbol)
      .then((data) => setIntel(data))
      .catch(() => {
        setIntel(null);
        setError('Failed to load asset data');
      })
      .finally(() => setLoading(false));
  }, [assetSymbol]);

  const quote = useMemo(
    () => (assetSymbol ? quotes[assetSymbol] ?? intel?.quote : null),
    [assetSymbol, quotes, intel],
  );

  if (!assetSymbol) return null;

  if (loading) {
    return (
      <div className="asset-detail">
        <LoadingPulse count={8} />
      </div>
    );
  }

  if (error && !quote) {
    return (
      <div className="asset-detail">
        <button className="article-reader-back" onClick={() => setActiveView('market')}>
          ← Back to Market
        </button>
        <div className="empty-state">
          <div className="empty-state-icon">⚠️</div>
          <div className="empty-state-title">{error}</div>
          <div className="empty-state-text">Could not load data for {assetSymbol}</div>
        </div>
      </div>
    );
  }

  const isPositive = (quote?.change ?? 0) >= 0;
  const changeSign = isPositive ? '+' : '';
  const arrow = isPositive ? '▲' : '▼';
  const now = new Date();
  const hour = now.getHours();
  const isMarketOpen = hour >= 9 && hour < 16;

  const sentimentLabel = intel?.sentiment
    ? intel.sentiment.charAt(0).toUpperCase() + intel.sentiment.slice(1)
    : 'Neutral';
  const sentimentVariant = intel?.sentiment === 'bullish' ? 'bullish' : intel?.sentiment === 'bearish' ? 'bearish' : 'neutral';
  const confidence = intel?.sentiment_breakdown?.confidence ?? (intel?.sentiment === 'bullish' ? 72 : intel?.sentiment === 'bearish' ? 65 : 50);

  return (
    <div className="asset-detail">
      {/* Back navigation */}
      <button className="article-reader-back" onClick={() => setActiveView('market')}>
        ← Back to Market
      </button>

      {/* ── HEADER ROW ── */}
      <div className="asset-detail-header">
        <div className="asset-detail-title-area">
          <h1 className="asset-detail-title">
            {quote?.name || assetSymbol}{' '}
            <span className="asset-detail-symbol">{assetSymbol}</span>{' '}
            <span
              className={`asset-detail-star ${starred ? 'active' : ''}`}
              onClick={() => setStarred(!starred)}
            >
              {starred ? '★' : '☆'}
            </span>
          </h1>
          <div className="asset-detail-price">
            {formatPrice(quote?.price)}
          </div>
          <div className={`asset-detail-change ${isPositive ? 'positive' : 'negative'}`}>
            {changeSign}{quote?.change?.toFixed(2) ?? '0.00'}{'  '}
            {changeSign}{quote?.change_pct?.toFixed(2) ?? '0.00'}%{arrow}
          </div>
          <div className="asset-detail-timestamp">
            As of {now.toLocaleTimeString('en-IN', { hour12: false })} IST • {now.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
            {' • '}
            <span className={`market-open-badge ${isMarketOpen ? '' : 'closed'}`}>
              ● {isMarketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}
            </span>
          </div>
        </div>

        <div className="asset-detail-stats-grid">
          <div className="asset-detail-stat">
            <span className="asset-detail-stat-label">High</span>
            <span className="asset-detail-stat-value">{formatPrice(quote?.high)}</span>
          </div>
          <div className="asset-detail-stat">
            <span className="asset-detail-stat-label">52W High</span>
            <span className="asset-detail-stat-value">{formatPrice(quote?.day_high)}</span>
          </div>
          <div className="asset-detail-stat">
            <span className="asset-detail-stat-label">Low</span>
            <span className="asset-detail-stat-value">{formatPrice(quote?.low)}</span>
          </div>
          <div className="asset-detail-stat">
            <span className="asset-detail-stat-label">52W Low</span>
            <span className="asset-detail-stat-value">{formatPrice(quote?.day_low)}</span>
          </div>
          <div className="asset-detail-stat">
            <span className="asset-detail-stat-label">Open</span>
            <span className="asset-detail-stat-value">{formatPrice(quote?.open)}</span>
          </div>
          <div className="asset-detail-stat">
            <span className="asset-detail-stat-label">Prev Close</span>
            <span className="asset-detail-stat-value">{formatPrice(quote?.prev_close)}</span>
          </div>
        </div>
      </div>

      {/* ── CHART AREA ── */}
      <div className="asset-detail-chart-toolbar">
        {CHART_PERIODS.map((period) => (
          <button
            key={period}
            className={`asset-detail-period-btn ${activePeriod === period ? 'active' : ''}`}
            onClick={() => setActivePeriod(period)}
          >
            {period}
          </button>
        ))}
      </div>
      <div className="asset-detail-chart">
        <div className="asset-detail-chart-gradient" />
        <div className="asset-detail-chart-label">
          {assetSymbol} • {activePeriod} • Chart coming in Phase 2
        </div>
      </div>

      {/* ── STATS ROW ── */}
      <div className="asset-detail-metrics">
        <div className="asset-detail-metric-item">
          <span className="asset-detail-metric-label">Volume</span>
          <span className="asset-detail-metric-value">{formatVolume(quote?.volume)}</span>
        </div>
        <div className="asset-detail-metric-item">
          <span className="asset-detail-metric-label">Market Cap</span>
          <span className="asset-detail-metric-value">—</span>
        </div>
        <div className="asset-detail-metric-item">
          <span className="asset-detail-metric-label">PE Ratio</span>
          <span className="asset-detail-metric-value">—</span>
        </div>
        <div className="asset-detail-metric-item">
          <span className="asset-detail-metric-label">Div Yield</span>
          <span className="asset-detail-metric-value">—</span>
        </div>
      </div>

      {/* ── NAVIGATION TABS ── */}
      <div className="asset-detail-tabs">
        {DETAIL_TABS.map((tab) => (
          <button
            key={tab}
            className={`asset-detail-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* ── CONTENT: AI Summary + Related News ── */}
      {activeTab === 'OVERVIEW' && (
        <div className="asset-detail-content">
          <div className="asset-detail-ai-summary">
            <h3 className="asset-detail-section-title">
              <span className="asset-detail-ai-icon">◆</span> AI SUMMARY
              <span className="asset-detail-generated-time">
                Generated {timeAgo(intel?.quote?.updated_at)}
              </span>
            </h3>
            <p className="asset-detail-ai-text">
              {intel?.ai_summary || `${quote?.name || assetSymbol} is currently trading at ${formatPrice(quote?.price)} with a ${isPositive ? 'positive' : 'negative'} change of ${changeSign}${quote?.change_pct?.toFixed(2) ?? 0}%. Market participants are closely watching key levels for directional cues.`}
            </p>
            {intel?.ai_outlook && (
              <p className="asset-detail-ai-text asset-detail-ai-outlook">
                <strong>Outlook:</strong> {intel.ai_outlook}
              </p>
            )}
            <div className="asset-detail-ai-metrics">
              <div className="asset-detail-ai-metric-item">
                <span className="asset-detail-ai-metric-label">Sentiment</span>
                <Badge text={sentimentLabel} variant={sentimentVariant} />
              </div>
              <div className="asset-detail-ai-metric-item">
                <span className="asset-detail-ai-metric-label">Confidence</span>
                <span className="asset-detail-ai-metric-value">{confidence}%</span>
              </div>
              <div className="asset-detail-ai-metric-item">
                <span className="asset-detail-ai-metric-label">Impact</span>
                <Badge text="HIGH" variant="orange" />
              </div>
            </div>
            {intel?.ai_key_levels && (
              <div className="asset-detail-key-levels">
                {intel.ai_key_levels.support != null && (
                  <div className="asset-detail-level">
                    <span className="asset-detail-level-label">Support</span>
                    <span className="asset-detail-level-value text-green">{formatPrice(intel.ai_key_levels.support)}</span>
                  </div>
                )}
                {intel.ai_key_levels.resistance != null && (
                  <div className="asset-detail-level">
                    <span className="asset-detail-level-label">Resistance</span>
                    <span className="asset-detail-level-value text-red">{formatPrice(intel.ai_key_levels.resistance)}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="asset-detail-related-news">
            <h3 className="asset-detail-section-title">RELATED NEWS</h3>
            {intel?.related_news && intel.related_news.length > 0 ? (
              intel.related_news.slice(0, 4).map((article: NewsItem, i: number) => (
                <div
                  key={article.id || i}
                  className="asset-detail-news-item"
                  onClick={() => {
                    selectArticle(article);
                    setActiveView('news');
                  }}
                >
                  <div className="asset-detail-news-headline">{article.headline}</div>
                  <div className="asset-detail-news-meta">
                    <span className="asset-detail-news-publisher">{article.publisher}</span>
                    <span className="asset-detail-news-time">{timeAgo(article.published_at)}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="asset-detail-no-news">No related news available</div>
            )}
          </div>
        </div>
      )}

      {/* Placeholder content for other tabs */}
      {activeTab !== 'OVERVIEW' && (
        <div className="asset-detail-content">
          <div className="empty-state">
            <div className="empty-state-icon">📊</div>
            <div className="empty-state-title">{activeTab}</div>
            <div className="empty-state-text">
              {activeTab} data for {assetSymbol} — coming soon
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
