/* ═══════════════════════════════════════════════════════
 * TerminalX — useCommand Hook
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useCallback, useEffect, useMemo } from 'react';
import { useCommandStore } from '@/stores/commandStore';
import { useNewsStore } from '@/stores/newsStore';
import { COMMANDS, BLOOMBERG_COMMANDS, CATEGORY_COMMAND_MAP } from '@/lib/constants';

export function useCommand() {
  const query = useCommandStore((s) => s.query);
  const history = useCommandStore((s) => s.history);
  const isOpen = useCommandStore((s) => s.isOpen);
  const activeView = useCommandStore((s) => s.activeView);
  const assetSymbol = useCommandStore((s) => s.assetSymbol);
  const searchQuery = useCommandStore((s) => s.searchQuery);
  const setQuery = useCommandStore((s) => s.setQuery);
  const executeCommand = useCommandStore((s) => s.executeCommand);
  const toggleOpen = useCommandStore((s) => s.toggleOpen);
  const setOpen = useCommandStore((s) => s.setOpen);
  const setActiveView = useCommandStore((s) => s.setActiveView);
  const setCategory = useNewsStore((s) => s.setCategory);

  // Filter suggestions based on current query
  const suggestions = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toUpperCase().trim();
    return COMMANDS.filter((cmd) =>
      cmd.startsWith(q)
    ).map((cmd) => ({
      command: cmd,
      description: BLOOMBERG_COMMANDS[cmd] || '',
    }));
  }, [query]);

  const handleExecute = useCallback(
    (cmd: string) => {
      const trimmed = cmd.trim().toUpperCase();

      // If it maps to a category, update news store
      if (trimmed in CATEGORY_COMMAND_MAP) {
        setCategory(CATEGORY_COMMAND_MAP[trimmed]);
      } else if (trimmed === 'NEWS' || trimmed === 'TOP') {
        setCategory(trimmed);
      }

      executeCommand(cmd);
    },
    [executeCommand, setCategory]
  );

  // Global keyboard shortcut: '/' to focus command bar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === '/' &&
        !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)
      ) {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === 'Escape') {
        setOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setOpen]);

  return {
    query,
    history,
    isOpen,
    activeView,
    assetSymbol,
    searchQuery,
    suggestions,
    setQuery,
    execute: handleExecute,
    toggleOpen,
    setOpen,
    setActiveView,
  };
}
