import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ChatQueryView } from './components/ChatQueryView';
import { DataExplorerView } from './components/DataExplorerView';
import { SchemaView } from './components/SchemaView';
import { UploadModal } from './components/UploadModal';
import { DatasetSwitcherModal } from './components/DatasetSwitcherModal';
import { KeyboardShortcutsModal } from './components/KeyboardShortcutsModal';
import { DatasetSummary, ChatMessage, QueryResult } from './types';
import { AlertCircle } from 'lucide-react';

const STORAGE_KEY_CHAT_HISTORY = 'pandasai_chat_history_v1';
const STORAGE_KEY_CURRENT_DATASET = 'pandasai_current_dataset_id_v1';

export default function App() {
  const [datasets, setDatasets] = useState<{ id: string; name: string; rowCount: number; columnCount: number }[]>([]);
  const [currentDatasetId, setCurrentDatasetId] = useState<string>(() => {
    try {
      return localStorage.getItem(STORAGE_KEY_CURRENT_DATASET) || 'heart';
    } catch {
      return 'heart';
    }
  });
  const [currentDataset, setCurrentDataset] = useState<DatasetSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'table' | 'schema'>('chat');

  // Load persisted chat message history across page reloads for each dataset
  const [messagesByDataset, setMessagesByDataset] = useState<Record<string, ChatMessage[]>>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_CHAT_HISTORY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && typeof parsed === 'object') {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to load chat history from localStorage:', e);
    }
    return {};
  });

  const [isLoadingQuery, setIsLoadingQuery] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isDatasetSwitcherOpen, setIsDatasetSwitcherOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Sync chat message history across page reloads
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_CHAT_HISTORY, JSON.stringify(messagesByDataset));
    } catch (e) {
      console.warn('Failed to persist chat history to localStorage:', e);
    }
  }, [messagesByDataset]);

  // Initial load
  useEffect(() => {
    const init = async () => {
      try {
        setInitialLoading(true);
        // Check health
        const healthRes = await fetch('/api/health');
        if (healthRes.ok) {
          const healthData = await healthRes.json();
          setHasGeminiKey(Boolean(healthData.hasGeminiKey));
        }

        // Fetch datasets
        const dsRes = await fetch('/api/datasets');
        if (dsRes.ok) {
          const dsList = await dsRes.json();
          setDatasets(dsList);
          if (dsList.length > 0) {
            let targetId = currentDatasetId;
            // Verify if stored dataset ID exists in list, otherwise default to first
            if (!dsList.some((d: any) => d.id === targetId)) {
              targetId = dsList[0].id;
              setCurrentDatasetId(targetId);
            }
            await loadDataset(targetId);
          }
        }
      } catch (err: any) {
        console.error('Initialization failed:', err);
        setErrorMsg('Failed to connect to backend server. Retrying...');
      } finally {
        setInitialLoading(false);
      }
    };

    init();
  }, []);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMod = e.metaKey || e.ctrlKey;
      const target = e.target as HTMLElement;
      const isTyping =
        target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable);

      // Cmd/Ctrl + K: Toggle Dataset Switcher
      if (isMod && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        setIsDatasetSwitcherOpen((prev) => !prev);
        return;
      }

      // Cmd/Ctrl + Enter: Send message in chat view
      if (isMod && e.key === 'Enter') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('trigger-send-message'));
        return;
      }

      // Cmd/Ctrl + U: Open Upload Modal
      if (isMod && (e.key === 'u' || e.key === 'U')) {
        e.preventDefault();
        setIsUploadOpen(true);
        return;
      }

      // Cmd/Ctrl + 1: Switch to Chat
      if (isMod && e.key === '1') {
        e.preventDefault();
        setActiveTab('chat');
        return;
      }

      // Cmd/Ctrl + 2: Switch to Explorer
      if (isMod && e.key === '2') {
        e.preventDefault();
        setActiveTab('table');
        return;
      }

      // Cmd/Ctrl + 3: Switch to Schema
      if (isMod && e.key === '3') {
        e.preventDefault();
        setActiveTab('schema');
        return;
      }

      // Cmd/Ctrl + /: Keyboard Shortcuts Help
      if (isMod && e.key === '/') {
        e.preventDefault();
        setIsShortcutsOpen((prev) => !prev);
        return;
      }

      // ? key (when not typing inside an input/textarea): Keyboard Shortcuts Help
      if (!isTyping && e.key === '?') {
        e.preventDefault();
        setIsShortcutsOpen((prev) => !prev);
        return;
      }

      // Escape: Close modals
      if (e.key === 'Escape') {
        if (isDatasetSwitcherOpen) setIsDatasetSwitcherOpen(false);
        if (isShortcutsOpen) setIsShortcutsOpen(false);
        if (isUploadOpen) setIsUploadOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isDatasetSwitcherOpen, isShortcutsOpen, isUploadOpen]);

  const loadDataset = async (id: string) => {
    try {
      setErrorMsg(null);
      const res = await fetch(`/api/datasets/${id}`);
      if (res.ok) {
        const data: DatasetSummary = await res.json();
        setCurrentDataset(data);
      } else {
        setErrorMsg('Failed to load dataset metadata');
      }
    } catch (err: any) {
      console.error('Failed to load dataset:', err);
      setErrorMsg('Error loading dataset');
    }
  };

  const handleSelectDataset = (id: string) => {
    setCurrentDatasetId(id);
    try {
      localStorage.setItem(STORAGE_KEY_CURRENT_DATASET, id);
    } catch (e) {
      console.warn('Failed to save current dataset to localStorage:', e);
    }
    loadDataset(id);
  };

  const handleClearChatHistory = () => {
    if (!currentDataset) return;
    setMessagesByDataset((prev) => {
      const next = { ...prev };
      delete next[currentDataset.id];
      return next;
    });
  };

  const handleSendQuery = async (queryText: string) => {
    if (!currentDataset) return;

    const userMessage: ChatMessage = {
      id: 'msg_' + Date.now().toString(36) + '_u',
      role: 'user',
      content: queryText,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessagesByDataset((prev) => ({
      ...prev,
      [currentDataset.id]: [...(prev[currentDataset.id] || []), userMessage],
    }));

    setIsLoadingQuery(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          datasetId: currentDataset.id,
          query: queryText,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Query processing failed');
      }

      const result: QueryResult = await res.json();

      const assistantMessage: ChatMessage = {
        id: 'msg_' + Date.now().toString(36) + '_a',
        role: 'assistant',
        content: result.answer,
        timestamp: result.timestamp || new Date().toLocaleTimeString(),
        result,
      };

      setMessagesByDataset((prev) => ({
        ...prev,
        [currentDataset.id]: [...(prev[currentDataset.id] || []), assistantMessage],
      }));
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: 'msg_' + Date.now().toString(36) + '_err',
        role: 'assistant',
        content: `Error: ${err.message || 'Unable to process query at this time.'}`,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessagesByDataset((prev) => ({
        ...prev,
        [currentDataset.id]: [...(prev[currentDataset.id] || []), errorMessage],
      }));
    } finally {
      setIsLoadingQuery(false);
    }
  };

  const handleUploadSuccess = async (newDatasetId: string) => {
    const dsRes = await fetch('/api/datasets');
    if (dsRes.ok) {
      const dsList = await dsRes.json();
      setDatasets(dsList);
      handleSelectDataset(newDatasetId);
      setActiveTab('chat');
    }
  };

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-[#0c0f16] flex items-center justify-center">
        <div className="text-center space-y-3 bg-[#131822] border border-[#232c3a] p-8 rounded-2xl shadow-xl max-w-sm w-full mx-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-2xl flex items-center justify-center mx-auto animate-pulse">
            🐼
          </div>
          <h2 className="text-sm font-semibold text-stone-100">Starting PandasAI Studio...</h2>
          <p className="text-xs text-stone-400">Initializing Gemini AI analytics engine & sandbox repositories</p>
        </div>
      </div>
    );
  }

  const currentMessages = (currentDataset ? messagesByDataset[currentDataset.id] : []) || [];

  return (
    <div className="min-h-screen bg-[#0c0f16] text-stone-100 flex flex-col selection:bg-amber-500 selection:text-stone-900">
      {/* Navbar */}
      <Navbar
        datasets={datasets}
        currentDatasetId={currentDatasetId}
        onSelectDataset={handleSelectDataset}
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenDatasetSwitcher={() => setIsDatasetSwitcherOpen(true)}
        onOpenShortcuts={() => setIsShortcutsOpen(true)}
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        hasGeminiKey={hasGeminiKey}
      />

      {errorMsg && (
        <div className="max-w-7xl mx-auto w-full px-4 pt-3">
          <div className="p-3 bg-amber-950/40 border border-amber-800/80 text-amber-200 rounded-xl text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              <span>{errorMsg}</span>
            </div>
            <button
              onClick={() => loadDataset(currentDatasetId)}
              className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 rounded-lg font-medium cursor-pointer transition-colors border border-amber-500/30"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1">
        {currentDataset ? (
          <>
            {activeTab === 'chat' && (
              <ChatQueryView
                dataset={currentDataset}
                messages={currentMessages}
                isLoading={isLoadingQuery}
                onSendQuery={handleSendQuery}
                onClearHistory={handleClearChatHistory}
              />
            )}
            {activeTab === 'table' && <DataExplorerView dataset={currentDataset} />}
            {activeTab === 'schema' && <SchemaView dataset={currentDataset} />}
          </>
        ) : (
          <div className="h-96 flex items-center justify-center text-stone-500 text-xs">
            No dataset currently selected
          </div>
        )}
      </main>

      {/* Upload CSV Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onSuccess={handleUploadSuccess}
      />

      {/* Dataset Switcher Command Palette (Cmd/Ctrl + K) */}
      <DatasetSwitcherModal
        isOpen={isDatasetSwitcherOpen}
        onClose={() => setIsDatasetSwitcherOpen(false)}
        datasets={datasets}
        currentDatasetId={currentDatasetId}
        onSelectDataset={handleSelectDataset}
        onOpenUpload={() => setIsUploadOpen(true)}
      />

      {/* Keyboard Shortcuts Cheat Sheet (? or Cmd/Ctrl + /) */}
      <KeyboardShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />
    </div>
  );
}
