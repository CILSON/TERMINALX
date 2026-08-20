/* ═══════════════════════════════════════════════════════
 * TerminalX — Article Header
 * ═══════════════════════════════════════════════════════ */
'use client';

import type { NewsItem } from '@/types';
import { SentimentBadge } from '@/components/ai/SentimentBadge';
import { Badge } from '@/components/common/Badge';

interface ArticleHeaderProps {
  article: NewsItem;
}

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Kolkata',
    });
  } catch {
    return dateStr;
  }
}

function getImportanceLabel(importance: number): { text: string; variant: 'bearish' | 'warning' | 'neutral' } {
  if (importance >= 8) return { text: 'HIGH', variant: 'bearish' };
  if (importance >= 5) return { text: 'MEDIUM', variant: 'warning' };
  return { text: 'LOW', variant: 'neutral' };
}

export function ArticleHeader({ article }: ArticleHeaderProps) {
  const imp = getImportanceLabel(article.importance);

  return (
    <div>
      <h1 className="article-reader-headline">{article.headline}</h1>
      <div className="article-reader-meta">
        <Badge text={article.source} variant="orange" />
        {article.publisher && <span>{article.publisher}</span>}
        <span>•</span>
        <span>{formatDate(article.published_at)}</span>
        <span>•</span>
        <Badge text={imp.text} variant={imp.variant} />
        <SentimentBadge sentiment={article.sentiment} />
      </div>
    </div>
  );
}
