/* ═══════════════════════════════════════════════════════
 * TerminalX — Quote Ticker (Horizontal Scroll)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useMarketStore } from '@/stores/marketStore';
import { useCommandStore } from '@/stores/commandStore';

export function QuoteTicker() {
  const quotes = useMarketStore((s) => s.quotes);
  const setActiveView = useCommandStore((s) => s.setActiveView);
  const quoteList = Object.values(quotes).filter(
    (q) => q && typeof q.price === 'number' && typeof q.symbol === 'string'
  );

  if (quoteList.length === 0) return null;

  const formatPrice = (price: number) => {
    if (price >= 10000) return price.toLocaleString('en-IN', { maximumFractionDigits: 2 });
    if (price >= 100) return price.toFixed(2);
    return price.toFixed(4);
  };

  // Duplicate for seamless infinite scroll
  const items = [...quoteList, ...quoteList];

  return (
    <div className="topbar-ticker">
      <div className="quote-ticker">
        {items.map((q, i) => {
          const isPositive = q.change_pct >= 0;
          return (
            <div
              key={`${q.symbol}-${i}`}
              className="quote-ticker-item"
              onClick={() => setActiveView('asset', q.symbol)}
            >
              <span className="quote-ticker-symbol">{q.symbol}</span>
              <span className="quote-ticker-price">{formatPrice(q.price)}</span>
              <span
                className={`quote-ticker-change ${isPositive ? 'price-positive' : 'price-negative'}`}
              >
                {isPositive ? '▲' : '▼'} {isPositive ? '+' : ''}{q.change_pct.toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
