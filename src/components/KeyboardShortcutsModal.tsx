import React from 'react';
import { Keyboard, X } from 'lucide-react';

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const KeyboardShortcutsModal: React.FC<KeyboardShortcutsModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const isMac = typeof window !== 'undefined' && /Mac|iPod|iPhone|iPad/.test(navigator.platform);
  const modKey = isMac ? '⌘' : 'Ctrl';

  const shortcuts = [
    {
      category: 'Chat & Querying',
      items: [
        {
          keys: [`${modKey}`, 'Enter'],
          description: 'Send current message / execute analytics query',
        },
        {
          keys: [`${modKey}`, 'E'],
          description: 'Open conversation & data export menu',
        },
      ],
    },
    {
      category: 'Dataset Navigation',
      items: [
        {
          keys: [`${modKey}`, 'K'],
          description: 'Open dataset switcher command palette',
        },
        {
          keys: ['↑', '↓'],
          description: 'Navigate datasets in command palette',
        },
        {
          keys: ['Enter'],
          description: 'Confirm and switch to highlighted dataset',
        },
        {
          keys: [`${modKey}`, 'U'],
          description: 'Upload new CSV dataset',
        },
      ],
    },
    {
      category: 'Views & Tabs',
      items: [
        {
          keys: [`${modKey}`, '1'],
          description: 'Switch to AI Chat view',
        },
        {
          keys: [`${modKey}`, '2'],
          description: 'Switch to Data Explorer table view',
        },
        {
          keys: [`${modKey}`, '3'],
          description: 'Switch to Schema & Stats view',
        },
      ],
    },
    {
      category: 'Column & Space Management',
      items: [
        {
          keys: ['Header', '⌃ / ✕'],
          description: 'Compress, expand, or remove dataset header in Chat view',
        },
        {
          keys: ['Col Header', '⤢ / ✕'],
          description: 'Compress / expand column width or remove column from table',
        },
        {
          keys: ['# Col'],
          description: 'Show / hide row index number column',
        },
      ],
    },
    {
      category: 'General',
      items: [
        {
          keys: ['?'],
          description: 'Show keyboard shortcuts guide',
        },
        {
          keys: ['Esc'],
          description: 'Close active dialog, palette, or menu',
        },
      ],
    },
  ];

  return (
    <div
      className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-100"
      onClick={onClose}
    >
      <div
        className="bg-[#121620] rounded-2xl max-w-lg w-full border border-[#273346] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-5 py-4 bg-[#0a0d14] text-white flex items-center justify-between border-b border-[#232c3a]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
              <Keyboard className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold tracking-tight">Keyboard Shortcuts</h3>
              <p className="text-[11px] text-stone-400">Power-user navigation & workflow accelerators</p>
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
        <div className="p-5 max-h-[70vh] overflow-y-auto space-y-4 divide-y divide-[#1f2735]">
          {shortcuts.map((section, sIdx) => (
            <div key={section.category} className={sIdx > 0 ? 'pt-3' : ''}>
              <h4 className="text-[11px] font-bold text-amber-400/90 uppercase tracking-wider mb-2.5">
                {section.category}
              </h4>
              <div className="space-y-2">
                {section.items.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between text-xs py-1"
                  >
                    <span className="text-stone-300">{item.description}</span>
                    <div className="flex items-center gap-1">
                      {item.keys.map((k, kIdx) => (
                        <kbd
                          key={kIdx}
                          className="px-2 py-0.5 rounded bg-[#18202d] border border-[#293649] font-mono text-[11px] font-medium text-stone-200 shadow-2xs"
                        >
                          {k}
                        </kbd>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 bg-[#0a0d14] border-t border-[#232c3a] flex justify-between items-center text-xs text-stone-400">
          <span>Press <kbd className="px-1.5 py-0.5 bg-[#161c26] border border-[#2a364a] rounded font-mono text-[10px] text-stone-300">Esc</kbd> anytime to close</span>
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-600 text-stone-950 font-bold rounded-lg cursor-pointer transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};
