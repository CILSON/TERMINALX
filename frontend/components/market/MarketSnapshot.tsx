/* ═══════════════════════════════════════════════════════
 * TerminalX — Market Snapshot (Right Panel Table)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useState } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { useCommandStore } from '@/stores/commandStore';
import { ASSET_GROUPS } from '@/lib/constants';

type TabKey = 'INDICES' | 'FUTURES' | 'GLOBAL' | 'COMMODITIES';

const TAB_SYMBOLS: Record<TabKey, readonly { readonly symbol: string; readonly name: string }[]> = {
  INDICES: ASSET_GROUPS.indices,
  FUTURES: ASSET_GROUPS.indices.slice(0, 3),
  GLOBAL: ASSET_GROUPS.forex,
  COMMODITIES: ASSET_GROUPS.commodities,
};

function formatPrice(price: number): string {
  if (price >= 10000) return price.toLocaleString('en-IN', { maximumFractionDigits: 2 });
  if (price >= 100) return price.toFixed(2);
  return price.toFixed(2);
}

export function MarketSnapshot() {
  const [activeTab, setActiveTab] = useState<TabKey>('INDICES');
  const quotes = useMarketStore((s) => s.quotes);
  const setActiveView = useCommandStore((s) => s.setActiveView);

  const symbols = TAB_SYMBOLS[activeTab];

  return (
    <div className="market-snapshot">
      <div className="panel-header">
        <span className="panel-header-title">Market Snapshot</span>
      </div>

      <div className="market-snapshot-tabs">
        {(Object.keys(TAB_SYMBOLS) as TabKey[]).map((tab) => (
          <button
            key={tab}
            className={`snapshot-tab ${activeTab === tab ? 'snapshot-tab-active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <table className="snapshot-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Last</th>
            <th>Chg</th>
            <th>% Chg</th>
          </tr>
        </thead>
        <tbody>
          {symbols.map((asset) => {
            const q = quotes[asset.symbol];
            const isPositive = (q?.change_pct ?? 0) >= 0;
            const color = isPositive ? 'var(--accent-green)' : 'var(--accent-red)';
            return (
              <tr
                key={asset.symbol}
                onClick={() => setActiveView('asset', asset.symbol)}
                style={{ cursor: 'pointer' }}
              >
                <td>{asset.name || asset.symbol}</td>
                <td>{q ? formatPrice(q.price) : '—'}</td>
                <td style={{ color }}>
                  {q ? `${isPositive ? '+' : ''}${q.change?.toFixed(2)}` : '—'}
                </td>
                <td style={{ color }}>
                  {q ? `${isPositive ? '+' : ''}${q.change_pct?.toFixed(2)}%` : '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
