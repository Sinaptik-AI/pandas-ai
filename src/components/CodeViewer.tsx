import React, { useState } from 'react';
import { Terminal, Copy, Check, ChevronDown, ChevronUp, Play, ShieldAlert, ShieldCheck, RefreshCw, AlertTriangle } from 'lucide-react';

interface CodeViewerProps {
  code: string;
  defaultExpanded?: boolean;
  datasetId?: string;
  securityCheck?: {
    isSafe: boolean;
    violations: string[];
    sandboxProtected: boolean;
    policy: string;
  };
}

export const CodeViewer: React.FC<CodeViewerProps> = ({
  code,
  defaultExpanded = false,
  datasetId,
  securityCheck,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [copied, setCopied] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [runResult, setRunResult] = useState<{
    status: string;
    output?: string;
    violations?: string[];
    message?: string;
    executionTimeMs?: number;
  } | null>(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRunInSandbox = async (codeToRun: string = code) => {
    setIsRunning(true);
    setExpanded(true);
    try {
      const res = await fetch('/api/sandbox/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: codeToRun, datasetId }),
      });
      const data = await res.json();
      setRunResult(data);
    } catch (err: any) {
      setRunResult({
        status: 'error',
        message: err.message || 'Failed to communicate with sandbox service',
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleTestAttackMitigation = () => {
    const maliciousPayload = `import os\n# Indirect Prompt Injection attack payload\nprint("Attempting OS command execution...")\nos.system("whoami")`;
    handleRunInSandbox(maliciousPayload);
  };

  const isBlocked = securityCheck && !securityCheck.isSafe;

  return (
    <div className="mt-3 border border-[#232c3a] rounded-xl overflow-hidden bg-[#0d1117] text-stone-100 text-xs shadow-md">
      {/* Top Bar */}
      <div className="flex flex-wrap items-center justify-between px-3.5 py-2.5 bg-[#121720] border-b border-[#232c3a] gap-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1.5 text-stone-300 hover:text-white transition-colors cursor-pointer text-left font-mono"
          >
            <Terminal className="w-3.5 h-3.5 text-amber-400" />
            <span className="font-semibold text-[11px] uppercase tracking-wider text-stone-300">
              PandasAI Python Script
            </span>
            {expanded ? <ChevronUp className="w-3 h-3 text-stone-400" /> : <ChevronDown className="w-3 h-3 text-stone-400" />}
          </button>

          {/* Sandbox Security Badge */}
          <div
            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium border ${
              isBlocked
                ? 'bg-rose-950/80 text-rose-300 border-rose-800'
                : 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
            }`}
            title="Default execution sandbox with restricted __builtins__ and AST validation active"
          >
            {isBlocked ? (
              <>
                <ShieldAlert className="w-3 h-3 text-rose-400" />
                <span>Sandbox Blocked</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                <span>Sandbox Protected</span>
              </>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => handleRunInSandbox()}
            disabled={isRunning}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 hover:text-amber-200 border border-amber-500/30 text-[11px] font-medium transition-colors cursor-pointer disabled:opacity-50"
            title="Execute within default sandbox environment"
          >
            {isRunning ? (
              <RefreshCw className="w-3 h-3 animate-spin" />
            ) : (
              <Play className="w-3 h-3" />
            )}
            <span>Run in Sandbox</span>
          </button>

          <button
            onClick={handleTestAttackMitigation}
            disabled={isRunning}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-rose-950/80 hover:bg-rose-900/90 text-rose-300 border border-rose-800 text-[11px] font-medium transition-colors cursor-pointer disabled:opacity-50"
            title="Test Issue #1895 mitigation: attempts os.system('whoami') in sandbox"
          >
            <AlertTriangle className="w-3 h-3 text-rose-400" />
            <span>Test Attack Defense</span>
          </button>

          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1 px-2 py-1 rounded hover:bg-stone-800 text-stone-400 hover:text-white transition-colors cursor-pointer text-[11px]"
            title="Copy code snippet"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-emerald-400" />
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Code Display */}
      {expanded && (
        <div className="relative">
          <pre className="p-3.5 overflow-x-auto text-amber-200/90 font-mono text-[11px] leading-relaxed selection:bg-amber-500/30 border-b border-[#232c3a] bg-[#090c12]">
            <code>{code}</code>
          </pre>

          {/* Sandbox Execution Terminal Output */}
          {runResult && (
            <div className="p-3 bg-black/85 border-t border-[#232c3a] font-mono text-[11px]">
              <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-stone-800/80">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span className="text-stone-400 font-semibold uppercase text-[10px]">
                    Sandbox Terminal (Default Safe Builtins)
                  </span>
                </div>
                {runResult.executionTimeMs !== undefined && (
                  <span className="text-stone-500 text-[10px]">
                    {runResult.executionTimeMs}ms
                  </span>
                )}
              </div>

              {runResult.status === 'blocked' ? (
                <div className="p-2.5 rounded bg-rose-950/60 border border-rose-800/80 text-rose-300 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-rose-200">
                    <ShieldAlert className="w-4 h-4 text-rose-400" />
                    <span>RCE Attack Blocked (Issue #1895 Remediation Active)</span>
                  </div>
                  <p className="text-[10px] text-rose-300/90 leading-tight">
                    {runResult.message || 'Execution was rejected by the AST and restricted builtins allowlist.'}
                  </p>
                  {runResult.violations && runResult.violations.length > 0 && (
                    <ul className="list-disc list-inside text-[10px] text-rose-200/90 pt-1 space-y-0.5">
                      {runResult.violations.map((v, i) => (
                        <li key={i}>{v}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : runResult.status === 'runtime_error' || runResult.status === 'timeout' ? (
                <div className="text-amber-400 p-2 rounded bg-amber-950/30 border border-amber-900/50">
                  <div className="font-semibold text-amber-300">Sandbox Notice:</div>
                  <div>{runResult.message || 'Execution aborted.'}</div>
                </div>
              ) : (
                <div className="text-emerald-400 whitespace-pre-wrap leading-tight">
                  {runResult.output || 'Execution finished with 0 errors in sandbox.'}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
