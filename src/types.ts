export interface ColumnStats {
  name: string;
  type: 'numeric' | 'string' | 'boolean' | 'date';
  nullCount: number;
  distinctCount: number;
  min?: number | string;
  max?: number | string;
  mean?: number;
  median?: number;
  sampleValues: (string | number | boolean | null)[];
}

export interface DatasetSummary {
  id: string;
  name: string;
  description: string;
  rowCount: number;
  columnCount: number;
  columns: ColumnStats[];
  sampleRows: Record<string, any>[];
  suggestedPrompts: string[];
}

export type ResponseType = 'string' | 'number' | 'dataframe' | 'chart' | 'error';

export interface ChartConfig {
  chartType: 'bar' | 'line' | 'pie' | 'scatter' | 'histogram';
  title?: string;
  xKey: string;
  yKey?: string;
  series?: string[];
  data: Record<string, any>[];
}

export interface QueryResult {
  id: string;
  query: string;
  type: ResponseType;
  answer: string;
  codeSnippet?: string;
  chart?: ChartConfig;
  dataframe?: {
    columns: string[];
    rows: Record<string, any>[];
    totalRows: number;
  };
  error?: string;
  executionTimeMs: number;
  timestamp: string;
  engine?: 'gemini' | 'local';
  modelName?: string;
  securityCheck?: {
    isSafe: boolean;
    violations: string[];
    sandboxProtected: boolean;
    policy: string;
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  result?: QueryResult;
}
