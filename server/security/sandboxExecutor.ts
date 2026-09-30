import { spawn } from 'child_process';
import path from 'path';
import { validatePythonCode, SecurityValidationResult } from './codeValidator';

export interface SandboxExecutionResult {
  status: 'success' | 'blocked' | 'runtime_error' | 'timeout';
  output?: string;
  violations?: string[];
  securityPolicy: string;
  executionTimeMs: number;
  message?: string;
}

const RUNNER_SCRIPT = path.join(process.cwd(), 'server', 'security', 'sandboxRunner.py');
const EXECUTION_TIMEOUT_MS = 3000;

/**
 * Executes Python code within the default secure sandbox.
 * Enforces AST-level validation and restricted __builtins__.
 */
export async function executeInSecureSandbox(
  code: string,
  datasetRecords: Record<string, any>[] = []
): Promise<SandboxExecutionResult> {
  const startTime = Date.now();

  // 1. Static pre-execution security check (Fail-Closed)
  const staticCheck: SecurityValidationResult = validatePythonCode(code);
  if (!staticCheck.isSafe) {
    return {
      status: 'blocked',
      securityPolicy: 'DEFAULT_SANDBOX_STRICT (Restricted Builtins + AST Allowlist)',
      violations: staticCheck.violations,
      executionTimeMs: Date.now() - startTime,
      message: 'Code execution blocked: detected forbidden imports, system calls, or dangerous attributes.',
    };
  }

  // 2. Execute via the Python AST-validated sandbox runner with restricted __builtins__
  return new Promise((resolve) => {
    let resolved = false;

    const payload = JSON.stringify({
      code,
      dataset: datasetRecords.slice(0, 100), // pass sample rows for analysis
    });

    const pyProcess = spawn('python3', [RUNNER_SCRIPT, payload]);

    let stdoutData = '';
    let stderrData = '';

    const timer = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        pyProcess.kill('SIGKILL');
        resolve({
          status: 'timeout',
          securityPolicy: 'DEFAULT_SANDBOX_STRICT',
          violations: ['Execution exceeded time limit of 3000ms'],
          executionTimeMs: Date.now() - startTime,
          message: 'Execution aborted: sandbox CPU/Time limit exceeded.',
        });
      }
    }, EXECUTION_TIMEOUT_MS);

    pyProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    pyProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    pyProcess.on('close', (exitCode) => {
      if (resolved) return;
      resolved = true;
      clearTimeout(timer);

      try {
        const parsed = JSON.parse(stdoutData.trim());
        resolve({
          status: parsed.status,
          output: parsed.output,
          violations: parsed.violations || [],
          securityPolicy: parsed.securityPolicy || 'DEFAULT_SANDBOX_STRICT',
          executionTimeMs: Date.now() - startTime,
          message: parsed.message,
        });
      } catch (err) {
        if (exitCode !== 0 || stderrData.trim()) {
          resolve({
            status: 'runtime_error',
            securityPolicy: 'DEFAULT_SANDBOX_STRICT',
            violations: [],
            executionTimeMs: Date.now() - startTime,
            message: stderrData.trim() || 'Python process exited with error',
          });
        } else {
          resolve({
            status: 'success',
            output: stdoutData.trim() || 'Executed cleanly in sandbox.',
            violations: [],
            securityPolicy: 'DEFAULT_SANDBOX_STRICT',
            executionTimeMs: Date.now() - startTime,
          });
        }
      }
    });

    pyProcess.on('error', (err) => {
      if (resolved) return;
      resolved = true;
      clearTimeout(timer);
      resolve({
        status: 'runtime_error',
        securityPolicy: 'DEFAULT_SANDBOX_STRICT',
        violations: [],
        executionTimeMs: Date.now() - startTime,
        message: `Sandbox runner initialization error: ${err.message}`,
      });
    });
  });
}
