import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Clock,
  AlertCircle,
  RefreshCw,
  Download,
  FileJson,
  FileSpreadsheet,
  Table,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  Minimize2,
  Maximize2,
  X,
  Info,
  CheckCircle2,
  Cpu,
  Lightbulb,
  Trash2,
} from 'lucide-react';
import { DatasetSummary, ChatMessage, QueryResult } from '../types';
import { ChartRenderer } from './ChartRenderer';
import { DataframeTable } from './DataframeTable';
import { CodeViewer } from './CodeViewer';
import { ExportModal } from './ExportModal';
import {
  exportConversationToJson,
  exportConversationToCsv,
  exportDataToCsv,
  exportDataToJson,
  getLatestExportableData,
} from '../utils/exportUtils';

interface ChatQueryViewProps {
  dataset: DatasetSummary;
  messages: ChatMessage[];
  isLoading: boolean;
  onSendQuery: (query: string) => void;
  onClearHistory?: () => void;
}

export const ChatQueryView: React.FC<ChatQueryViewProps> = ({
  dataset,
  messages,
  isLoading,
  onSendQuery,
  onClearHistory,
}) => {
  const [inputQuery, setInputQuery] = useState('');
  const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [exportModalTab, setExportModalTab] = useState<'chat' | 'data'>('chat');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Header compression / removal states
  const [isHeaderCompressed, setIsHeaderCompressed] = useState(false);
  const [isHeaderRemoved, setIsHeaderRemoved] = useState(false);

  // Gemini AI Insights State
  const [aiInsights, setAiInsights] = useState<{
    summary?: string;
    insights: string[];
    suggestedQueries: string[];
    source?: string;
  } | null>(null);
  const [isLoadingInsights, setIsLoadingInsights] = useState(false);
  const [showInsightsPanel, setShowInsightsPanel] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const exportMenuRef = useRef<HTMLDivElement>(null);

  const isMac = typeof window !== 'undefined' && /Mac|iPod|iPhone|iPad/.test(navigator.platform);
  const modSymbol = isMac ? '⌘' : 'Ctrl';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Reset insights when dataset changes
  useEffect(() => {
    setAiInsights(null);
    setShowInsightsPanel(false);
  }, [dataset.id]);

  // Close export dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(e.target as Node)) {
        setIsExportMenuOpen(false);
      }
    };
    if (isExportMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isExportMenuOpen]);

  // Listen for global send triggers
  useEffect(() => {
    const handleGlobalTrigger = (e: CustomEvent) => {
      if (e.detail?.query) {
        onSendQuery(e.detail.query);
      } else if (inputQuery.trim() && !isLoading) {
        onSendQuery(inputQuery);
        setInputQuery('');
      } else {
        inputRef.current?.focus();
      }
    };

    window.addEventListener('trigger-send-message' as any, handleGlobalTrigger as any);
    return () => {
      window.removeEventListener('trigger-send-message' as any, handleGlobalTrigger as any);
    };
  }, [inputQuery, isLoading, onSendQuery]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((prev) => (prev === msg ? null : prev));
    }, 3000);
  };

  const handleFetchInsights = async () => {
    if (aiInsights) {
      setShowInsightsPanel((prev) => !prev);
      return;
    }
    setIsLoadingInsights(true);
    setShowInsightsPanel(true);
    try {
      const res = await fetch(`/api/datasets/${dataset.id}/insights`);
      if (res.ok) {
        const data = await res.json();
        setAiInsights(data);
      }
    } catch (err) {
      console.error('Failed to load Gemini insights:', err);
    } finally {
      setIsLoadingInsights(false);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;
    onSendQuery(inputQuery);
    setInputQuery('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handlePromptClick = (prompt: string) => {
    if (isLoading) return;
    onSendQuery(prompt);
  };

  // Quick export handlers
  const handleExportChatJson = () => {
    exportConversationToJson(dataset, messages);
    setIsExportMenuOpen(false);
    showToast(`Exported ${messages.length} messages to JSON`);
  };

  const handleExportChatCsv = () => {
    exportConversationToCsv(dataset, messages);
    setIsExportMenuOpen(false);
    showToast(`Exported ${messages.length} messages to CSV`);
  };

  const handleExportLatestDataCsv = () => {
    const data = getLatestExportableData(messages, dataset);
    if (!data) {
      showToast('No query data available to export yet');
      return;
    }
    exportDataToCsv(data.columns, data.rows, `${dataset.id}_query_results`);
    setIsExportMenuOpen(false);
    showToast(`Exported ${data.rows.length} rows to CSV`);
  };

  const handleExportLatestDataJson = () => {
    const data = getLatestExportableData(messages, dataset);
    if (!data) {
      showToast('No query data available to export yet');
      return;
    }
    exportDataToJson(data.columns, data.rows, `${dataset.id}_query_results`, { title: data.title });
    setIsExportMenuOpen(false);
    showToast(`Exported ${data.rows.length} rows to JSON`);
  };

  const handleExportMessageData = (result: QueryResult, format: 'csv' | 'json') => {
    if (result.dataframe) {
      if (format === 'csv') {
        exportDataToCsv(
          result.dataframe.columns,
          result.dataframe.rows,
          `${dataset.id}_result_${result.id}`
        );
      } else {
        exportDataToJson(
          result.dataframe.columns,
          result.dataframe.rows,
          `${dataset.id}_result_${result.id}`,
          { query: result.query }
        );
      }
      showToast(`Exported result dataframe to ${format.toUpperCase()}`);
    } else if (result.chart && result.chart.data?.length > 0) {
      const cols = Object.keys(result.chart.data[0]);
      if (format === 'csv') {
        exportDataToCsv(cols, result.chart.data, `${dataset.id}_chart_${result.id}`);
      } else {
        exportDataToJson(cols, result.chart.data, `${dataset.id}_chart_${result.id}`, {
          chartType: result.chart.chartType,
          title: result.chart.title,
        });
      }
      showToast(`Exported chart data to ${format.toUpperCase()}`);
    }
  };

  const hasExportableData = Boolean(getLatestExportableData(messages, dataset));

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto px-4 sm:px-6 py-4 relative">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="absolute top-2 right-6 z-40 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex items-center gap-2 bg-[#18202d] text-stone-100 px-3.5 py-2 rounded-xl text-xs shadow-xl border border-[#2f3c4e]">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Restorable Header Pill if removed */}
      {isHeaderRemoved && (
        <div className="flex items-center justify-between mb-3 px-3.5 py-1.5 bg-[#131822]/90 border border-[#232c3a] rounded-xl text-xs text-stone-400">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-stone-200">{dataset.name}</span>
            <span className="text-[10px] text-stone-500 font-mono">
              ({dataset.rowCount.toLocaleString()} rows, {dataset.columnCount} cols)
            </span>
          </div>
          <button
            onClick={() => setIsHeaderRemoved(false)}
            className="flex items-center gap-1.5 text-[11px] text-amber-400 hover:text-amber-300 font-medium cursor-pointer"
            title="Restore dataset details and suggestions"
          >
            <Maximize2 className="w-3 h-3" />
            <span>Show Dataset Header</span>
          </button>
        </div>
      )}

      {/* Compressed Single-Line Header */}
      {!isHeaderRemoved && isHeaderCompressed && (
        <div className="bg-[#131822] border border-[#232c3a] rounded-xl px-3.5 py-2 mb-3 shadow-sm flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 min-w-0">
            <h2 className="text-xs font-bold text-stone-100 tracking-tight truncate">
              {dataset.name}
            </h2>
            <span className="px-2 py-0.5 rounded-md text-[10px] font-mono bg-[#18202d] text-stone-300 border border-[#283549] shrink-0">
              {dataset.rowCount.toLocaleString()} rows • {dataset.columnCount} cols
            </span>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {/* Gemini Insights Toggle Button */}
            <button
              id="btn-gemini-insights-compressed"
              onClick={handleFetchInsights}
              disabled={isLoadingInsights}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold text-emerald-300 bg-emerald-950/40 hover:bg-emerald-900/40 border border-emerald-800/60 rounded-lg transition-colors cursor-pointer"
              title="Generate natural analytical observations using Gemini AI"
            >
              {isLoadingInsights ? (
                <RefreshCw className="w-3 h-3 text-emerald-400 animate-spin" />
              ) : (
                <Sparkles className="w-3 h-3 text-emerald-400" />
              )}
              <span className="hidden sm:inline">Insights</span>
            </button>

            {/* Quick Export Trigger */}
            <button
              onClick={() => {
                setExportModalTab('chat');
                setIsExportModalOpen(true);
              }}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium text-stone-200 bg-[#18202d] hover:bg-[#202b3c] border border-[#283549] rounded-lg transition-colors cursor-pointer"
              title="Export conversation or query data"
            >
              <Download className="w-3 h-3 text-stone-400" />
              <span>Export</span>
            </button>

            {/* Expand Header Button */}
            <button
              onClick={() => setIsHeaderCompressed(false)}
              className="p-1 text-stone-400 hover:text-stone-100 hover:bg-[#1f2837] rounded-lg border border-[#283549] transition-colors cursor-pointer"
              title="Expand dataset header and suggestions"
            >
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {/* Remove / Close Header Button */}
            <button
              onClick={() => setIsHeaderRemoved(true)}
              className="p-1 text-stone-500 hover:text-rose-400 hover:bg-rose-950/30 rounded-lg border border-transparent hover:border-rose-900/40 transition-colors cursor-pointer"
              title="Remove / Hide header completely to maximize chat space"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Expanded Full Header Info with Export Menu & Gemini Insights */}
      {!isHeaderRemoved && !isHeaderCompressed && (
      <div className="bg-[#131822] border border-[#232c3a] rounded-2xl p-4 sm:p-5 mb-4 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-base font-bold text-stone-100 tracking-tight">
                {dataset.name}
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/10 text-amber-300 border border-amber-500/20">
                Active Dataset
              </span>
            </div>
            <p className="text-xs text-stone-400 mt-1">{dataset.description}</p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {messages.length > 0 && (
              <span
                className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#18202d] text-[11px] text-emerald-400 font-mono border border-[#283549]"
                title="Chat message history is automatically synchronized and persisted in browser localStorage across page reloads"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Session Saved</span>
              </span>
            )}
            <span className="px-2.5 py-1 rounded-lg bg-[#18202d] font-mono text-stone-300 font-medium text-xs border border-[#283549]">
              {dataset.rowCount.toLocaleString()} rows
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-[#18202d] font-mono text-stone-300 font-medium text-xs border border-[#283549]">
              {dataset.columnCount} cols
            </span>

            {/* Gemini Insights Toggle Button */}
            <button
              id="btn-gemini-insights"
              onClick={handleFetchInsights}
              disabled={isLoadingInsights}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-300 bg-emerald-950/40 hover:bg-emerald-900/40 border border-emerald-800/60 rounded-xl transition-colors cursor-pointer"
              title="Generate natural analytical observations using Gemini AI"
            >
              {isLoadingInsights ? (
                <RefreshCw className="w-3.5 h-3.5 text-emerald-400 animate-spin" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              )}
              <span className="hidden sm:inline">Gemini Insights</span>
            </button>

            {/* Export Dropdown Menu */}
            <div className="relative" ref={exportMenuRef}>
              <button
                id="btn-export-menu"
                onClick={() => setIsExportMenuOpen((prev) => !prev)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-stone-200 bg-[#18202d] hover:bg-[#202b3c] border border-[#283549] rounded-xl transition-colors cursor-pointer shadow-sm"
                title="Export conversation or query data (JSON / CSV)"
              >
                <Download className="w-3.5 h-3.5 text-stone-400" />
                <span>Export</span>
                <ChevronDown className="w-3 h-3 text-stone-400" />
              </button>

              {isExportMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-[#151c27] rounded-xl border border-[#2a364a] shadow-2xl py-1.5 z-40 text-xs animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-3 py-1.5 text-[10px] font-bold text-stone-400 uppercase tracking-wider">
                    Export Chat History
                  </div>
                  <button
                    onClick={handleExportChatJson}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-stone-200 hover:bg-[#1d2635] hover:text-amber-300 cursor-pointer text-left"
                  >
                    <FileJson className="w-4 h-4 text-amber-400 shrink-0" />
                    <div>
                      <div className="font-medium">Export Chat as JSON</div>
                      <div className="text-[10px] text-stone-400">Full conversation & code snippets</div>
                    </div>
                  </button>
                  <button
                    onClick={handleExportChatCsv}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-stone-200 hover:bg-[#1d2635] hover:text-emerald-300 cursor-pointer text-left"
                  >
                    <FileSpreadsheet className="w-4 h-4 text-emerald-400 shrink-0" />
                    <div>
                      <div className="font-medium">Export Chat as CSV</div>
                      <div className="text-[10px] text-stone-400">Tabular transcript of Q&A rows</div>
                    </div>
                  </button>

                  <div className="border-t border-[#232c3a] my-1"></div>

                  <div className="px-3 py-1.5 text-[10px] font-bold text-stone-400 uppercase tracking-wider">
                    Export Query Data Results
                  </div>
                  <button
                    onClick={handleExportLatestDataCsv}
                    disabled={!hasExportableData}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-stone-200 hover:bg-[#1d2635] hover:text-emerald-300 cursor-pointer text-left disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <Table className="w-4 h-4 text-emerald-400 shrink-0" />
                    <div>
                      <div className="font-medium">Export Data as CSV</div>
                      <div className="text-[10px] text-stone-400">Latest dataframe/chart records</div>
                    </div>
                  </button>
                  <button
                    onClick={handleExportLatestDataJson}
                    disabled={!hasExportableData}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-stone-200 hover:bg-[#1d2635] hover:text-amber-300 cursor-pointer text-left disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <FileJson className="w-4 h-4 text-amber-400 shrink-0" />
                    <div>
                      <div className="font-medium">Export Data as JSON</div>
                      <div className="text-[10px] text-stone-400">Array of raw data records</div>
                    </div>
                  </button>

                  <div className="border-t border-[#232c3a] my-1"></div>

                  <button
                    onClick={() => {
                      setIsExportMenuOpen(false);
                      setIsExportModalOpen(true);
                    }}
                    className="w-full flex items-center gap-2 px-3 py-1.5 text-stone-300 hover:text-amber-300 text-[11px] font-medium hover:bg-[#1d2635] cursor-pointer"
                  >
                    <span>Preview & Custom Export...</span>
                  </button>

                  {messages.length > 0 && onClearHistory && (
                    <>
                      <div className="border-t border-[#232c3a] my-1"></div>
                      <button
                        onClick={() => {
                          setIsExportMenuOpen(false);
                          onClearHistory();
                          showToast('Chat history cleared from session storage');
                        }}
                        className="w-full flex items-center gap-2 px-3 py-1.5 text-rose-400 hover:text-rose-300 text-[11px] font-medium hover:bg-rose-950/30 cursor-pointer text-left"
                      >
                        <Trash2 className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                        <span>Clear Chat History</span>
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Compress / Collapse Header Button */}
            <button
              onClick={() => setIsHeaderCompressed(true)}
              className="p-1.5 text-stone-400 hover:text-stone-100 bg-[#18202d] hover:bg-[#202b3c] border border-[#283549] rounded-xl transition-colors cursor-pointer"
              title="Compress dataset header to save space"
            >
              <ChevronUp className="w-3.5 h-3.5" />
            </button>

            {/* Remove / Close Header Button */}
            <button
              onClick={() => setIsHeaderRemoved(true)}
              className="p-1.5 text-stone-500 hover:text-rose-400 hover:bg-rose-950/40 border border-transparent hover:border-rose-900/50 rounded-xl transition-colors cursor-pointer"
              title="Remove / Hide dataset header to maximize chat space"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Gemini AI Insights Panel */}
        {showInsightsPanel && aiInsights && (
          <div className="mt-3 p-3.5 rounded-xl bg-gradient-to-r from-emerald-950/40 via-[#141b25] to-amber-950/20 border border-emerald-800/40 animate-in fade-in duration-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-300">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Gemini AI Dataset Insights</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400/80 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/60">
                {aiInsights.source === 'gemini' ? 'Gemini 3.8 Flash' : 'PandasAI Analysis'}
              </span>
            </div>
            <p className="text-xs text-stone-300 leading-relaxed mb-2.5">
              {aiInsights.summary}
            </p>
            <div className="space-y-1.5">
              {aiInsights.insights.map((ins, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-stone-300">
                  <span className="text-emerald-400 font-bold shrink-0">•</span>
                  <span>{ins}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Suggested Prompts */}
        {dataset.suggestedPrompts && dataset.suggestedPrompts.length > 0 && (
          <div className="mt-3 pt-3 border-t border-[#232c3a]">
            <div className="flex items-center gap-1.5 text-xs text-stone-400 mb-2 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Suggested questions for this dataset:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {dataset.suggestedPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePromptClick(prompt)}
                  disabled={isLoading}
                  className="text-xs bg-[#18202d] hover:bg-[#202c3e] hover:text-amber-300 hover:border-amber-500/40 text-stone-300 px-3 py-1.5 rounded-xl border border-[#273447] transition-all text-left cursor-pointer disabled:opacity-50 shadow-sm"
                >
                  "{prompt}"
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
      )}

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 pb-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-[#232c3a] rounded-2xl bg-[#11151e]/50">
            <div className="w-14 h-14 rounded-2xl bg-amber-500/15 border border-amber-500/25 flex items-center justify-center text-3xl mb-3">
              🐼
            </div>
            <h3 className="text-base font-bold text-stone-100 tracking-tight">
              Conversational Data Science with Gemini AI
            </h3>
            <p className="text-xs text-stone-400 max-w-md mt-1 mb-4 leading-relaxed">
              Ask natural-language questions to formulate analytics code, render responsive
              visualizations, and safely query tabular dataframes.
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg mb-4">
              {dataset.suggestedPrompts.slice(0, 3).map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePromptClick(prompt)}
                  className="text-xs bg-[#18202d] hover:bg-[#202c3e] text-stone-200 px-3 py-1.5 rounded-xl border border-[#283549] shadow-sm hover:border-amber-400/50 hover:text-amber-300 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
            <div className="inline-flex items-center gap-2 text-[11px] text-stone-400 bg-[#161c26] border border-[#263244] px-3.5 py-1.5 rounded-xl">
              <span>Pro-tip: Press</span>
              <kbd className="px-1.5 py-0.5 bg-[#0d1117] rounded border border-[#2e3b4e] font-mono text-[10px] text-amber-300">
                {modSymbol} + K
              </kbd>
              <span>to switch datasets, or</span>
              <kbd className="px-1.5 py-0.5 bg-[#0d1117] rounded border border-[#2e3b4e] font-mono text-[10px] text-amber-300">
                {modSymbol} + Enter
              </kbd>
              <span>to send queries</span>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className="space-y-2">
              {msg.role === 'user' ? (
                <div className="flex justify-end">
                  <div className="max-w-2xl bg-[#1c2432] text-stone-100 border border-[#2e3c50] px-4 py-2.5 rounded-2xl rounded-tr-xs text-xs sm:text-sm font-medium shadow-md">
                    {msg.content}
                  </div>
                </div>
              ) : (
                <div className="flex justify-start">
                  <div className="max-w-3xl w-full bg-[#131822] border border-[#232c3a] rounded-2xl rounded-tl-xs p-4 sm:p-5 shadow-lg space-y-3">
                    {/* Header badge & time */}
                    <div className="flex items-center justify-between text-xs text-stone-400 border-b border-[#232c3a] pb-2">
                      <div className="flex items-center gap-2">
                        {msg.result?.engine === 'gemini' ? (
                          <div className="flex items-center gap-1.5 text-emerald-300 font-semibold text-xs">
                            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Gemini 3.8 Flash</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5 text-amber-400 font-semibold text-xs">
                            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                            <span>PandasAI Engine</span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center gap-3">
                        {msg.result?.executionTimeMs !== undefined && (
                          <div className="flex items-center gap-1 font-mono text-[11px] text-stone-400">
                            <Clock className="w-3 h-3" />
                            <span>{msg.result.executionTimeMs}ms</span>
                          </div>
                        )}

                        {/* Inline Export Actions for this result */}
                        {msg.result && (msg.result.dataframe || (msg.result.chart && msg.result.chart.data?.length > 0)) && (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleExportMessageData(msg.result!, 'csv')}
                              className="px-2 py-0.5 text-[10px] font-medium text-stone-300 hover:text-emerald-300 bg-[#18202d] hover:bg-[#202c3e] rounded border border-[#283549] transition-colors cursor-pointer flex items-center gap-1"
                              title="Export this result as CSV"
                            >
                              <FileSpreadsheet className="w-3 h-3 text-emerald-400" />
                              <span>CSV</span>
                            </button>
                            <button
                              onClick={() => handleExportMessageData(msg.result!, 'json')}
                              className="px-2 py-0.5 text-[10px] font-medium text-stone-300 hover:text-amber-300 bg-[#18202d] hover:bg-[#202c3e] rounded border border-[#283549] transition-colors cursor-pointer flex items-center gap-1"
                              title="Export this result as JSON"
                            >
                              <FileJson className="w-3 h-3 text-amber-400" />
                              <span>JSON</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Security Alert Banner if Blocked */}
                    {msg.result?.securityCheck && !msg.result.securityCheck.isSafe && (
                      <div className="p-3 bg-rose-950/50 border border-rose-800/80 rounded-xl text-rose-200 text-xs flex items-start gap-2.5">
                        <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                        <div>
                          <p className="font-semibold text-rose-100">
                            Issue #1895 Mitigation: Sandbox Blocked Untrusted Execution
                          </p>
                          <p className="text-rose-300 mt-0.5 text-[11px] leading-relaxed">
                            {msg.result.securityCheck.violations.join('; ')}
                          </p>
                          <p className="text-rose-400 text-[10px] mt-1 font-mono">
                            Policy: Default Sandbox (Restricted __builtins__, AST Allowlist, Fail-Closed)
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Text Answer */}
                    <p className="text-stone-200 text-xs sm:text-sm leading-relaxed font-normal">
                      {msg.content}
                    </p>

                    {/* Visual Chart if returned */}
                    {msg.result?.chart && (
                      <div className="pt-2">
                        <ChartRenderer config={msg.result.chart} />
                      </div>
                    )}

                    {/* Dataframe preview if returned */}
                    {msg.result?.dataframe && (
                      <div className="pt-2">
                        <DataframeTable
                          columns={msg.result.dataframe.columns}
                          rows={msg.result.dataframe.rows}
                          totalRows={msg.result.dataframe.totalRows}
                        />
                      </div>
                    )}

                    {/* Generated Code Viewer */}
                    {msg.result?.codeSnippet && (
                      <CodeViewer
                        code={msg.result.codeSnippet}
                        datasetId={dataset.id}
                        securityCheck={msg.result.securityCheck}
                      />
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[#131822] border border-[#232c3a] rounded-2xl p-4 shadow-md flex items-center gap-3">
              <RefreshCw className="w-4 h-4 text-amber-400 animate-spin" />
              <div className="space-y-1">
                <span className="text-xs font-medium text-stone-200 flex items-center gap-2">
                  <span>Gemini AI is analyzing dataset & generating visualizations...</span>
                </span>
                <p className="text-[11px] text-stone-400">
                  Parsing schema, executing transformations and rendering charts
                </p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form with Keyboard Shortcut Integration */}
      <div className="pt-2">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            ref={inputRef}
            type="text"
            id="query-input"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Ask a question about ${dataset.name}... (Press ${modSymbol} + Enter to send)`}
            className="w-full bg-[#131822] border border-[#283549] hover:border-[#384a66] focus:border-amber-400 rounded-xl pl-4 pr-24 py-3 text-xs sm:text-sm text-stone-100 shadow-md focus:outline-none focus:ring-3 focus:ring-amber-500/20 transition-all placeholder:text-stone-500"
            disabled={isLoading}
          />
          <div className="absolute right-2 flex items-center gap-1.5">
            <span className="hidden sm:inline-block text-[10px] font-mono text-stone-400 bg-[#0d1117] border border-[#283549] px-1.5 py-0.5 rounded">
              {modSymbol}+↵
            </span>
            <button
              type="submit"
              id="query-submit-btn"
              disabled={!inputQuery.trim() || isLoading}
              className="p-2 bg-amber-500 hover:bg-amber-600 disabled:opacity-30 disabled:hover:bg-amber-500 text-stone-950 font-bold rounded-lg transition-colors cursor-pointer shadow-sm flex items-center justify-center"
              title={`Run Query (${modSymbol} + Enter)`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
        <div className="flex items-center justify-between text-[11px] text-stone-400 mt-1.5 px-1">
          <span>Conversational analytics powered by Gemini AI with secure sandbox execution.</span>
          <div className="hidden md:flex items-center gap-2">
            <span>
              <kbd className="font-mono text-amber-400">{modSymbol}+K</kbd> Switch dataset
            </span>
            <span>·</span>
            <span>
              <kbd className="font-mono text-amber-400">{modSymbol}+Enter</kbd> Send
            </span>
          </div>
        </div>
      </div>

      {/* Export Preview / Full Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        dataset={dataset}
        messages={messages}
        defaultTab={exportModalTab}
      />
    </div>
  );
};
