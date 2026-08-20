/* ═══════════════════════════════════════════════════════
 * TerminalX — Loading Pulse (Skeleton)
 * ═══════════════════════════════════════════════════════ */

interface LoadingPulseProps {
  count?: number;
}

export function LoadingPulse({ count = 4 }: LoadingPulseProps) {
  return (
    <div className="loading-pulse">
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className="loading-pulse-line" />
      ))}
    </div>
  );
}
