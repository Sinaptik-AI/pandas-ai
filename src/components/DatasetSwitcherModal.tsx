import React, { useState, useEffect, useRef } from 'react';
import { Database, Search, Check, Plus, CornerDownLeft, X } from 'lucide-react';

interface DatasetSwitcherModalProps {
  isOpen: boolean;
  onClose: () => void;
  datasets: { id: string; name: string; rowCount: number; columnCount: number }[];
  currentDatasetId: string;
  onSelectDataset: (id: string) => void;
  onOpenUpload: () => void;
}

export const DatasetSwitcherModal: React.FC<DatasetSwitcherModalProps> = ({
  isOpen,
  onClose,
  datasets,
  currentDatasetId,
  onSelectDataset,
  onOpenUpload,
}) => {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const filteredDatasets = datasets.filter((d) =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.id.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setSearch('');
      const currentIndex = datasets.findIndex((d) => d.id === currentDatasetId);
      setSelectedIndex(currentIndex >= 0 ? currentIndex : 0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen, currentDatasetId, datasets]);

  useEffect(() => {
    if (selectedIndex >= filteredDatasets.length) {
      setSelectedIndex(Math.max(0, filteredDatasets.length - 1));
    }
  }, [filteredDatasets.length, selectedIndex]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % Math.max(1, filteredDatasets.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filteredDatasets.length) % Math.max(1, filteredDatasets.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredDatasets[selectedIndex]) {
        onSelectDataset(filteredDatasets[selectedIndex].id);
        onClose();
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-start justify-center p-4 pt-16 sm:pt-24 animate-in fade-in duration-100"
      onClick={onClose}
    >
      <div
        className="bg-[#121620] rounded-2xl max-w-lg w-full border border-[#273346] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        {/* Search Header */}
        <div className="p-3.5 border-b border-[#232c3a] flex items-center gap-2.5 bg-[#0b0e14]">
          <Search className="w-4 h-4 text-stone-400 shrink-0 ml-1.5" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Search datasets... (e.g. Heart, Loans, Titanic)"
            className="w-full bg-transparent text-sm text-stone-100 placeholder:text-stone-500 focus:outline-none"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="p-1 text-stone-400 hover:text-stone-200 rounded-md"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <kbd className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-mono text-stone-400 bg-[#161c26] border border-[#2a364a] rounded">
            ESC
          </kbd>
        </div>

        {/* Dataset List */}
        <div ref={listRef} className="max-h-72 overflow-y-auto p-2 space-y-1">
          {filteredDatasets.length === 0 ? (
            <div className="py-8 text-center text-xs text-stone-500">
              No datasets found matching "{search}"
            </div>
          ) : (
            filteredDatasets.map((d, idx) => {
              const isSelected = idx === selectedIndex;
              const isCurrent = d.id === currentDatasetId;

              return (
                <div
                  key={d.id}
                  onClick={() => {
                    onSelectDataset(d.id);
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-amber-500/15 text-stone-100 border border-amber-500/30'
                      : 'hover:bg-[#18202d] text-stone-300 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        isCurrent
                          ? 'bg-amber-500 text-stone-950 font-bold'
                          : isSelected
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-[#18202d] text-stone-400'
                      }`}
                    >
                      <Database className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold truncate">{d.name}</span>
                        {isCurrent && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
                            Active
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-stone-400 truncate mt-0.5">
                        {d.rowCount.toLocaleString()} rows · {d.columnCount} columns
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {isCurrent ? (
                      <Check className="w-4 h-4 text-amber-400" />
                    ) : isSelected ? (
                      <div className="flex items-center gap-1 text-[11px] font-mono text-amber-300 bg-amber-500/20 px-2 py-0.5 rounded">
                        <span>Select</span>
                        <CornerDownLeft className="w-3 h-3" />
                      </div>
                    ) : null}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Actions & Shortcut Hints */}
        <div className="px-4 py-2.5 bg-[#0b0e14] border-t border-[#232c3a] flex items-center justify-between text-xs">
          <div className="flex items-center gap-3 text-[11px] text-stone-400">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-[#161c26] border border-[#2a364a] rounded font-mono text-[10px] text-stone-300">↑</kbd>
              <kbd className="px-1.5 py-0.5 bg-[#161c26] border border-[#2a364a] rounded font-mono text-[10px] text-stone-300">↓</kbd>
              Navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-[#161c26] border border-[#2a364a] rounded font-mono text-[10px] text-stone-300">↵</kbd>
              Switch
            </span>
          </div>

          <button
            onClick={() => {
              onClose();
              onOpenUpload();
            }}
            className="flex items-center gap-1.5 text-stone-300 hover:text-amber-400 text-[11px] font-medium transition-colors cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Upload New CSV</span>
          </button>
        </div>
      </div>
    </div>
  );
};
