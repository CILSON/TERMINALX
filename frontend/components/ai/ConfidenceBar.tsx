/* ═══════════════════════════════════════════════════════
 * TerminalX — Confidence Bar
 * ═══════════════════════════════════════════════════════ */
'use client';

interface ConfidenceBarProps {
  value: number; // 0–100 or 0–1
}

export function ConfidenceBar({ value }: ConfidenceBarProps) {
  // Normalize: if value is 0–1, convert to percentage
  const pct = value <= 1 ? Math.round(value * 100) : Math.round(value);
  const clamped = Math.max(0, Math.min(100, pct));

  const level = clamped < 30 ? 'low' : clamped < 60 ? 'medium' : 'high';
  const colorClass = `confidence-bar-fill ${level}`;
  const textColor =
    level === 'high'
      ? 'var(--accent-green)'
      : level === 'medium'
      ? 'var(--accent-yellow)'
      : 'var(--accent-red)';

  return (
    <div className="confidence-bar">
      <div className="confidence-bar-track">
        <div className={colorClass} style={{ width: `${clamped}%` }} />
      </div>
      <span className="confidence-bar-value" style={{ color: textColor }}>
        {clamped}%
      </span>
    </div>
  );
}
