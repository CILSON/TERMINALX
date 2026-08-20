/* ═══════════════════════════════════════════════════════
 * TerminalX — Market Sidebar (Right Panel Default)
 * Shows compact price list when no article is selected
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useMarketStore } from '@/stores/marketStore';
import { useCommandStore } from '@/stores/commandStore';
import { ASSET_GROUPS } from '@/lib/constants';

const SECTIONS = [
  { key: 'indices', label: 'INDICES', icon: '📊' },
  { key: 'commodities', label: 'COMMODITIES', icon: '🏗️' },
  { key: 'forex', label: 'FOREX', icon: '💱' },
  { key: 'crypto', label: 'CRYPTO', icon: '₿' },
] as const;

export function MarketSidebar() {
  const quotes = useMarketStore((s) => s.quotes);
  const setActiveView = useCommandStore((s) => s.setActiveView);

  const formatPrice = (price: number) => {
    if (price >= 10000) return price.toLocaleString('en-IN', { maximumFractionDigits: 2 });
    if (price >= 100) return price.toFixed(2);
    if (price >= 1) return price.toFixed(4);
    return price.toFixed(6);
  };

  return (
    <div className="market-sidebar">
      <div className="panel-header">
        <span className="panel-header-title">Markets</span>
        <span className="panel-header-count">LIVE</span>
      </div>
      <div className="scrollable">
        {SECTIONS.map((section) => {
          const assets = ASSET_GROUPS[section.key];
          return (
            <div key={section.key}>
              <div className="section-header">
                {section.label}
              </div>
              {assets.map((asset) => {
                const q = quotes[asset.symbol];
                const isPositive = q ? q.change_pct >= 0 : true;
                return (
                  <div
                    key={asset.symbol}
                    className="market-sidebar-item"
                    onClick={() => setActiveView('asset', asset.symbol)}
                  >
                    <div>
                      <div className="market-sidebar-symbol">{asset.symbol}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="market-sidebar-price" style={{ color: 'var(--text-primary)' }}>
                        {q ? formatPrice(q.price) : '—'}
                      </div>
                      {q && (
                        <div
                          className={`market-sidebar-change ${isPositive ? 'price-positive' : 'price-negative'}`}
                        >
                          {isPositive ? '▲' : '▼'} {isPositive ? '+' : ''}{q.change_pct.toFixed(2)}%
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
