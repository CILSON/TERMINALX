/* ═══════════════════════════════════════════════════════
 * TerminalX — Related Assets
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useMarketStore } from '@/stores/marketStore';
import { useCommandStore } from '@/stores/commandStore';
import { PriceChange } from '@/components/market/PriceChange';

interface RelatedAssetsProps {
  symbols: string[] | string;
}

export function RelatedAssets({ symbols: rawSymbols }: RelatedAssetsProps) {
  const symbols = Array.isArray(rawSymbols)
    ? rawSymbols
    : typeof rawSymbols === 'string'
      ? rawSymbols.split(/[\s,]+/).filter(Boolean)
      : [];
  const quotes = useMarketStore((s) => s.quotes);
  const setActiveView = useCommandStore((s) => s.setActiveView);
  const selectArticle = useCommandStore(() => {
    // We clear the article selection from the newsStore
    return null;
  });

  const handleClick = (symbol: string) => {
    setActiveView('asset', symbol);
  };

  return (
    <div className="related-assets">
      {symbols.map((symbol) => {
        const quote = quotes[symbol.toUpperCase()];
        return (
          <div
            key={symbol}
            className="related-asset"
            onClick={() => handleClick(symbol.toUpperCase())}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleClick(symbol.toUpperCase());
            }}
          >
            <span className="related-asset-symbol">{symbol}</span>
            {quote && (
              <>
                <span className="related-asset-price">
                  {quote.price.toLocaleString('en-IN', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </span>
                <PriceChange change={quote.change} changePct={quote.change_pct} size="sm" showArrow={false} />
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}
