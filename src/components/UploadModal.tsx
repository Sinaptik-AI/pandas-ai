import React, { useState } from 'react';
import { X, Upload, FileText, AlertCircle } from 'lucide-react';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newDatasetId: string) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [csvContent, setCsvContent] = useState('');
  const [fileName, setFileName] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleFileUpload = (file: File) => {
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.txt')) {
      setError('Please select a valid .csv file');
      return;
    }
    setFileName(file.name);
    if (!name) {
      setName(file.name.replace(/\.[^/.]+$/, ''));
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setCsvContent(text);
      setError('');
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvContent.trim()) {
      setError('Please select a CSV file or paste CSV content');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const res = await fetch('/api/datasets/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim() || 'Custom Dataset',
          description: description.trim() || 'Uploaded CSV dataset',
          csvContent,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to upload dataset');
      }

      const created = await res.json();
      onSuccess(created.id);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to process dataset');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs">
      <div className="bg-[#121620] rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-[#273346]">
        <div className="flex items-center justify-between pb-4 border-b border-[#232c3a]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
              <Upload className="w-4 h-4" />
            </div>
            <h3 className="text-base font-bold text-stone-100">Upload Dataset</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-stone-800 text-stone-400 hover:text-stone-200 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-rose-950/60 border border-rose-800/80 rounded-xl flex items-center gap-2 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4 text-xs">
          <div>
            <label className="block font-medium text-stone-300 mb-1.5">Dataset Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Q3 Sales Records"
              className="w-full bg-[#18202d] border border-[#293649] rounded-xl px-3.5 py-2.5 text-stone-100 focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-400 placeholder:text-stone-500"
            />
          </div>

          <div>
            <label className="block font-medium text-stone-300 mb-1.5">Description (Optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Sales numbers and customer acquisition costs"
              className="w-full bg-[#18202d] border border-[#293649] rounded-xl px-3.5 py-2.5 text-stone-100 focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-400 placeholder:text-stone-500"
            />
          </div>

          {/* Drag and Drop Zone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="border-2 border-dashed border-[#293649] hover:border-amber-500/60 bg-[#161c26] hover:bg-[#1c2432] rounded-2xl p-6 text-center cursor-pointer transition-colors"
            onClick={() => document.getElementById('file-upload-input')?.click()}
          >
            <input
              id="file-upload-input"
              type="file"
              accept=".csv,.txt"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
            <FileText className="w-8 h-8 text-stone-400 mx-auto mb-2" />
            <p className="font-semibold text-stone-200">
              {fileName ? fileName : 'Drop your CSV file here, or click to browse'}
            </p>
            <p className="text-stone-400 text-[11px] mt-1">Supports standard CSV files with headers</p>
          </div>

          {/* Fallback raw CSV text area */}
          <div>
            <label className="block font-medium text-stone-300 mb-1.5">Or paste CSV content:</label>
            <textarea
              rows={3}
              value={csvContent}
              onChange={(e) => {
                setCsvContent(e.target.value);
                setFileName('');
              }}
              placeholder="id,name,value\n1,Alpha,42\n2,Beta,99"
              className="w-full font-mono text-[11px] bg-[#18202d] border border-[#293649] rounded-xl p-2.5 text-stone-100 focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-400 placeholder:text-stone-500"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#232c3a]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-[#293649] text-stone-300 hover:bg-[#18202d] font-medium cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-stone-950 font-bold cursor-pointer shadow-sm transition-colors"
            >
              {isSubmitting ? 'Loading...' : 'Ingest Dataset'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
