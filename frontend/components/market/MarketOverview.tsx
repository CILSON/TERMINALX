/* ═══════════════════════════════════════════════════════
 * TerminalX — Market Overview
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useMarketStore } from '@/stores/marketStore';
import { ASSET_GROUPS } from '@/lib/constants';
import { AssetCard } from './AssetCard';
import { LoadingPulse } from '@/components/common/LoadingPulse';

const SECTIONS = [
  { key: 'indices', label: 'INDICES' },
  { key: 'commodities', label: 'COMMODITIES' },
  { key: 'forex', label: 'FOREX' },
  { key: 'crypto', label: 'CRYPTO' },
] as const;

export function MarketOverview() {
  const quotes = useMarketStore((s) => s.quotes);
  const previousPrices = useMarketStore((s) => s.previousPrices);
  const hasQuotes = Object.keys(quotes).length > 0;

  if (!hasQuotes) {
    return (
      <div className="market-overview">
        <div className="section-header">Market Overview</div>
        <LoadingPulse count={8} />
        <div className="empty-state" style={{ marginTop: '32px' }}>
          <div className="empty-state-icon">📊</div>
          <div className="empty-state-title">Loading Market Data...</div>
          <div className="empty-state-text">
            Connecting to data feed. Quotes will appear shortly.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="market-overview">
      {SECTIONS.map((section) => {
        const assets = ASSET_GROUPS[section.key];
        return (
          <div key={section.key} className="market-section">
            <div className="market-section-header">
              <span className="market-section-title">{section.label}</span>
            </div>
            <div className="market-grid">
              {assets.map((asset) => {
                const quote = quotes[asset.symbol];
                const prevPrice = previousPrices[asset.symbol];
                return (
                  <AssetCard
                    key={asset.symbol}
                    symbol={asset.symbol}
                    name={asset.name}
                    quote={quote || null}
                    previousPrice={prevPrice}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
