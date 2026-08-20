/* ═══════════════════════════════════════════════════════
 * TerminalX — Category Tabs
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useNewsStore } from '@/stores/newsStore';
import { NEWS_CATEGORIES } from '@/lib/constants';

export function CategoryTabs() {
  const category = useNewsStore((s) => s.category);
  const setCategory = useNewsStore((s) => s.setCategory);

  return (
    <div className="category-tabs">
      {NEWS_CATEGORIES.map((cat) => (
        <button
          key={cat}
          className={`category-tab ${category === cat ? 'active' : ''}`}
          onClick={() => setCategory(cat)}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
