import express from 'express';
import cors from 'cors';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import { DatasetRepository } from './server/dataEngine';
import { processQuery, generateDatasetInsights } from './server/queryEngine';
import { executeInSecureSandbox } from './server/security/sandboxExecutor';
import { validatePythonCode, detectPromptInjection, sanitizeUntrustedInput } from './server/security/codeValidator';

const PORT = 3000;
const repo = new DatasetRepository();

async function startServer() {
  const app = express();

  app.use(cors());
  app.use(express.json({ limit: '20mb' }));

  // Health endpoint
  app.get('/api/health', (req, res) => {
    const hasKey = Boolean(process.env.GEMINI_API_KEY || process.env.API_KEY);
    res.json({
      status: 'ok',
      hasGeminiKey: hasKey,
      geminiModel: 'gemini-3.8-flash',
      engine: hasKey ? 'Gemini 3.8 Flash' : 'PandasAI Local Interpreter',
      datasetsCount: repo.getAllSummaries().length,
      sandbox: {
        enabledByDefault: true,
        restrictedBuiltins: true,
        astAllowlist: true,
        status: 'PROTECTED',
      },
    });
  });

  // Sandbox status & security info endpoint (Issue #1895)
  app.get('/api/sandbox/status', (req, res) => {
    res.json({
      active: true,
      policy: 'DEFAULT_SANDBOX_STRICT',
      issueMitigation: 'Issue #1895: Default code executor sandbox enforcement',
      features: [
        'Strict restricted __builtins__ allowlist (no __import__, open, eval, exec)',
        'AST-level syntax tree allowlist rejecting forbidden imports & dunders',
        'Indirect prompt injection defense for CSV metadata & column names',
        'Fail-closed security policy on unapproved library references',
        'Subprocess execution timeout (3000ms max)',
      ],
    });
  });

  // Sandbox code validation endpoint
  app.post('/api/sandbox/validate', (req, res) => {
    const { code } = req.body;
    if (!code || typeof code !== 'string') {
      return res.status(400).json({ error: 'Code string required' });
    }
    const result = validatePythonCode(code);
    res.json(result);
  });

  // Sandbox execution endpoint
  app.post('/api/sandbox/execute', async (req, res) => {
    try {
      const { code, datasetId } = req.body;
      if (!code || typeof code !== 'string') {
        return res.status(400).json({ error: 'Code string required' });
      }

      const dataset = datasetId ? repo.getDataset(datasetId) : undefined;
      const sampleRows = dataset ? dataset.rows.slice(0, 50) : [];

      const execResult = await executeInSecureSandbox(code, sampleRows);
      res.json(execResult);
    } catch (err: any) {
      res.status(500).json({
        status: 'runtime_error',
        securityPolicy: 'DEFAULT_SANDBOX_STRICT',
        message: err.message || 'Execution error in sandbox',
      });
    }
  });

  // Get all datasets summary
  app.get('/api/datasets', (req, res) => {
    res.json(repo.getAllSummaries());
  });

  // Get dataset details by ID
  app.get('/api/datasets/:id', (req, res) => {
    const dataset = repo.getDataset(req.params.id);
    if (!dataset) {
      return res.status(404).json({ error: 'Dataset not found' });
    }
    res.json({
      id: dataset.id,
      name: dataset.name,
      description: dataset.description,
      rowCount: dataset.rows.length,
      columnCount: dataset.columns.length,
      columns: dataset.columns,
      sampleRows: dataset.rows.slice(0, 5),
      suggestedPrompts: dataset.suggestedPrompts,
    });
  });

  // Get Gemini AI insights for a dataset
  app.get('/api/datasets/:id/insights', async (req, res) => {
    try {
      const dataset = repo.getDataset(req.params.id);
      if (!dataset) {
        return res.status(404).json({ error: 'Dataset not found' });
      }
      const insights = await generateDatasetInsights(dataset);
      res.json(insights);
    } catch (err: any) {
      res.status(500).json({ error: err.message || 'Failed to generate insights' });
    }
  });

  // Get paginated rows
  app.get('/api/datasets/:id/rows', (req, res) => {
    const dataset = repo.getDataset(req.params.id);
    if (!dataset) {
      return res.status(404).json({ error: 'Dataset not found' });
    }

    const page = parseInt(req.query.page as string, 10) || 1;
    const limit = Math.min(parseInt(req.query.limit as string, 10) || 25, 100);
    const search = ((req.query.search as string) || '').toLowerCase().trim();
    const sortCol = req.query.sortCol as string;
    const sortDir = (req.query.sortDir as string) === 'desc' ? -1 : 1;

    let filteredRows = dataset.rows;

    if (search) {
      filteredRows = filteredRows.filter(r =>
        Object.values(r).some(val =>
          val !== null && val !== undefined && String(val).toLowerCase().includes(search)
        )
      );
    }

    if (sortCol && dataset.columnNames.includes(sortCol)) {
      filteredRows = [...filteredRows].sort((a, b) => {
        const valA = a[sortCol];
        const valB = b[sortCol];
        if (valA === valB) return 0;
        if (valA === null || valA === undefined) return 1;
        if (valB === null || valB === undefined) return -1;
        if (typeof valA === 'number' && typeof valB === 'number') {
          return (valA - valB) * sortDir;
        }
        return String(valA).localeCompare(String(valB)) * sortDir;
      });
    }

    const totalRows = filteredRows.length;
    const totalPages = Math.ceil(totalRows / limit);
    const offset = (page - 1) * limit;
    const paginatedRows = filteredRows.slice(offset, offset + limit);

    res.json({
      rows: paginatedRows,
      totalRows,
      totalPages,
      currentPage: page,
      limit,
    });
  });

  // Upload custom CSV dataset
  app.post('/api/datasets/upload', (req, res) => {
    try {
      const { name, description, csvContent } = req.body;
      if (!csvContent || typeof csvContent !== 'string') {
        return res.status(400).json({ error: 'csvContent string is required' });
      }

      const cleanName = sanitizeUntrustedInput(name || 'Custom Dataset');
      const cleanDesc = sanitizeUntrustedInput(description || 'User uploaded CSV dataset');

      // Check first line (headers) for indirect prompt injection attempts
      const headerLine = csvContent.split(/\r?\n/)[0] || '';
      const injectionCheck = detectPromptInjection(headerLine);
      if (injectionCheck.isSuspicious) {
        return res.status(400).json({
          error: `Security policy rejection: CSV headers contain potential indirect prompt injection payload (${injectionCheck.reason}).`,
        });
      }

      const id = 'custom_' + Date.now().toString(36);
      const dataset = repo.addCustomDataset(
        id,
        cleanName,
        cleanDesc,
        csvContent
      );

      res.status(201).json({
        id: dataset.id,
        name: dataset.name,
        rowCount: dataset.rows.length,
        columnCount: dataset.columns.length,
        sandboxVerified: true,
      });
    } catch (err: any) {
      res.status(400).json({ error: err.message || 'Failed to parse CSV' });
    }
  });

  // Query / Chat endpoint
  app.post('/api/chat', async (req, res) => {
    try {
      const { datasetId, query } = req.body;
      if (!query || typeof query !== 'string') {
        return res.status(400).json({ error: 'Query string is required' });
      }

      const dataset = repo.getDataset(datasetId || 'heart');
      if (!dataset) {
        return res.status(404).json({ error: 'Dataset not found' });
      }

      const result = await processQuery(dataset, query);
      res.json(result);
    } catch (err: any) {
      console.error('Chat endpoint error:', err);
      res.status(500).json({
        error: err.message || 'Error processing data analysis query',
      });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`PandasAI Studio server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
