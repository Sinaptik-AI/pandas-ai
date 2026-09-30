import React, { useState } from 'react';
import {
  Database,
  Sparkles,
  Plus,
  Table2,
  MessageSquare,
  BarChart3,
  ShieldCheck,
  X,
  CheckCircle2,
  Lock,
  Keyboard,
  Cpu,
} from 'lucide-react';

interface NavbarProps {
  datasets: { id: string; name: string; rowCount: number; columnCount: number }[];
  currentDatasetId: string;
  onSelectDataset: (id: string) => void;
  onOpenUpload: () => void;
  onOpenDatasetSwitcher: () => void;
  onOpenShortcuts: () => void;
  activeTab: 'chat' | 'table' | 'schema';
  onChangeTab: (tab: 'chat' | 'table' | 'schema') => void;
  hasGeminiKey: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  datasets,
  currentDatasetId,
  onSelectDataset,
  onOpenUpload,
  onOpenDatasetSwitcher,
  onOpenShortcuts,
  activeTab,
  onChangeTab,
  hasGeminiKey,
}) => {
  const [showSecurityModal, setShowSecurityModal] = useState(false);

  const isMac = typeof window !== 'undefined' && /Mac|iPod|iPhone|iPad/.test(navigator.platform);
  const modSymbol = isMac ? '⌘' : 'Ctrl';

  const currentDataset = datasets.find((d) => d.id === currentDatasetId);

  return (
    <>
      <header className="bg-[#10141d]/95 backdrop-blur-md border-b border-[#232c3a] sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Brand */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-lg shadow-sm">
                🐼
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-stone-100 tracking-tight text-lg">PandasAI</span>
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md bg-[#18202d] text-amber-400 border border-amber-500/20">
                    Studio
                  </span>
                </div>
                <p className="text-xs text-stone-400 hidden sm:block">
                  Conversational Analytics & Visualization
                </p>
              </div>
            </div>

            {/* Dataset Switcher & Upload */}
            <div className="flex items-center gap-2">
              {/* Quick Switch Button with Cmd+K */}
              <button
                id="btn-dataset-switcher"
                onClick={onOpenDatasetSwitcher}
                className="hidden sm:inline-flex items-center gap-2 bg-[#161c26] hover:bg-[#1d2533] border border-[#273346] hover:border-amber-500/50 text-stone-200 text-xs sm:text-sm font-medium rounded-xl px-3 py-1.5 transition-colors cursor-pointer shadow-sm"
                title={`Switch dataset (${modSymbol} + K)`}
              >
                <Database className="w-3.5 h-3.5 text-amber-400" />
                <span className="max-w-[130px] truncate">{currentDataset?.name || 'Select Dataset'}</span>
                <span className="text-[10px] font-mono text-stone-400 bg-[#0d1117] border border-[#273346] px-1.5 py-0.5 rounded">
                  {modSymbol}K
                </span>
              </button>

              {/* Standard Dropdown fallback on mobile */}
              <div className="relative sm:hidden">
                <select
                  id="dataset-selector"
                  value={currentDatasetId}
                  onChange={(e) => onSelectDataset(e.target.value)}
                  className="appearance-none bg-[#161c26] border border-[#273346] text-stone-200 text-xs font-medium rounded-lg pl-2.5 pr-7 py-1.5 focus:outline-none focus:ring-2 focus:ring-amber-500/30"
                >
                  {datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-1.5 text-stone-400">
                  <Database className="w-3 h-3" />
                </div>
              </div>

              <button
                id="btn-upload-dataset"
                onClick={onOpenUpload}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-stone-200 bg-[#161c26] hover:bg-[#202938] border border-[#273346] rounded-xl transition-colors cursor-pointer"
                title={`Upload custom CSV dataset (${modSymbol} + U)`}
              >
                <Plus className="w-3.5 h-3.5 text-stone-400" />
                <span className="hidden md:inline">Upload CSV</span>
              </button>
            </div>

            {/* Navigation Tabs & Engine Badges */}
            <div className="flex items-center gap-2 sm:gap-3">
              <nav className="flex items-center bg-[#0c0f16] p-1 rounded-xl border border-[#232c3a]">
                <button
                  id="tab-btn-chat"
                  onClick={() => onChangeTab('chat')}
                  className={`inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                    activeTab === 'chat'
                      ? 'bg-[#18212e] text-amber-400 shadow-sm border border-[#2e3c50]'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                  title={`AI Chat (${modSymbol} + 1)`}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>AI Chat</span>
                </button>

                <button
                  id="tab-btn-table"
                  onClick={() => onChangeTab('table')}
                  className={`inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                    activeTab === 'table'
                      ? 'bg-[#18212e] text-amber-400 shadow-sm border border-[#2e3c50]'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                  title={`Data Explorer (${modSymbol} + 2)`}
                >
                  <Table2 className="w-3.5 h-3.5" />
                  <span className="hidden xs:inline">Explorer</span>
                </button>

                <button
                  id="tab-btn-schema"
                  onClick={() => onChangeTab('schema')}
                  className={`inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                    activeTab === 'schema'
                      ? 'bg-[#18212e] text-amber-400 shadow-sm border border-[#2e3c50]'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                  title={`Schema (${modSymbol} + 3)`}
                >
                  <BarChart3 className="w-3.5 h-3.5" />
                  <span className="hidden xs:inline">Schema</span>
                </button>
              </nav>

              {/* Gemini AI Status Badge */}
              <div
                className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-emerald-950/60 text-emerald-300 border-emerald-800/80 shadow-2xs"
                title="Google Gemini 3.8 Flash AI Model integrated for high-precision query parsing and visual charting"
              >
                <Sparkles className="w-3 h-3 text-emerald-400 animate-pulse" />
                <span>Gemini 3.8 Flash</span>
              </div>

              {/* Sandbox Status Badge */}
              <button
                onClick={() => setShowSecurityModal(true)}
                className="inline-flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full text-xs font-medium bg-[#14201c] hover:bg-[#1a2b25] text-emerald-300 border border-emerald-800/70 transition-colors cursor-pointer"
                title="View Sandbox Security Architecture (Issue #1895 Resolution)"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span className="hidden md:inline">Sandbox Active</span>
              </button>

              {/* Keyboard Shortcuts Guide Button */}
              <button
                id="btn-shortcuts-guide"
                onClick={onOpenShortcuts}
                className="p-1.5 sm:px-2 sm:py-1.5 rounded-xl text-stone-400 hover:text-stone-100 hover:bg-[#18202d] border border-transparent hover:border-[#273346] transition-colors cursor-pointer flex items-center gap-1 text-xs"
                title="Keyboard Shortcuts (?)"
              >
                <Keyboard className="w-4 h-4 text-stone-400" />
                <span className="hidden xl:inline text-[11px] font-mono text-stone-400">?</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Security Architecture & Issue #1895 Modal */}
      {showSecurityModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#12161f] rounded-2xl max-w-xl w-full border border-[#273346] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-4 bg-[#0a0d14] text-white flex items-center justify-between border-b border-[#232c3a]">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold tracking-tight">
                  PandasAI Secure-by-Default Sandbox
                </h3>
              </div>
              <button
                onClick={() => setShowSecurityModal(false)}
                className="p-1 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs sm:text-sm text-stone-300 leading-relaxed">
              <div className="p-3.5 bg-emerald-950/40 border border-emerald-800/80 rounded-xl text-emerald-200">
                <div className="font-semibold text-emerald-300 flex items-center gap-1.5 mb-1">
                  <Lock className="w-4 h-4 text-emerald-400" />
                  <span>Issue #1895 Resolution: Sandbox Active by Default</span>
                </div>
                <p className="text-emerald-300/90 text-xs">
                  All LLM-generated and user-submitted code is isolated in a restricted execution sandbox with zero host OS access.
                </p>
              </div>

              <div className="space-y-3 pt-1">
                <h4 className="font-bold text-stone-100 text-xs uppercase tracking-wider">
                  Enforced Security Controls
                </h4>

                <div className="space-y-2 text-xs">
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-stone-100">Restricted __builtins__ Allowlist:</span>
                      <p className="text-stone-400 mt-0.5">
                        Dynamic injection like <code className="bg-[#18202d] px-1 py-0.5 rounded text-rose-300 font-mono">__import__('os').system(...)</code>, <code className="bg-[#18202d] px-1 py-0.5 rounded text-rose-300 font-mono">eval()</code>, <code className="bg-[#18202d] px-1 py-0.5 rounded text-rose-300 font-mono">exec()</code>, and <code className="bg-[#18202d] px-1 py-0.5 rounded text-rose-300 font-mono">open()</code> are completely removed from runtime.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-stone-100">AST-Level Syntax Validation:</span>
                      <p className="text-stone-400 mt-0.5">
                        Abstract syntax tree inspection blocks all unauthorized library imports (<code className="bg-[#18202d] px-1 py-0.5 rounded text-stone-300 font-mono">os</code>, <code className="bg-[#18202d] px-1 py-0.5 rounded text-stone-300 font-mono">sys</code>, <code className="bg-[#18202d] px-1 py-0.5 rounded text-stone-300 font-mono">subprocess</code>) and dunder traversal methods (<code className="bg-[#18202d] px-1 py-0.5 rounded text-stone-300 font-mono">__subclasses__</code>).
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-stone-100">Indirect Prompt Injection Mitigation:</span>
                      <p className="text-stone-400 mt-0.5">
                        Untrusted data in ingested CSV columns or records cannot steer code execution toward malicious system commands; generated snippets are validated before execution and fail closed.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-[#232c3a] flex justify-end">
                <button
                  onClick={() => setShowSecurityModal(false)}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-stone-900 text-xs font-semibold rounded-xl transition-colors cursor-pointer"
                >
                  Close Security Overview
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
