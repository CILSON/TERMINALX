/* ═══════════════════════════════════════════════════════
 * TerminalX — News Card
 * ═══════════════════════════════════════════════════════ */
'use client';

import type { CSSProperties } from 'react';
import type { NewsItem } from '@/types';

interface NewsCardProps {
  article: NewsItem;
  isActive: boolean;
  onClick: () => void;
  style?: CSSProperties;
}

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;

  if (isNaN(diffMs)) return '';

  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return 'now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function getImportanceClass(importance: number): string {
  if (importance >= 8) return 'news-card--high';
  if (importance >= 5) return 'news-card--medium';
  return 'news-card--low';
}

export function NewsCard({ article, isActive, onClick, style }: NewsCardProps) {
  const importanceClass = getImportanceClass(article.importance);
  const activeClass = isActive ? 'news-card--active' : '';

  return (
    <div
      className={`news-card ${importanceClass} ${activeClass}`}
      onClick={onClick}
      style={style}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <div className="news-card-headline">{article.headline}</div>
      <div className="news-card-meta">
        <span className="news-card-source">{article.source}</span>
        <span>•</span>
        <span>{timeAgo(article.published_at)}</span>
        <span
          className={`news-card-dot ${article.sentiment}`}
          title={article.sentiment}
        />
      </div>
    </div>
  );
}
