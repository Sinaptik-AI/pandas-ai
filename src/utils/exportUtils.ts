import { ChatMessage, DatasetSummary, QueryResult } from '../types';

/**
 * Escapes a cell value for standard RFC4180 CSV compliance.
 */
export function escapeCsvCell(cell: any): string {
  if (cell === null || cell === undefined) {
    return '';
  }
  let str: string;
  if (typeof cell === 'object') {
    try {
      str = JSON.stringify(cell);
    } catch {
      str = String(cell);
    }
  } else {
    str = String(cell);
  }

  // If cell contains commas, double quotes, or newlines, quote it and escape internal quotes
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

/**
 * Converts column headers and row objects into a CSV string.
 */
export function convertRowsToCsv(columns: string[], rows: Record<string, any>[]): string {
  const header = columns.map(escapeCsvCell).join(',');
  const rowLines = rows.map((row) =>
    columns.map((col) => escapeCsvCell(row[col])).join(',')
  );
  return [header, ...rowLines].join('\r\n');
}

/**
 * Triggers a client-side browser download for a Blob.
 */
export function downloadBlob(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/**
 * Exports the active chat conversation history to a formatted JSON file.
 */
export function exportConversationToJson(dataset: DatasetSummary, messages: ChatMessage[]): void {
  const exportPayload = {
    exportedAt: new Date().toISOString(),
    dataset: {
      id: dataset.id,
      name: dataset.name,
      rowCount: dataset.rowCount,
      columnCount: dataset.columnCount,
    },
    totalMessages: messages.length,
    messages: messages.map((m) => ({
      id: m.id,
      role: m.role,
      timestamp: m.timestamp,
      content: m.content,
      result: m.result
        ? {
            query: m.result.query,
            type: m.result.type,
            executionTimeMs: m.result.executionTimeMs,
            codeSnippet: m.result.codeSnippet,
            securityCheck: m.result.securityCheck,
            chart: m.result.chart
              ? {
                  type: m.result.chart.chartType,
                  title: m.result.chart.title,
                  dataPointCount: m.result.chart.data?.length || 0,
                  data: m.result.chart.data,
                }
              : undefined,
            dataframe: m.result.dataframe
              ? {
                  totalRows: m.result.dataframe.totalRows,
                  columns: m.result.dataframe.columns,
                  rows: m.result.dataframe.rows,
                }
              : undefined,
          }
        : undefined,
    })),
  };

  const filename = `${dataset.id}_chat_${new Date().toISOString().slice(0, 10)}.json`;
  downloadBlob(JSON.stringify(exportPayload, null, 2), filename, 'application/json');
}

/**
 * Exports the active chat conversation history to a CSV table.
 */
export function exportConversationToCsv(dataset: DatasetSummary, messages: ChatMessage[]): void {
  const columns = [
    'Index',
    'Role',
    'Timestamp',
    'Content / Answer',
    'Result Type',
    'Execution Time (ms)',
    'Generated Code',
    'Sandbox Policy',
    'Violations',
  ];

  const rows = messages.map((m, idx) => ({
    Index: idx + 1,
    Role: m.role.toUpperCase(),
    Timestamp: m.timestamp,
    'Content / Answer': m.content,
    'Result Type': m.result?.type || (m.role === 'user' ? 'USER_QUERY' : 'N/A'),
    'Execution Time (ms)': m.result?.executionTimeMs ?? '',
    'Generated Code': m.result?.codeSnippet || '',
    'Sandbox Policy': m.result?.securityCheck?.policy || '',
    Violations: m.result?.securityCheck?.violations?.join('; ') || '',
  }));

  const csvContent = convertRowsToCsv(columns, rows);
  const filename = `${dataset.id}_chat_${new Date().toISOString().slice(0, 10)}.csv`;
  downloadBlob(csvContent, filename, 'text/csv;charset=utf-8;');
}

/**
 * Finds the latest exportable data result (dataframe or chart data) from messages,
 * or falls back to dataset sample rows.
 */
export function getLatestExportableData(
  messages: ChatMessage[],
  fallbackDataset?: DatasetSummary
): { title: string; columns: string[]; rows: Record<string, any>[] } | null {
  // Search backward from latest message
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg.result?.dataframe && msg.result.dataframe.rows?.length > 0) {
      return {
        title: msg.result.query ? `Result for: ${msg.result.query}` : 'Query Dataframe Result',
        columns: msg.result.dataframe.columns,
        rows: msg.result.dataframe.rows,
      };
    }
    if (msg.result?.chart && msg.result.chart.data?.length > 0) {
      const data = msg.result.chart.data;
      const columns = Object.keys(data[0] || {});
      return {
        title: msg.result.chart.title || (msg.result.query ? `Chart Data for: ${msg.result.query}` : 'Chart Data Result'),
        columns,
        rows: data,
      };
    }
  }

  // Fallback to sample rows if dataset provided
  if (fallbackDataset && fallbackDataset.sampleRows && fallbackDataset.sampleRows.length > 0) {
    const columns = fallbackDataset.columns.map((c) => c.name);
    return {
      title: `${fallbackDataset.name} Sample Data`,
      columns,
      rows: fallbackDataset.sampleRows,
    };
  }

  return null;
}

/**
 * Exports tabular data (dataframe or chart points) to CSV.
 */
export function exportDataToCsv(
  columns: string[],
  rows: Record<string, any>[],
  filenamePrefix: string
): void {
  const csvContent = convertRowsToCsv(columns, rows);
  const cleanPrefix = filenamePrefix.toLowerCase().replace(/[^a-z0-9_-]/g, '_');
  const filename = `${cleanPrefix}_${new Date().toISOString().slice(0, 10)}.csv`;
  downloadBlob(csvContent, filename, 'text/csv;charset=utf-8;');
}

/**
 * Exports tabular data (dataframe or chart points) to JSON.
 */
export function exportDataToJson(
  columns: string[],
  rows: Record<string, any>[],
  filenamePrefix: string,
  metadata?: Record<string, any>
): void {
  const payload = {
    exportedAt: new Date().toISOString(),
    totalRows: rows.length,
    columns,
    ...(metadata || {}),
    data: rows,
  };
  const cleanPrefix = filenamePrefix.toLowerCase().replace(/[^a-z0-9_-]/g, '_');
  const filename = `${cleanPrefix}_${new Date().toISOString().slice(0, 10)}.json`;
  downloadBlob(JSON.stringify(payload, null, 2), filename, 'application/json');
}
