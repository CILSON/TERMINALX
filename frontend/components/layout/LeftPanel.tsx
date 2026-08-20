/* ═══════════════════════════════════════════════════════
 * TerminalX — Left Panel (News Feed)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { CategoryTabs } from '@/components/news/CategoryTabs';
import { NewsFeed } from '@/components/news/NewsFeed';

export function LeftPanel() {
  return (
    <aside className="panel left-panel">
      <div className="left-panel-header">
        <span className="left-panel-title">NEWS</span>
        <span className="left-panel-expand">⤢</span>
      </div>
      <CategoryTabs />
      <NewsFeed />
    </aside>
  );
}
