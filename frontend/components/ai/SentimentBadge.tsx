/* ═══════════════════════════════════════════════════════
 * TerminalX — Sentiment Badge
 * ═══════════════════════════════════════════════════════ */
'use client';

import type { Sentiment } from '@/types';

interface SentimentBadgeProps {
  sentiment: Sentiment;
}

const LABEL: Record<Sentiment, string> = {
  bullish: 'BULLISH',
  bearish: 'BEARISH',
  neutral: 'NEUTRAL',
};

export function SentimentBadge({ sentiment }: SentimentBadgeProps) {
  return (
    <span className={`badge badge-${sentiment}`}>
      {LABEL[sentiment]}
    </span>
  );
}
