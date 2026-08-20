/* ═══════════════════════════════════════════════════════
 * TerminalX — Asset Card (Market Tile)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect, useState, useRef } from 'react';
import { PriceChange } from './PriceChange';
import { Sparkline } from '@/components/common/Sparkline';
import { useCommandStore } from '@/stores/commandStore';
import type { Quote } from '@/types';

interface AssetCardProps {
  symbol: string;
  name: string;
  quote: Quote | null;
  previousPrice?: number;
}

export function AssetCard({ symbol, name, quote, previousPrice }: AssetCardProps) {
  const [flashClass, setFlashClass] = useState('');
  const [priceHistory, setPriceHistory] = useState<number[]>([]);
  const setActiveView = useCommandStore((s) => s.setActiveView);
  const prevPriceRef = useRef<number | undefined>(previousPrice);

  // Flash animation on price change
  useEffect(() => {
    if (quote && prevPriceRef.current !== undefined) {
      if (quote.price > prevPriceRef.current) {
        setFlashClass('flash-up');
      } else if (quote.price < prevPriceRef.current) {
        setFlashClass('flash-down');
      }
      const timer = setTimeout(() => setFlashClass(''), 800);
      return () => clearTimeout(timer);
    }
    prevPriceRef.current = quote?.price;
  }, [quote?.price]);

  // Track price history for sparkline
  useEffect(() => {
    if (quote) {
      setPriceHistory((prev) => {
        const next = [...prev, quote.price];
        return next.slice(-20); // Keep last 20 ticks
      });
    }
  }, [quote?.price]);

  const formatPrice = (price: number) => {
    if (price >= 10000) return price.toLocaleString('en-IN', { maximumFractionDigits: 2 });
    if (price >= 100) return price.toFixed(2);
    if (price >= 1) return price.toFixed(4);
    return price.toFixed(6);
  };

  return (
    <div
      className={`asset-card ${flashClass}`}
      onClick={() => setActiveView('asset', symbol)}
    >
      <div className="asset-card-symbol">{symbol}</div>
      <div className="asset-card-name">{quote?.name || name}</div>
      <div className="asset-card-price">
        {quote ? formatPrice(quote.price) : '—'}
      </div>
      {quote && (
        <PriceChange change={quote.change} changePct={quote.change_pct} />
      )}
      {priceHistory.length > 3 && (
        <Sparkline data={priceHistory} width={160} height={24} />
      )}
    </div>
  );
}
