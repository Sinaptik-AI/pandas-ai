import React, { useState, useEffect } from 'react';
import {
  Search,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Download,
  RefreshCw,
  Minimize2,
  Maximize2,
  X,
  SlidersHorizontal,
  RotateCcw,
  Hash,
} from 'lucide-react';
import { DatasetSummary } from '../types';

interface DataExplorerViewProps {
  dataset: DatasetSummary;
}

export const DataExplorerView: React.FC<DataExplorerViewProps> = ({ dataset }) => {
  const [rows, setRows] = useState<Record<string, any>[]>([]);
  const [page, setPage] = useState(1);
  const [limit] = useState(25);
  const [totalRows, setTotalRows] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [sortCol, setSortCol] = useState('');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [loading, setLoading] = useState(false);

  // Column compression & removal features
  const [isGlobalCompact, setIsGlobalCompact] = useState(false);
  const [showIndexCol, setShowIndexCol] = useState(true);
  const [hiddenColumns, setHiddenColumns] = useState<string[]>([]);
  const [compressedColumns, setCompressedColumns] = useState<string[]>([]);
  const [isColumnPickerOpen, setIsColumnPickerOpen] = useState(false);

  const fetchRows = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        limit: String(limit),
        search,
        sortCol,
        sortDir,
      });
      const res = await fetch(`/api/datasets/${dataset.id}/rows?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setRows(data.rows);
        setTotalRows(data.totalRows);
        setTotalPages(data.totalPages);
      }
    } catch (err) {
      console.error('Failed to fetch dataset rows:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRows();
  }, [dataset.id, page, sortCol, sortDir]);

  // Reset column adjustments when dataset changes
  useEffect(() => {
    setHiddenColumns([]);
    setCompressedColumns([]);
    setShowIndexCol(true);
    setIsGlobalCompact(false);
  }, [dataset.id]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchRows();
  };

  const handleSort = (colName: string) => {
    if (sortCol === colName) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortCol(colName);
      setSortDir('asc');
    }
    setPage(1);
  };

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
    setCompressedColumns(dataset.columns.map((c) => c.name));
    setIsGlobalCompact(true);
  };

  const handleExpandAll = () => {
    setCompressedColumns([]);
    setIsGlobalCompact(false);
  };

  const visibleColumns = dataset.columns.filter((c) => !hiddenColumns.includes(c.name));

  const handleExportCSV = () => {
    if (!rows || rows.length === 0) return;
    const cols = visibleColumns.map((c) => c.name);
    const csvLines = [
      cols.join(','),
      ...rows.map((row) =>
        cols.map((col) => {
          const val = row[col];
          if (val === null || val === undefined) return '';
          if (typeof val === 'string' && val.includes(',')) return `"${val.replace(/"/g, '""')}"`;
          return String(val);
        }).join(',')
      ),
    ];
    const blob = new Blob([csvLines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${dataset.id}_export_page${page}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Top Controls Card */}
      <div className="bg-[#131822] border border-[#232c3a] rounded-2xl p-4 sm:p-5 shadow-md mb-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-stone-100 tracking-tight flex items-center gap-2">
              <span>{dataset.name}</span>
              <span className="text-xs font-normal text-amber-400 font-mono">
                ({totalRows.toLocaleString()} total rows • {visibleColumns.length}/{dataset.columns.length} columns)
              </span>
            </h2>
            <p className="text-xs text-stone-400 mt-1">
              Interactive tabular data viewer with column compression, expand, and removal controls
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Search */}
            <form onSubmit={handleSearchSubmit} className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search across columns..."
                className="bg-[#18202d] border border-[#293649] rounded-xl pl-8 pr-3 py-1.5 text-xs text-stone-100 focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-400 w-44 sm:w-56 placeholder:text-stone-500"
              />
              <Search className="w-3.5 h-3.5 text-stone-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            </form>

            {/* Compress / Expand Columns Mode */}
            <button
              onClick={() => {
                if (isGlobalCompact) {
                  handleExpandAll();
                } else {
                  handleCompressAll();
                }
              }}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-xl border transition-colors cursor-pointer shadow-sm ${
                isGlobalCompact
                  ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                  : 'bg-[#18202d] text-stone-200 border-[#293649] hover:bg-[#222d3e]'
              }`}
              title={isGlobalCompact ? 'Expand all columns to full width' : 'Compress all columns to compact width'}
            >
              {isGlobalCompact ? (
                <>
                  <Maximize2 className="w-3.5 h-3.5 text-amber-400" />
                  <span>Expand Columns</span>
                </>
              ) : (
                <>
                  <Minimize2 className="w-3.5 h-3.5 text-stone-400" />
                  <span>Compress Columns</span>
                </>
              )}
            </button>

            {/* Toggle # Row Index Column */}
            <button
              onClick={() => setShowIndexCol((prev) => !prev)}
              className={`inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-mono rounded-xl border transition-colors cursor-pointer shadow-sm ${
                !showIndexCol
                  ? 'bg-rose-500/10 text-rose-300 border-rose-500/30 line-through'
                  : 'bg-[#18202d] text-stone-300 border-[#293649] hover:bg-[#222d3e]'
              }`}
              title={showIndexCol ? 'Remove / Hide "#" row number column' : 'Show "#" row number column'}
            >
              <Hash className="w-3.5 h-3.5" />
              <span># Col</span>
            </button>

            {/* Columns Visibility & Compression Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsColumnPickerOpen((prev) => !prev)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-stone-200 bg-[#18202d] hover:bg-[#222d3e] border border-[#293649] rounded-xl transition-colors cursor-pointer shadow-sm"
                title="Manage column visibility and compression"
              >
                <SlidersHorizontal className="w-3.5 h-3.5 text-stone-400" />
                <span>Columns</span>
                {hiddenColumns.length > 0 && (
                  <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                )}
              </button>

              {isColumnPickerOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-[#151c27] rounded-xl border border-[#2a364a] shadow-2xl py-2 z-40 text-xs animate-in fade-in zoom-in-95 duration-100">
                  <div className="flex items-center justify-between px-3 pb-2 border-b border-[#232c3a]">
                    <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">
                      Columns ({visibleColumns.length}/{dataset.columns.length})
                    </span>
                    {(hiddenColumns.length > 0 || compressedColumns.length > 0 || !showIndexCol) && (
                      <button
                        onClick={handleResetColumns}
                        className="text-[11px] text-amber-400 hover:text-amber-300 flex items-center gap-1 cursor-pointer font-medium"
                      >
                        <RotateCcw className="w-3 h-3" />
                        <span>Reset All</span>
                      </button>
                    )}
                  </div>

                  <div className="max-h-60 overflow-y-auto py-1 divide-y divide-[#1e2736]">
                    {/* Row Index toggle */}
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

                    {/* Columns list */}
                    {dataset.columns.map((col) => {
                      const isVisible = !hiddenColumns.includes(col.name);
                      const isCompressed = compressedColumns.includes(col.name);
                      return (
                        <div
                          key={col.name}
                          className="flex items-center justify-between px-3 py-1.5 hover:bg-[#1c2432]"
                        >
                          <label className="flex items-center gap-2 cursor-pointer flex-1 min-w-0">
                            <input
                              type="checkbox"
                              checked={isVisible}
                              onChange={() => toggleHideColumn(col.name)}
                              className="rounded accent-amber-500 cursor-pointer"
                            />
                            <span
                              className={`truncate text-[11px] ${
                                isVisible ? 'text-stone-200' : 'text-stone-500 line-through'
                              }`}
                            >
                              {col.name}
                            </span>
                          </label>

                          {isVisible && (
                            <button
                              onClick={() => toggleCompressColumn(col.name)}
                              className={`ml-2 px-1.5 py-0.5 rounded text-[10px] cursor-pointer border ${
                                isCompressed
                                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/30 font-medium'
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

            {/* Export Page */}
            <button
              onClick={handleExportCSV}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-stone-200 bg-[#18202d] hover:bg-[#222d3e] border border-[#293649] rounded-xl transition-colors cursor-pointer shadow-sm"
              title="Download currently visible page as CSV"
            >
              <Download className="w-3.5 h-3.5 text-stone-400" />
              <span>Export Page</span>
            </button>
          </div>
        </div>
      </div>

      {/* Hidden Columns Restoration Banner */}
      {hiddenColumns.length > 0 && (
        <div className="mb-4 px-4 py-2 bg-amber-950/30 border border-amber-800/40 rounded-xl text-xs text-amber-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>
              {hiddenColumns.length} {hiddenColumns.length === 1 ? 'column' : 'columns'} removed/hidden:{' '}
              <strong className="font-mono">{hiddenColumns.join(', ')}</strong>
            </span>
          </div>
          <button
            onClick={handleResetColumns}
            className="text-xs text-amber-400 hover:text-amber-200 underline font-medium cursor-pointer"
          >
            Restore all columns
          </button>
        </div>
      )}

      {/* Table Container */}
      <div className="bg-[#131822] border border-[#232c3a] rounded-2xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto min-h-[400px]">
          {loading ? (
            <div className="h-64 flex items-center justify-center gap-2 text-stone-400 text-xs">
              <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
              <span>Loading dataset rows...</span>
            </div>
          ) : rows.length === 0 ? (
            <div className="h-64 flex items-center justify-center text-stone-500 text-xs italic">
              No matching records found
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#18202d] border-b border-[#232c3a] text-stone-300 font-semibold sticky top-0 z-10">
                  {showIndexCol && (
                    <th className="py-2.5 px-3 w-12 text-stone-500 font-mono text-[10px] select-none">
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
                    const isColCompressed = isGlobalCompact || compressedColumns.includes(col.name);
                    return (
                      <th
                        key={col.name}
                        className={`py-2.5 px-3 text-stone-300 font-medium transition-all group select-none ${
                          isColCompressed ? 'max-w-[120px] w-32' : 'whitespace-nowrap'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-1.5">
                          {/* Sort click area */}
                          <div
                            onClick={() => handleSort(col.name)}
                            className="flex items-center gap-1.5 cursor-pointer hover:text-amber-300 transition-colors flex-1 min-w-0"
                            title={`Sort by ${col.name}`}
                          >
                            <span
                              className={`truncate font-medium text-stone-200 ${
                                isColCompressed ? 'font-mono text-[11px]' : ''
                              }`}
                            >
                              {col.name}
                            </span>
                            <ArrowUpDown className="w-3 h-3 text-stone-500 shrink-0" />
                            {sortCol === col.name && (
                              <span className="text-[10px] text-amber-400 font-bold shrink-0">
                                {sortDir === 'asc' ? '↑' : '↓'}
                              </span>
                            )}
                          </div>

                          {/* Quick action icons for this column */}
                          <div className="flex items-center gap-1 opacity-70 group-hover:opacity-100 transition-opacity">
                            {/* Compress / Expand this column */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleCompressColumn(col.name);
                              }}
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

                            {/* Remove / Hide this column */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleHideColumn(col.name);
                              }}
                              className="p-0.5 rounded text-stone-500 hover:text-rose-400 transition-colors cursor-pointer"
                              title={`Remove / Hide column "${col.name}"`}
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
                {rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-[#1a2332]/70 transition-colors">
                    {showIndexCol && (
                      <td className="py-2 px-3 text-stone-500 font-mono text-[10px]">
                        {(page - 1) * limit + idx + 1}
                      </td>
                    )}
                    {visibleColumns.map((col) => {
                      const isColCompressed = isGlobalCompact || compressedColumns.includes(col.name);
                      const val = row[col.name];
                      const display =
                        val === null || val === undefined
                          ? '-'
                          : typeof val === 'object'
                          ? JSON.stringify(val)
                          : String(val);

                      return (
                        <td
                          key={col.name}
                          className={`py-2 px-3 font-normal ${
                            isColCompressed
                              ? 'max-w-[120px] truncate text-[11px]'
                              : 'whitespace-nowrap'
                          }`}
                          title={display}
                        >
                          {col.type === 'numeric' && val !== null ? (
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
          )}
        </div>

        {/* Pagination Footer */}
        <div className="flex items-center justify-between px-4 py-3.5 bg-[#10141d] border-t border-[#232c3a] text-xs">
          <div className="text-stone-400">
            Showing <span className="font-medium text-stone-200">{rows.length > 0 ? (page - 1) * limit + 1 : 0}</span> to{' '}
            <span className="font-medium text-stone-200">
              {Math.min(page * limit, totalRows)}
            </span>{' '}
            of <span className="font-medium text-stone-200">{totalRows.toLocaleString()}</span> entries
            {hiddenColumns.length > 0 && (
              <span className="ml-2 text-amber-400/80 font-mono text-[11px]">
                ({visibleColumns.length}/{dataset.columns.length} columns displayed)
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-stone-400">
              Page {page} of {Math.max(totalPages, 1)}
            </span>
            <div className="inline-flex gap-1">
              <button
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                className="p-1.5 rounded-lg bg-[#18202d] border border-[#293649] hover:bg-[#202b3c] disabled:opacity-30 disabled:cursor-not-allowed text-stone-300 cursor-pointer"
                title="Previous page"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={page >= totalPages || loading}
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                className="p-1.5 rounded-lg bg-[#18202d] border border-[#293649] hover:bg-[#202b3c] disabled:opacity-30 disabled:cursor-not-allowed text-stone-300 cursor-pointer"
                title="Next page"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
