/* ═══════════════════════════════════════════════════════
 * TerminalX — Badge Component
 * ═══════════════════════════════════════════════════════ */

type BadgeVariant = 'bullish' | 'bearish' | 'neutral' | 'info' | 'warning' | 'orange' | 'high' | 'medium' | 'low';

interface BadgeProps {
  text: string;
  variant?: BadgeVariant;
  onClick?: () => void;
}

export function Badge({ text, variant = 'neutral', onClick }: BadgeProps) {
  return (
    <span
      className={`badge badge-${variant}`}
      onClick={onClick}
      style={onClick ? { cursor: 'pointer' } : undefined}
    >
      {text}
    </span>
  );
}
