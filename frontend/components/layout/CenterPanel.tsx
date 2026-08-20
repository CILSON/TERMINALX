/* ═══════════════════════════════════════════════════════
 * TerminalX — Center Panel (Dynamic Content)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useCommandStore } from '@/stores/commandStore';
import { useNewsStore } from '@/stores/newsStore';
import { AssetDetail } from '@/components/market/AssetDetail';
import { ArticleReader } from '@/components/article/ArticleReader';
import { MarketHeatmap } from '@/components/market/MarketHeatmap';
import { EconomicCalendar } from '@/components/calendar/EconomicCalendar';
import { MarketOverview } from '@/components/market/MarketOverview';
import { NewsFeed } from '@/components/news/NewsFeed';

export function CenterPanel() {
  const activeView = useCommandStore((s) => s.activeView);
  const selectedArticle = useNewsStore((s) => s.selectedArticle);

  if (selectedArticle) {
    return <main className="center-panel"><ArticleReader article={selectedArticle} /></main>;
  }

  const renderView = () => {
    switch (activeView) {
      case 'calendar': return <EconomicCalendar />;
      case 'heatmap': return <MarketHeatmap />;
      case 'market': return <MarketOverview />;
      case 'news': return <NewsFeed />;
      case 'asset':
      case 'search':
      default:
        return <AssetDetail />;
    }
  };

  return <main className="center-panel">{renderView()}</main>;
}
