import React, { useState } from 'react';
import {
  Download,
  X,
  FileJson,
  FileSpreadsheet,
  Copy,
  Check,
  Table,
  MessageSquare,
} from 'lucide-react';
import { ChatMessage, DatasetSummary } from '../types';
import {
  exportConversationToJson,
  exportConversationToCsv,
  exportDataToCsv,
  exportDataToJson,
  getLatestExportableData,
  convertRowsToCsv,
} from '../utils/exportUtils';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  dataset: DatasetSummary;
  messages: ChatMessage[];
  defaultTab?: 'chat' | 'data';
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  dataset,
  messages,
  defaultTab = 'chat',
}) => {
  const [activeType, setActiveType] = useState<'chat' | 'data'>(defaultTab);
  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const latestData = getLatestExportableData(messages, dataset);

  // Calculate preview content
  let previewText = '';
  if (activeType === 'chat') {
    if (format === 'json') {
      const payload = {
        exportedAt: new Date().toISOString(),
        dataset: { id: dataset.id, name: dataset.name },
        totalMessages: messages.length,
        messages: messages.map((m) => ({
          role: m.role,
          timestamp: m.timestamp,
          content: m.content,
          queryType: m.result?.type,
          executionTimeMs: m.result?.executionTimeMs,
          codeSnippet: m.result?.codeSnippet,
        })),
      };
      previewText = JSON.stringify(payload, null, 2);
    } else {
      const columns = ['Role', 'Timestamp', 'Content / Answer', 'Execution Time', 'Result Type'];
      const rows = messages.map((m) => ({
        Role: m.role.toUpperCase(),
        Timestamp: m.timestamp,
        'Content / Answer': m.content,
        'Execution Time': m.result?.executionTimeMs ? `${m.result.executionTimeMs}ms` : '',
        'Result Type': m.result?.type || '',
      }));
      previewText = convertRowsToCsv(columns, rows);
    }
  } else {
    // Data results
    if (latestData) {
      if (format === 'json') {
        previewText = JSON.stringify(
          {
            title: latestData.title,
            columns: latestData.columns,
            totalRows: latestData.rows.length,
            data: latestData.rows.slice(0, 10),
          },
          null,
          2
        );
      } else {
        previewText = convertRowsToCsv(latestData.columns, latestData.rows.slice(0, 10));
      }
    } else {
      previewText = 'No data result available to export yet. Run a query first!';
    }
  }

  const handleDownload = () => {
    if (activeType === 'chat') {
      if (format === 'json') {
        exportConversationToJson(dataset, messages);
      } else {
        exportConversationToCsv(dataset, messages);
      }
    } else {
      if (latestData) {
        if (format === 'json') {
          exportDataToJson(latestData.columns, latestData.rows, `${dataset.id}_query_results`);
        } else {
          exportDataToCsv(latestData.columns, latestData.rows, `${dataset.id}_query_results`);
        }
      }
    }
    onClose();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(previewText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-100"
      onClick={onClose}
    >
      <div
        className="bg-[#121620] rounded-2xl max-w-2xl w-full border border-[#273346] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150 flex flex-col max-h-[85vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 bg-[#0a0d14] text-white flex items-center justify-between border-b border-[#232c3a]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
              <Download className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold tracking-tight">Export Data & Chat</h3>
              <p className="text-[11px] text-stone-400">
                Download analytics outputs or conversational histories
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {/* Export Target Selection */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setActiveType('chat')}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                activeType === 'chat'
                  ? 'border-amber-500/60 bg-amber-500/10 ring-1 ring-amber-500/40 text-stone-100'
                  : 'border-[#273346] bg-[#161c26] hover:bg-[#1d2534] text-stone-300'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold">Chat Conversation</span>
              </div>
              <p className="text-[11px] text-stone-400">
                {messages.length} messages, code snippets, timestamps & safety audits
              </p>
            </button>

            <button
              onClick={() => setActiveType('data')}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                activeType === 'data'
                  ? 'border-amber-500/60 bg-amber-500/10 ring-1 ring-amber-500/40 text-stone-100'
                  : 'border-[#273346] bg-[#161c26] hover:bg-[#1d2534] text-stone-300'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <Table className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold">Data Results</span>
              </div>
              <p className="text-[11px] text-stone-400">
                {latestData
                  ? `${latestData.rows.length.toLocaleString()} rows (${latestData.columns.length} columns)`
                  : 'No active query result'}
              </p>
            </button>
          </div>

          {/* Format Selection */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-stone-300">Format:</span>
              <div className="inline-flex bg-[#0b0e14] p-1 rounded-xl border border-[#232c3a]">
                <button
                  onClick={() => setFormat('csv')}
                  className={`inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-lg transition-all cursor-pointer ${
                    format === 'csv'
                      ? 'bg-[#18212e] text-emerald-300 shadow-sm font-semibold'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                >
                  <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                  <span>CSV (.csv)</span>
                </button>
                <button
                  onClick={() => setFormat('json')}
                  className={`inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-lg transition-all cursor-pointer ${
                    format === 'json'
                      ? 'bg-[#18212e] text-amber-300 shadow-sm font-semibold'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                >
                  <FileJson className="w-3.5 h-3.5 text-amber-400" />
                  <span>JSON (.json)</span>
                </button>
              </div>
            </div>

            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3 py-1 text-xs text-stone-300 hover:text-stone-100 bg-[#161c26] border border-[#273346] rounded-lg hover:bg-[#1f2838] transition-colors cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          {/* Preview Window */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-stone-400 font-mono">
              <span>Preview ({format.toUpperCase()})</span>
              {activeType === 'data' && latestData && (
                <span>Showing first {Math.min(10, latestData.rows.length)} of {latestData.rows.length} rows</span>
              )}
            </div>
            <pre className="bg-[#090c12] text-amber-200/90 font-mono text-[11px] p-3.5 rounded-xl border border-[#232c3a] overflow-x-auto max-h-56 leading-relaxed selection:bg-amber-500/30">
              {previewText}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-[#0b0e14] border-t border-[#232c3a] flex items-center justify-between">
          <span className="text-xs text-stone-400">
            {activeType === 'chat'
              ? `Exporting ${messages.length} messages from "${dataset.name}"`
              : latestData
              ? `Exporting ${latestData.rows.length} records (${latestData.title})`
              : 'Ready to export'}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3.5 py-2 text-xs font-medium text-stone-400 hover:text-stone-200 rounded-lg cursor-pointer"
            >
              Cancel
            </button>
            <button
              onClick={handleDownload}
              disabled={activeType === 'data' && !latestData}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-stone-950 text-xs font-bold rounded-xl shadow-sm cursor-pointer transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Download {format.toUpperCase()}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
