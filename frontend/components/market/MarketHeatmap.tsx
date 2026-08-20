/* ═══════════════════════════════════════════════════════
 * TerminalX — Market Heatmap (Visual Performance Grid)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useMarketStore } from '@/stores/marketStore';
import { useCommandStore } from '@/stores/commandStore';
import { ASSET_GROUPS } from '@/lib/constants';

export function MarketHeatmap() {
  const quotes = useMarketStore((s) => s.quotes);
  const setActiveView = useCommandStore((s) => s.setActiveView);

  const allSymbols = Object.values(ASSET_GROUPS).flat();

  const getColor = (changePct: number) => {
    if (changePct >= 3) return '#15803d';
    if (changePct >= 1.5) return '#16a34a';
    if (changePct >= 0.5) return '#22c55e';
    if (changePct >= 0.1) return '#14532d';
    if (changePct >= -0.1) return '#1e293b';
    if (changePct >= -0.5) return '#7f1d1d';
    if (changePct >= -1.5) return '#dc2626';
    if (changePct >= -3) return '#ef4444';
    return '#b91c1c';
  };

  const getTextColor = (changePct: number) => {
    return Math.abs(changePct) > 0.1 ? '#f1f5f9' : '#94a3b8';
  };

  const formatPrice = (price: number) => {
    if (price >= 10000) return price.toLocaleString('en-IN', { maximumFractionDigits: 0 });
    if (price >= 100) return price.toFixed(1);
    if (price >= 1) return price.toFixed(2);
    return price.toFixed(4);
  };

  return (
    <div className="market-heatmap">
      <div className="panel-header">
        <span className="panel-header-title">Market Heatmap</span>
        <span className="panel-header-count">LIVE</span>
      </div>

      <div className="heatmap-grid">
        {allSymbols.map((asset) => {
          const q = quotes[asset.symbol];
          const changePct = q?.change_pct ?? 0;

          return (
            <div
              key={asset.symbol}
              className="heatmap-cell"
              style={{
                backgroundColor: getColor(changePct),
                color: getTextColor(changePct),
              }}
              onClick={() => setActiveView('asset', asset.symbol)}
              title={`${asset.symbol}: ${changePct >= 0 ? '+' : ''}${changePct.toFixed(2)}%`}
            >
              <div className="heatmap-symbol">{asset.symbol}</div>
              <div className="heatmap-price">
                {q ? formatPrice(q.price) : '—'}
              </div>
              <div className="heatmap-change">
                {changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
