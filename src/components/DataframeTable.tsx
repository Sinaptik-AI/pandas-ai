import React, { useState } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  FileSpreadsheet,
  Minimize2,
  Maximize2,
  X,
  RotateCcw,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  Hash,
} from 'lucide-react';

interface DataframeTableProps {
  columns: string[];
  rows: Record<string, any>[];
  totalRows?: number;
  pageSize?: number;
}

export const DataframeTable: React.FC<DataframeTableProps> = ({
  columns,
  rows,
  totalRows,
  pageSize = 6,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [isTableCollapsed, setIsTableCollapsed] = useState(false);
  const [isGlobalCompact, setIsGlobalCompact] = useState(false);
  const [showIndexCol, setShowIndexCol] = useState(true);
  const [hiddenColumns, setHiddenColumns] = useState<string[]>([]);
  const [compressedColumns, setCompressedColumns] = useState<string[]>([]);
  const [isColumnMenuOpen, setIsColumnMenuOpen] = useState(false);

  if (!rows || rows.length === 0) {
    return (
      <div className="p-4 text-center text-stone-400 text-xs italic bg-[#131822] rounded-xl border border-[#232c3a]">
        Empty dataframe result
      </div>
    );
  }

  const effectiveTotal = totalRows ?? rows.length;
  const visibleColumns = columns.filter((col) => !hiddenColumns.includes(col));
  const totalPages = Math.ceil(rows.length / pageSize);
  const displayedRows = rows.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const toggleHideColumn = (colName: string) => {
    setHiddenColumns((prev) =>
      prev.includes(colName) ? prev.filter((c) => c !== colName) : [...prev, colName]
    );
  };

  const toggleCompressColumn = (colName: string) => {
    setCompressedColumns((prev) =>
      prev.includes(colName) ? prev.filter((c) => c !== colName) : [...prev, colName]
    );
  };

  const handleResetColumns = () => {
    setHiddenColumns([]);
    setCompressedColumns([]);
    setShowIndexCol(true);
    setIsGlobalCompact(false);
  };

  const handleCompressAll = () => {
    setCompressedColumns([...columns]);
    setIsGlobalCompact(true);
  };

  const handleExpandAll = () => {
    setCompressedColumns([]);
    setIsGlobalCompact(false);
  };

  return (
    <div className="w-full bg-[#131822] rounded-xl border border-[#232c3a] overflow-hidden shadow-md">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between px-3.5 py-2.5 bg-[#18202d] border-b border-[#232c3a] gap-2 text-xs">
        <div className="flex items-center gap-2 text-stone-200 font-medium">
          <FileSpreadsheet className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>
            Dataframe Result ({effectiveTotal.toLocaleString()} {effectiveTotal === 1 ? 'row' : 'rows'}
            {hiddenColumns.length > 0 && (
              <span className="text-amber-400 font-normal ml-1">
                • {visibleColumns.length}/{columns.length} cols visible
              </span>
            )}
            )
          </span>
        </div>

        {/* Controls Toolbar */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {/* Compress / Expand Columns Mode */}
          <button
            onClick={() => {
              if (isGlobalCompact) {
                handleExpandAll();
              } else {
                handleCompressAll();
              }
            }}
            className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium transition-colors border cursor-pointer ${
              isGlobalCompact
                ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                : 'bg-[#131822] text-stone-300 border-[#2a364a] hover:bg-[#202b3c] hover:text-white'
            }`}
            title={isGlobalCompact ? 'Expand all columns to full width' : 'Compress all columns to compact width'}
          >
            {isGlobalCompact ? (
              <>
                <Maximize2 className="w-3 h-3 text-amber-400" />
                <span>Expand Cols</span>
              </>
            ) : (
              <>
                <Minimize2 className="w-3 h-3 text-stone-400" />
                <span>Compress Cols</span>
              </>
            )}
          </button>

          {/* Toggle # Index Column */}
          <button
            onClick={() => setShowIndexCol((prev) => !prev)}
            className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-mono transition-colors border cursor-pointer ${
              !showIndexCol
                ? 'bg-rose-500/10 text-rose-300 border-rose-500/30 line-through'
                : 'bg-[#131822] text-stone-300 border-[#2a364a] hover:bg-[#202b3c]'
            }`}
            title={showIndexCol ? 'Remove / Hide "#" row index column' : 'Show "#" row index column'}
          >
            <Hash className="w-3 h-3" />
            <span>#</span>
          </button>

          {/* Column Visibility Selector Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsColumnMenuOpen((prev) => !prev)}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium bg-[#131822] text-stone-300 border border-[#2a364a] hover:bg-[#202b3c] hover:text-white transition-colors cursor-pointer"
              title="Manage column visibility and compression"
            >
              <SlidersHorizontal className="w-3 h-3 text-stone-400" />
              <span>Columns</span>
              {hiddenColumns.length > 0 && (
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
              )}
            </button>

            {isColumnMenuOpen && (
              <div className="absolute right-0 mt-1 w-56 bg-[#151c27] rounded-xl border border-[#2a364a] shadow-2xl py-2 z-40 text-xs animate-in fade-in zoom-in-95 duration-100">
                <div className="flex items-center justify-between px-3 pb-1.5 border-b border-[#232c3a]">
                  <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">
                    Columns ({visibleColumns.length}/{columns.length})
                  </span>
                  {(hiddenColumns.length > 0 || compressedColumns.length > 0 || !showIndexCol) && (
                    <button
                      onClick={handleResetColumns}
                      className="text-[10px] text-amber-400 hover:text-amber-300 flex items-center gap-1 cursor-pointer"
                    >
                      <RotateCcw className="w-2.5 h-2.5" />
                      <span>Reset</span>
                    </button>
                  )}
                </div>

                <div className="max-h-48 overflow-y-auto py-1 divide-y divide-[#1e2736]">
                  {/* Row index col option */}
                  <label className="flex items-center justify-between px-3 py-1.5 hover:bg-[#1c2432] cursor-pointer text-stone-200">
                    <span className="font-mono text-[11px] flex items-center gap-1.5">
                      <Hash className="w-3 h-3 text-stone-400" />
                      <span>Row Index (#)</span>
                    </span>
                    <input
                      type="checkbox"
                      checked={showIndexCol}
                      onChange={() => setShowIndexCol((prev) => !prev)}
                      className="rounded accent-amber-500 cursor-pointer"
                    />
                  </label>

                  {/* Each column option */}
                  {columns.map((col) => {
                    const isVisible = !hiddenColumns.includes(col);
                    const isCompressed = compressedColumns.includes(col);
                    return (
                      <div
                        key={col}
                        className="flex items-center justify-between px-3 py-1.5 hover:bg-[#1c2432]"
                      >
                        <label className="flex items-center gap-2 cursor-pointer flex-1 min-w-0">
                          <input
                            type="checkbox"
                            checked={isVisible}
                            onChange={() => toggleHideColumn(col)}
                            className="rounded accent-amber-500 cursor-pointer"
                          />
                          <span
                            className={`truncate text-[11px] ${
                              isVisible ? 'text-stone-200' : 'text-stone-500 line-through'
                            }`}
                          >
                            {col}
                          </span>
                        </label>

                        {isVisible && (
                          <button
                            onClick={() => toggleCompressColumn(col)}
                            className={`ml-2 px-1.5 py-0.5 rounded text-[10px] cursor-pointer border ${
                              isCompressed
                                ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                                : 'bg-[#121620] text-stone-400 border-[#263143] hover:text-stone-200'
                            }`}
                            title={isCompressed ? 'Expand this column' : 'Compress this column'}
                          >
                            {isCompressed ? 'Expand' : 'Compress'}
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && !isTableCollapsed && (
            <div className="flex items-center gap-1 ml-1 pl-2 border-l border-[#2a364a]">
              <span className="text-[10px] text-stone-400">
                {currentPage}/{totalPages}
              </span>
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                className="p-1 rounded bg-[#131822] hover:bg-[#202b3c] disabled:opacity-30 disabled:cursor-not-allowed text-stone-300 border border-[#2a364a] cursor-pointer"
                title="Previous page"
              >
                <ChevronLeft className="w-3 h-3" />
              </button>
              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                className="p-1 rounded bg-[#131822] hover:bg-[#202b3c] disabled:opacity-30 disabled:cursor-not-allowed text-stone-300 border border-[#2a364a] cursor-pointer"
                title="Next page"
              >
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          )}

          {/* Compress / Expand entire table card */}
          <button
            onClick={() => setIsTableCollapsed((prev) => !prev)}
            className="p-1 rounded-lg bg-[#131822] hover:bg-[#202b3c] text-stone-400 hover:text-stone-200 border border-[#2a364a] transition-colors cursor-pointer ml-0.5"
            title={isTableCollapsed ? 'Expand dataframe table' : 'Compress / Collapse dataframe table'}
          >
            {isTableCollapsed ? (
              <ChevronDown className="w-3.5 h-3.5" />
            ) : (
              <ChevronUp className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* Hidden Columns Restoration Banner if any hidden */}
      {hiddenColumns.length > 0 && !isTableCollapsed && (
        <div className="px-3.5 py-1.5 bg-amber-950/20 border-b border-amber-900/30 text-[11px] text-amber-300 flex items-center justify-between">
          <span>
            {hiddenColumns.length} {hiddenColumns.length === 1 ? 'column' : 'columns'} removed/hidden:{' '}
            <strong className="font-mono">{hiddenColumns.join(', ')}</strong>
          </span>
          <button
            onClick={handleResetColumns}
            className="text-[10px] underline hover:text-amber-200 cursor-pointer font-medium"
          >
            Restore all columns
          </button>
        </div>
      )}

      {/* Table Content Area (Collapsible) */}
      {!isTableCollapsed && (
        <div className="overflow-x-auto max-h-80">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#18202d]/95 border-b border-[#232c3a] text-stone-300 font-semibold sticky top-0 backdrop-blur-xs">
                {showIndexCol && (
                  <th className="py-2.5 px-3 w-10 text-stone-500 font-mono text-[10px] select-none">
                    <div className="flex items-center gap-1">
                      <span>#</span>
                      <button
                        onClick={() => setShowIndexCol(false)}
                        className="text-stone-600 hover:text-rose-400 transition-colors cursor-pointer"
                        title="Remove / Hide this index column"
                      >
                        <X className="w-2.5 h-2.5" />
                      </button>
                    </div>
                  </th>
                )}
                {visibleColumns.map((col) => {
                  const isColCompressed = isGlobalCompact || compressedColumns.includes(col);
                  return (
                    <th
                      key={col}
                      className={`py-2.5 px-3 text-stone-300 font-medium transition-all group select-none ${
                        isColCompressed ? 'max-w-[110px] w-28' : 'whitespace-nowrap'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-1.5">
                        <span
                          className={`truncate ${isColCompressed ? 'font-mono text-[11px]' : ''}`}
                          title={`Column: ${col}${isColCompressed ? ' (Compressed)' : ''}`}
                        >
                          {col}
                        </span>

                        {/* Quick action buttons on column header */}
                        <div className="flex items-center gap-1 opacity-70 group-hover:opacity-100 transition-opacity">
                          {/* Compress/Expand column */}
                          <button
                            onClick={() => toggleCompressColumn(col)}
                            className={`p-0.5 rounded transition-colors cursor-pointer ${
                              isColCompressed
                                ? 'text-amber-400 hover:text-amber-300 bg-amber-500/20'
                                : 'text-stone-500 hover:text-stone-300'
                            }`}
                            title={isColCompressed ? 'Expand this column' : 'Compress this column'}
                          >
                            {isColCompressed ? (
                              <Maximize2 className="w-2.5 h-2.5" />
                            ) : (
                              <Minimize2 className="w-2.5 h-2.5" />
                            )}
                          </button>

                          {/* Remove/Hide column */}
                          <button
                            onClick={() => toggleHideColumn(col)}
                            className="p-0.5 rounded text-stone-500 hover:text-rose-400 transition-colors cursor-pointer"
                            title={`Remove / Hide column "${col}"`}
                          >
                            <X className="w-2.5 h-2.5" />
                          </button>
                        </div>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f2735] text-stone-200">
              {displayedRows.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-[#1a2332]/60 transition-colors">
                  {showIndexCol && (
                    <td className="py-2 px-3 text-stone-500 font-mono text-[10px]">
                      {(currentPage - 1) * pageSize + rIdx + 1}
                    </td>
                  )}
                  {visibleColumns.map((col) => {
                    const isColCompressed = isGlobalCompact || compressedColumns.includes(col);
                    const val = row[col];
                    const display =
                      val === null || val === undefined
                        ? '-'
                        : typeof val === 'object'
                        ? JSON.stringify(val)
                        : String(val);

                    return (
                      <td
                        key={col}
                        className={`py-2 px-3 ${
                          isColCompressed
                            ? 'max-w-[110px] truncate text-[11px]'
                            : 'whitespace-nowrap'
                        }`}
                        title={display}
                      >
                        {typeof val === 'number' ? (
                          <span className="font-mono text-amber-300">{display}</span>
                        ) : (
                          display
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
