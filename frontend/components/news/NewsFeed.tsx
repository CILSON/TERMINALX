/* ═══════════════════════════════════════════════════════
 * TerminalX — News Feed (Scrollable List)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useRef, useCallback } from 'react';
import { useNewsStore } from '@/stores/newsStore';
import { useNews } from '@/hooks/useNews';
import { NewsCard } from './NewsCard';
import { LoadingPulse } from '@/components/common/LoadingPulse';

export function NewsFeed() {
  const articles = useNewsStore((s) => s.articles);
  const loading = useNewsStore((s) => s.loading);
  const selectedArticle = useNewsStore((s) => s.selectedArticle);
  const { loadMore, hasMore, openArticle } = useNews();
  const scrollRef = useRef<HTMLDivElement>(null);

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el || loading || !hasMore) return;

    const { scrollTop, scrollHeight, clientHeight } = el;
    if (scrollHeight - scrollTop - clientHeight < 200) {
      loadMore();
    }
  }, [loading, hasMore, loadMore]);

  if (loading && articles.length === 0) {
    return (
      <div className="scrollable">
        <LoadingPulse count={8} />
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="scrollable">
        <div className="empty-state">
          <div className="empty-state-icon">📡</div>
          <div className="empty-state-title">No News Available</div>
          <div className="empty-state-text">
            Waiting for market news feed...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="scrollable" ref={scrollRef} onScroll={handleScroll}>
      {articles.map((article, index) => (
        <NewsCard
          key={`${article.id}-${index}`}
          article={article}
          isActive={selectedArticle?.id === article.id}
          onClick={() => openArticle(article)}
          style={{ animationDelay: `${Math.min(index * 30, 300)}ms` }}
        />
      ))}
      {loading && <LoadingPulse count={2} />}
    </div>
  );
}
