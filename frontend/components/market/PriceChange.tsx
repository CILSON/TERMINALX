/* ═══════════════════════════════════════════════════════
 * TerminalX — Price Change Display
 * ═══════════════════════════════════════════════════════ */

interface PriceChangeProps {
  change: number;
  changePct: number;
  showArrow?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function PriceChange({ change, changePct, showArrow = true, size = 'md' }: PriceChangeProps) {
  const isPositive = change >= 0;
  const colorClass = change === 0 ? 'price-unchanged' : isPositive ? 'price-positive' : 'price-negative';
  const arrow = isPositive ? '▲' : '▼';
  const sign = isPositive ? '+' : '';

  const fontSize = size === 'sm' ? '11px' : size === 'lg' ? '16px' : '12px';

  return (
    <span className={`asset-card-change ${colorClass}`} style={{ fontSize }}>
      {showArrow && <span style={{ fontSize: '8px' }}>{arrow}</span>}
      <span>{sign}{change.toFixed(2)}</span>
      <span>({sign}{changePct.toFixed(2)}%)</span>
    </span>
  );
}
