/* ═══════════════════════════════════════════════════════
 * TerminalX — CommandBar
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useRef, useState, useEffect, useCallback } from 'react';
import { useCommand } from '@/hooks/useCommand';

export function CommandBar() {
  const inputRef = useRef<HTMLInputElement>(null);
  const { query, suggestions, isOpen, setQuery, execute, setOpen } = useCommand();
  const [selectedIdx, setSelectedIdx] = useState(-1);
  const [historyIdx, setHistoryIdx] = useState(-1);
  const { history } = useCommand();

  // Focus when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const showDropdown = query.trim().length > 0 && suggestions.length > 0;

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        if (selectedIdx >= 0 && suggestions[selectedIdx]) {
          execute(suggestions[selectedIdx].command);
        } else if (query.trim()) {
          execute(query);
        }
        setSelectedIdx(-1);
        setHistoryIdx(-1);
        return;
      }

      if (e.key === 'Escape') {
        setOpen(false);
        inputRef.current?.blur();
        return;
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (showDropdown) {
          setSelectedIdx((prev) => Math.min(prev + 1, suggestions.length - 1));
        }
        return;
      }

      if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (showDropdown && selectedIdx > 0) {
          setSelectedIdx((prev) => prev - 1);
        } else if (!showDropdown && history.length > 0) {
          const newIdx = Math.min(historyIdx + 1, history.length - 1);
          setHistoryIdx(newIdx);
          setQuery(history[newIdx]);
        }
        return;
      }

      if (e.key === 'Tab' && showDropdown) {
        e.preventDefault();
        const idx = selectedIdx >= 0 ? selectedIdx : 0;
        if (suggestions[idx]) {
          setQuery(suggestions[idx].command);
          setSelectedIdx(-1);
        }
      }
    },
    [query, suggestions, selectedIdx, showDropdown, history, historyIdx, execute, setQuery, setOpen]
  );

  return (
    <div className="command-bar">
      <input
        ref={inputRef}
        type="text"
        className="command-bar-input"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setSelectedIdx(-1);
          setHistoryIdx(-1);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
        placeholder="Type command... (NEWS, MKT, CAL, BTC...)"
        spellCheck={false}
        autoComplete="off"
      />
      <span className="command-bar-shortcut">/</span>

      {showDropdown && (
        <div className="command-bar-dropdown">
          {suggestions.map((s, i) => (
            <div
              key={s.command}
              className={`command-bar-item ${i === selectedIdx ? 'active' : ''}`}
              onClick={() => {
                execute(s.command);
                setSelectedIdx(-1);
              }}
              onMouseEnter={() => setSelectedIdx(i)}
            >
              <span className="command-bar-item-cmd">{s.command}</span>
              <span className="command-bar-item-desc">{s.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
