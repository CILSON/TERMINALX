/* ═══════════════════════════════════════════════════════
 * TerminalX — Article Reader (Full Article View)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect, useRef } from 'react';
import type { NewsItem } from '@/types';
import { useNewsStore } from '@/stores/newsStore';
import { ArticleHeader } from './ArticleHeader';
import { RelatedAssets } from './RelatedAssets';

interface ArticleReaderProps {
  article: NewsItem;
}

/**
 * Checks if body/summary is just a repeat of the headline.
 * RSS feeds often duplicate the headline as the summary.
 */
function getUniqueBody(article: NewsItem): string | null {
  const headline = (article.headline || '').trim().toLowerCase();
  const body = (article.body || '').trim();
  const summary = (article.summary || '').trim();

  // Use body if it's meaningfully different from headline
  if (body && body.toLowerCase() !== headline && body.length > headline.length + 20) {
    return body;
  }
  // Fallback to summary if it's different from headline
  if (summary && summary.toLowerCase() !== headline && summary.length > headline.length + 20) {
    return summary;
  }
  return null;
}

export function ArticleReader({ article }: ArticleReaderProps) {
  const selectArticle = useNewsStore((s) => s.selectArticle);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Scroll to top when article changes
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [article.id]);

  const bodyText = getUniqueBody(article);

  return (
    <div className="scrollable" ref={scrollRef}>
      <div className="article-reader">
        {/* Back button */}
        <button
          className="article-reader-back"
          onClick={() => selectArticle(null)}
        >
          ← Back to News
        </button>

        {/* Header */}
        <ArticleHeader article={article} />

        {/* Divider */}
        <div className="divider" style={{ margin: '16px 0 24px' }} />

        {/* Body — only show if it's different from the headline */}
        {bodyText ? (
          <div className="article-reader-body">
            {bodyText.split('\n').map((paragraph, i) => (
              <p key={i} style={{ marginBottom: '12px' }}>{paragraph}</p>
            ))}
          </div>
        ) : (
          <div className="article-reader-body" style={{ color: 'var(--text-secondary)' }}>
            <p style={{ marginBottom: '12px' }}>
              Full article available at source. See AI Intelligence panel on the right for analysis.
            </p>
            {article.source_url && (
              <a
                href={article.source_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: 'var(--accent-orange)',
                  textDecoration: 'none',
                  fontSize: '13px',
                  borderBottom: '1px dashed var(--accent-orange)',
                }}
              >
                Read full article on {article.publisher || article.source} →
              </a>
            )}
          </div>
        )}

        {/* Related Assets */}
        {article.entities && article.entities.length > 0 && (
          <div className="article-reader-section">
            <div className="article-reader-section-title">Related Assets</div>
            <RelatedAssets symbols={article.entities} />
          </div>
        )}

        {/* AI Analysis is shown ONLY in the Right Panel (AIPanel.tsx) — no duplication here */}
      </div>
    </div>
  );
}
