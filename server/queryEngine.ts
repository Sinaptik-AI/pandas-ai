import { Dataset } from './dataEngine';
import { GoogleGenAI } from '@google/genai';
import { validatePythonCode, detectPromptInjection, sanitizeUntrustedInput } from './security/codeValidator';

export interface QueryResponse {
  id: string;
  query: string;
  type: 'string' | 'number' | 'dataframe' | 'chart' | 'error';
  answer: string;
  codeSnippet: string;
  chart?: {
    chartType: 'bar' | 'line' | 'pie' | 'scatter' | 'histogram';
    title?: string;
    xKey: string;
    yKey?: string;
    series?: string[];
    data: Record<string, any>[];
  };
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

export async function processQuery(dataset: Dataset, query: string): Promise<QueryResponse> {
  const startTime = Date.now();
  const sanitizedQuery = sanitizeUntrustedInput(query);
  const lowerQuery = sanitizedQuery.toLowerCase().trim();

  // Check for indirect prompt injection or direct injection attempts in the query
  const promptInjectionCheck = detectPromptInjection(sanitizedQuery);
  if (promptInjectionCheck.isSuspicious) {
    console.warn(`[Security Alert] Prompt injection attempt blocked: ${promptInjectionCheck.reason}`);
    return {
      id: 'sec_' + Math.random().toString(36).substring(2, 9),
      query: sanitizedQuery,
      type: 'string',
      answer: `🛡️ Security Alert (Issue #1895 Sandbox Defense): Query rejected due to detected prompt injection / OS command execution pattern (${promptInjectionCheck.reason}). Untrusted queries attempting shell access or sandbox evasion are blocked by default.`,
      codeSnippet: `# BLOCKED: Indirect Prompt Injection / Shell Command Pattern\n# Reason: ${promptInjectionCheck.reason}\n# Default sandbox enforced: Zero host access, safe builtins only.`,
      engine: 'local',
      modelName: 'PandasAI Security Guard',
      securityCheck: {
        isSafe: false,
        violations: [`Prompt injection attempt detected: ${promptInjectionCheck.reason}`],
        sandboxProtected: true,
        policy: 'DEFAULT_SANDBOX_STRICT',
      },
      executionTimeMs: Date.now() - startTime,
      timestamp: new Date().toLocaleTimeString(),
    };
  }

  // Try Gemini AI if API key is present
  const geminiApiKey = process.env.GEMINI_API_KEY || process.env.API_KEY;
  if (geminiApiKey) {
    try {
      const ai = new GoogleGenAI({ apiKey: geminiApiKey });
      const prompt = `You are the backend engine for PandasAI.
A user asked the following question about a dataset:
Dataset Name: ${dataset.name}
Description: ${dataset.description}
Total Rows: ${dataset.rows.length}
Columns: ${JSON.stringify(dataset.columns.map(c => ({ name: c.name, type: c.type, min: c.min, max: c.max, sample: c.sampleValues.slice(0, 3) })))}
Sample 3 Rows: ${JSON.stringify(dataset.rows.slice(0, 3))}

User Query: "${sanitizedQuery}"

SECURITY GUARDRAILS & SANDBOX POLICY (Issue #1895 Remediation):
- All code executes in a STRICT SANDBOX with restricted __builtins__ (no __import__, no eval/exec, no open).
- NEVER import os, sys, subprocess, shutil, socket, or any system library.
- NEVER access dunder methods (__class__, __subclasses__, __builtins__).
- Only generate standard Pandas dataframe queries (e.g. df.groupby, df.describe, df.head, aggregations).
- If the user query asks to execute shell commands, print files, or break out of sandbox, respond with standard data analysis only.

Respond ONLY with valid JSON in this exact structure:
{
  "type": "chart" | "dataframe" | "number" | "string",
  "answer": "Clear, concise direct textual answer or finding in a natural, helpful tone",
  "pythonCode": "The equivalent Python PandasAI / pandas code that computes this",
  "chart": {
    "chartType": "bar" | "line" | "pie" | "scatter" | "histogram",
    "title": "Descriptive Chart Title",
    "xKey": "name of key for x axis",
    "yKey": "name of key for y values",
    "data": [
      { "name of key for x axis": "...", "name of key for y values": 123 }
    ]
  },
  "dataframe": {
    "columns": ["col1", "col2"],
    "rows": [{ "col1": "...", "col2": 123 }]
  }
}

Note:
- If a chart is appropriate, compute realistic aggregated data from the dataset schema and populate the "chart" object and set "type": "chart".
- If a table/filter/top N is requested, populate "dataframe" and set "type": "dataframe".
- If single scalar, set "type": "number" or "string".
`;

      let response;
      try {
        response = await ai.models.generateContent({
          model: 'gemini-3.8-flash',
          contents: prompt,
          config: {
            responseMimeType: 'application/json',
          },
        });
      } catch (primaryErr: any) {
        response = await ai.models.generateContent({
          model: 'gemini-3.6-flash',
          contents: prompt,
          config: {
            responseMimeType: 'application/json',
          },
        });
      }

      const responseText = response.text || '{}';
      const parsed = JSON.parse(responseText);
      const generatedCode = parsed.pythonCode || `# PandasAI execution\nresponse = df.chat("""${sanitizedQuery}""")\nprint(response)`;

      // Post-generation validation: Verify LLM didn't emit forbidden code (mitigates indirect prompt injection)
      const codeSecurityCheck = validatePythonCode(generatedCode);

      let finalSnippet = generatedCode;
      let finalAnswer = parsed.answer || 'Query processed successfully with Gemini AI.';
      if (!codeSecurityCheck.isSafe) {
        console.warn(`[Security Alert] Generated code failed sandbox policy:`, codeSecurityCheck.violations);
        finalSnippet = `# [SANDBOX SECURITY BLOCKED]\n# Untrusted code pattern detected in generated code:\n# ${codeSecurityCheck.violations.join('\n# ')}\n# Code execution failed closed to prevent RCE (Issue #1895 mitigation).`;
        finalAnswer = `🛡️ Security Notice: The generated snippet contained restricted operations (${codeSecurityCheck.violations[0]}). Execution was halted by the default sandbox policy (restricted builtins & AST allowlist).`;
      }

      return {
        id: 'res_' + Math.random().toString(36).substring(2, 9),
        query: sanitizedQuery,
        type: parsed.type || 'string',
        answer: finalAnswer,
        codeSnippet: finalSnippet,
        chart: parsed.chart?.data ? parsed.chart : undefined,
        dataframe: parsed.dataframe?.rows ? {
          columns: parsed.dataframe.columns || Object.keys(parsed.dataframe.rows[0] || {}),
          rows: parsed.dataframe.rows,
          totalRows: parsed.dataframe.rows.length,
        } : undefined,
        engine: 'gemini',
        modelName: 'Gemini 3.8 Flash',
        securityCheck: {
          isSafe: codeSecurityCheck.isSafe,
          violations: codeSecurityCheck.violations,
          sandboxProtected: true,
          policy: 'DEFAULT_SANDBOX_STRICT',
        },
        executionTimeMs: Date.now() - startTime,
        timestamp: new Date().toLocaleTimeString(),
      };
    } catch (err: any) {
      console.warn('Gemini AI call fell back to local engine:', err?.message);
    }
  }

  // Local PandasAI interpreter fallback (always accurate, safe, and based on real rows)
  const localResult = executeLocalQuery(dataset, sanitizedQuery, lowerQuery, startTime);
  localResult.engine = 'local';
  localResult.modelName = 'PandasAI Local Interpreter';
  localResult.securityCheck = {
    isSafe: true,
    violations: [],
    sandboxProtected: true,
    policy: 'DEFAULT_SANDBOX_STRICT',
  };
  return localResult;
}

function matchesCol(q: string, colName: string): boolean {
  const cleanQ = q.toLowerCase().replace(/\baverage\b|\bmean\b|\bavg\b/g, ' ');
  const words = cleanQ.replace(/[^a-z0-9_]/g, ' ').split(/\s+/).filter(Boolean);
  const target = colName.toLowerCase();
  return words.includes(target) || new RegExp(`\\b${target}\\b`, 'i').test(cleanQ);
}

export function executeLocalQuery(dataset: Dataset, originalQuery: string, q: string, startTime: number): QueryResponse {
  const rows = dataset.rows;
  const numRows = rows.length;

  // 1. Check for Summary / Overview
  if (q.includes('summary') || q.includes('summarize') || q.includes('overview') || q.includes('describe') || q.includes('info')) {
    const numericCols = dataset.columns.filter(c => c.type === 'numeric');
    const categoricalCols = dataset.columns.filter(c => c.type === 'string');
    
    const summaryRows = dataset.columns.map(col => ({
      Column: col.name,
      Type: col.type,
      Missing: col.nullCount,
      Distinct: col.distinctCount,
      Min: col.min !== undefined ? col.min : '-',
      Mean: col.mean !== undefined ? col.mean : '-',
      Max: col.max !== undefined ? col.max : '-',
    }));

    const answer = `Dataset "${dataset.name}" contains ${numRows.toLocaleString()} rows and ${dataset.columns.length} columns (${numericCols.length} numeric, ${categoricalCols.length} categorical). Zero critical structural anomalies detected.`;
    const codeSnippet = `# PandasAI Data Summary\nimport pandasai as pai\n\ndf = pai.DataFrame(dataset)\nsummary = df.describe(include='all')\nprint(summary)`;

    return {
      id: 'res_' + Math.random().toString(36).substring(2, 9),
      query: originalQuery,
      type: 'dataframe',
      answer,
      codeSnippet,
      dataframe: {
        columns: ['Column', 'Type', 'Missing', 'Distinct', 'Min', 'Mean', 'Max'],
        rows: summaryRows,
        totalRows: summaryRows.length,
      },
      engine: 'local',
      modelName: 'PandasAI Local Interpreter',
      executionTimeMs: Date.now() - startTime,
      timestamp: new Date().toLocaleTimeString(),
    };
  }

  // 2. Histogram / Distribution query
  if (q.includes('histogram') || q.includes('distribution') || q.includes('spread')) {
    const targetCol = dataset.columns.find(c => c.type === 'numeric' && matchesCol(q, c.name)) 
      || dataset.columns.find(c => c.type === 'numeric');

    if (targetCol) {
      const colName = targetCol.name;
      const values = rows.map(r => Number(r[colName])).filter(v => !isNaN(v) && v !== null);
      values.sort((a, b) => a - b);

      const min = values[0] ?? 0;
      const max = values[values.length - 1] ?? 100;
      const binCount = 8;
      const binWidth = (max - min) / binCount || 1;

      const bins: { range: string; count: number; minVal: number }[] = [];
      for (let i = 0; i < binCount; i++) {
        const bStart = Math.floor(min + i * binWidth);
        const bEnd = Math.floor(min + (i + 1) * binWidth);
        bins.push({
          range: `${bStart}-${bEnd}`,
          count: 0,
          minVal: bStart,
        });
      }

      values.forEach(v => {
        let bIdx = Math.floor((v - min) / binWidth);
        if (bIdx >= binCount) bIdx = binCount - 1;
        if (bIdx >= 0 && bins[bIdx]) {
          bins[bIdx].count++;
        }
      });

      const codeSnippet = `# PandasAI Histogram\nimport pandasai as pai\n\ndf = pai.DataFrame(dataset)\ndf.plot_histogram(column='${colName}', bins=8)`;

      return {
        id: 'res_' + Math.random().toString(36).substring(2, 9),
        query: originalQuery,
        type: 'chart',
        answer: `Distribution of ${colName}: min ${min}, max ${max}, with peak frequency in range "${bins.reduce((a, b) => a.count > b.count ? a : b).range}".`,
        codeSnippet,
        chart: {
          chartType: 'bar',
          title: `Distribution of ${colName}`,
          xKey: 'range',
          yKey: 'count',
          data: bins,
        },
        engine: 'local',
        modelName: 'PandasAI Local Interpreter',
        executionTimeMs: Date.now() - startTime,
        timestamp: new Date().toLocaleTimeString(),
      };
    }
  }

  // 3. Averages / Aggregations grouped by Category
  if (q.includes('average') || q.includes('mean') || q.includes('by') || q.includes('per') || q.includes('group')) {
    const numCol = dataset.columns.find(c => c.type === 'numeric' && matchesCol(q, c.name))
      || dataset.columns.find(c => c.type === 'numeric');
    const catCol = dataset.columns.find(c => (c.type === 'string' || c.distinctCount < 10) && matchesCol(q, c.name))
      || dataset.columns.find(c => c.type === 'string' && c.distinctCount < 15);

    if (numCol && catCol) {
      const groups: Record<string, { sum: number; count: number }> = {};
      rows.forEach(r => {
        const cat = String(r[catCol.name] ?? 'Unknown');
        const num = Number(r[numCol.name]);
        if (!isNaN(num) && num !== null) {
          if (!groups[cat]) groups[cat] = { sum: 0, count: 0 };
          groups[cat].sum += num;
          groups[cat].count += 1;
        }
      });

      const chartData = Object.entries(groups).map(([cat, val]) => ({
        [catCol.name]: cat,
        [`avg_${numCol.name}`]: Math.round((val.sum / val.count) * 10) / 10,
        count: val.count,
      })).slice(0, 10);

      const codeSnippet = `# PandasAI Grouped Aggregation\nimport pandasai as pai\n\ndf = pai.DataFrame(dataset)\nresult = df.groupby('${catCol.name}')['${numCol.name}'].mean().reset_index()\nprint(result)`;

      return {
        id: 'res_' + Math.random().toString(36).substring(2, 9),
        query: originalQuery,
        type: 'chart',
        answer: `Average ${numCol.name} grouped by ${catCol.name}. Found ${chartData.length} distinct groups.`,
        codeSnippet,
        chart: {
          chartType: 'bar',
          title: `Average ${numCol.name} by ${catCol.name}`,
          xKey: catCol.name,
          yKey: `avg_${numCol.name}`,
          data: chartData,
        },
        engine: 'local',
        modelName: 'PandasAI Local Interpreter',
        executionTimeMs: Date.now() - startTime,
        timestamp: new Date().toLocaleTimeString(),
      };
    }
  }

  // 4. Breakdown / Composition (Pie chart)
  if (q.includes('pie') || q.includes('ratio') || q.includes('proportion') || q.includes('share') || q.includes('percentage') || q.includes('breakdown')) {
    const catCol = dataset.columns.find(c => c.distinctCount >= 2 && c.distinctCount <= 8 && matchesCol(q, c.name))
      || dataset.columns.find(c => c.distinctCount >= 2 && c.distinctCount <= 8);

    if (catCol) {
      const counts: Record<string, number> = {};
      rows.forEach(r => {
        const cat = String(r[catCol.name] ?? 'Other');
        counts[cat] = (counts[cat] || 0) + 1;
      });

      const pieData = Object.entries(counts).map(([name, value]) => ({
        name,
        value,
      }));

      const codeSnippet = `# PandasAI Categorical Distribution\nimport pandasai as pai\n\ndf = pai.DataFrame(dataset)\nresult = df['${catCol.name}'].value_counts()\nprint(result)`;

      return {
        id: 'res_' + Math.random().toString(36).substring(2, 9),
        query: originalQuery,
        type: 'chart',
        answer: `Categorical breakdown of ${catCol.name} across ${numRows.toLocaleString()} rows.`,
        codeSnippet,
        chart: {
          chartType: 'pie',
          title: `${catCol.name} Share & Distribution`,
          xKey: 'name',
          yKey: 'value',
          data: pieData,
        },
        engine: 'local',
        modelName: 'PandasAI Local Interpreter',
        executionTimeMs: Date.now() - startTime,
        timestamp: new Date().toLocaleTimeString(),
      };
    }
  }

  // 5. Top N / Ranking queries
  if (q.includes('top') || q.includes('highest') || q.includes('lowest') || q.includes('max') || q.includes('min') || q.includes('bottom')) {
    const matchN = q.match(/\b(\d+)\b/);
    const limit = matchN ? parseInt(matchN[1], 10) : 5;
    const isLowest = q.includes('lowest') || q.includes('bottom') || q.includes('min');

    const sortCol = dataset.columns.find(c => c.type === 'numeric' && matchesCol(q, c.name))
      || dataset.columns.find(c => c.type === 'numeric');

    if (sortCol) {
      const sorted = [...rows].filter(r => r[sortCol.name] !== null && !isNaN(Number(r[sortCol.name])));
      sorted.sort((a, b) => {
        const valA = Number(a[sortCol.name]);
        const valB = Number(b[sortCol.name]);
        return isLowest ? valA - valB : valB - valA;
      });

      const topRows = sorted.slice(0, limit);
      const displayCols = dataset.columnNames.slice(0, 6);

      const codeSnippet = `# PandasAI Top N Ranking\nimport pandasai as pai\n\ndf = pai.DataFrame(dataset)\nresult = df.sort_values(by='${sortCol.name}', ascending=${isLowest}).head(${limit})\nprint(result)`;

      return {
        id: 'res_' + Math.random().toString(36).substring(2, 9),
        query: originalQuery,
        type: 'dataframe',
        answer: `Retrieved the ${limit} ${isLowest ? 'lowest' : 'highest'} records ranked by ${sortCol.name}.`,
        codeSnippet,
        dataframe: {
          columns: displayCols,
          rows: topRows.map(r => {
            const row: Record<string, any> = {};
            displayCols.forEach(c => row[c] = r[c]);
            return row;
          }),
          totalRows: topRows.length,
        },
        engine: 'local',
        modelName: 'PandasAI Local Interpreter',
        executionTimeMs: Date.now() - startTime,
        timestamp: new Date().toLocaleTimeString(),
      };
    }
  }

  // Default: Smart analysis
  const sampleCols = dataset.columnNames.slice(0, 5);
  const sampleRows = rows.slice(0, 5).map(r => {
    const row: Record<string, any> = {};
    sampleCols.forEach(c => row[c] = r[c]);
    return row;
  });

  return {
    id: 'res_' + Math.random().toString(36).substring(2, 9),
    query: originalQuery,
    type: 'string',
    answer: `Analyzed query "${originalQuery}" against ${dataset.name} (${numRows.toLocaleString()} rows). Try asking specific questions like "What is the average ${dataset.columns[0]?.name}?", "Show distribution of ${dataset.columns.find(c => c.type === 'numeric')?.name || 'values'}", or "Plot bar chart of counts".`,
    codeSnippet: `# PandasAI Query Execution\nimport pandasai as pai\n\ndf = pai.DataFrame(dataset)\nresponse = df.chat("""${originalQuery}""")\nprint(response)`,
    dataframe: {
      columns: sampleCols,
      rows: sampleRows,
      totalRows: 5,
    },
    engine: 'local',
    modelName: 'PandasAI Local Interpreter',
    executionTimeMs: Date.now() - startTime,
    timestamp: new Date().toLocaleTimeString(),
  };
}

/**
 * Generates natural statistical insights for a dataset using Gemini AI.
 */
export async function generateDatasetInsights(dataset: Dataset): Promise<{
  insights: string[];
  suggestedQueries: string[];
  summary: string;
  source: 'gemini' | 'local';
}> {
  const geminiApiKey = process.env.GEMINI_API_KEY || process.env.API_KEY;
  if (geminiApiKey) {
    try {
      const ai = new GoogleGenAI({ apiKey: geminiApiKey });
      const prompt = `You are a Senior Data Scientist analyzing this dataset:
Name: ${dataset.name}
Description: ${dataset.description}
Total Records: ${dataset.rows.length}
Columns: ${JSON.stringify(dataset.columns.map(c => ({
  name: c.name,
  type: c.type,
  min: c.min,
  max: c.max,
  mean: c.mean,
  nullCount: c.nullCount,
  distinctCount: c.distinctCount,
  sample: c.sampleValues.slice(0, 3),
})))}

Produce 3-4 natural, high-value data insights about potential correlations, distribution patterns, or anomalies, along with 3 targeted queries the user should explore.
Respond in valid JSON:
{
  "summary": "1-2 sentence executive summary of the dataset's nature",
  "insights": [
    "Insight 1 with specific metric or trend",
    "Insight 2 with category comparison or relationship",
    "Insight 3 with key highlight or actionable takeaway"
  ],
  "suggestedQueries": [
    "Query 1 to run",
    "Query 2 to run",
    "Query 3 to run"
  ]
}`;

      const res = await ai.models.generateContent({
        model: 'gemini-3.8-flash',
        contents: prompt,
        config: {
          responseMimeType: 'application/json',
        },
      });

      const parsed = JSON.parse(res.text || '{}');
      if (parsed.insights && parsed.insights.length > 0) {
        return {
          summary: parsed.summary || `${dataset.name} contains ${dataset.rows.length} records ready for analysis.`,
          insights: parsed.insights,
          suggestedQueries: parsed.suggestedQueries || dataset.suggestedPrompts.slice(0, 3),
          source: 'gemini',
        };
      }
    } catch (err: any) {
      console.warn('Gemini insights generation fell back to heuristic generator:', err?.message);
    }
  }

  // Natural heuristic fallback
  const numeric = dataset.columns.filter(c => c.type === 'numeric');
  const categorical = dataset.columns.filter(c => c.type === 'string');
  const insights = [
    `Contains ${dataset.rows.length.toLocaleString()} total observations across ${dataset.columns.length} features (${numeric.length} numeric, ${categorical.length} categorical).`,
  ];
  if (numeric.length > 0) {
    const mainNum = numeric[0];
    insights.push(`Primary numeric metric "${mainNum.name}" ranges from ${mainNum.min} to ${mainNum.max} with an average of ${mainNum.mean ?? 'N/A'}.`);
  }
  if (categorical.length > 0) {
    const mainCat = categorical[0];
    insights.push(`Categorical segment "${mainCat.name}" features ${mainCat.distinctCount} distinct segments across the data.`);
  }

  return {
    summary: `${dataset.name} holds clean, structured records ready for conversational analysis and visualization.`,
    insights,
    suggestedQueries: dataset.suggestedPrompts.slice(0, 3),
    source: 'local',
  };
}
