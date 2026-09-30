/**
 * Code and Prompt Security Validator for PandasAI
 * Addresses Issue #1895: Default code executor runs LLM-generated code with full builtins (no sandbox by default) -> RCE via indirect prompt injection
 */

export interface SecurityValidationResult {
  isSafe: boolean;
  violations: string[];
  severity: 'none' | 'warning' | 'critical';
  detectedPatterns: string[];
}

// Blocklist of forbidden modules that can lead to RCE, OS command execution, or network egress
export const FORBIDDEN_MODULES = [
  'os',
  'sys',
  'subprocess',
  'shutil',
  'pty',
  'commands',
  'builtins',
  'posix',
  'nt',
  'ctypes',
  'socket',
  'urllib',
  'requests',
  'http',
  'threading',
  'multiprocessing',
  'pickle',
  'importlib',
  'signal',
  'platform',
  'inspect',
  'gc',
];

// Dangerous calls and functions
export const FORBIDDEN_CALLS = [
  '__import__',
  'eval',
  'exec',
  'open',
  'compile',
  'input',
  'breakpoint',
  'globals',
  'locals',
  'vars',
  'dir',
  'getattr',
  'setattr',
  'delattr',
];

// Dangerous dunders and traversal patterns
export const FORBIDDEN_DUNDERS = [
  '__builtins__',
  '__class__',
  '__base__',
  '__bases__',
  '__subclasses__',
  '__mro__',
  '__globals__',
  '__code__',
  '__reduce__',
  '__reduce_ex__',
  '__dict__',
  '__getattribute__',
];

// Command execution methods
export const FORBIDDEN_COMMAND_METHODS = [
  'system',
  'popen',
  'spawn',
  'call',
  'check_output',
  'check_call',
  'run',
];

/**
 * Validates generated or user-provided Python code against the Default Sandbox security policy.
 */
export function validatePythonCode(code: string): SecurityValidationResult {
  const violations: string[] = [];
  const detectedPatterns: string[] = [];

  if (!code || typeof code !== 'string') {
    return { isSafe: true, violations: [], severity: 'none', detectedPatterns: [] };
  }

  // 1. Check for forbidden module imports (import os, from os import system, import os.path, etc.)
  for (const mod of FORBIDDEN_MODULES) {
    const importRegex = new RegExp(`(^|\\n|;)\\s*(import\\s+([a-zA-Z0-9_.]+,\\s*)*${mod}\\b|from\\s+${mod}\\b)`, 'i');
    if (importRegex.test(code)) {
      violations.push(`Forbidden module import detected: '${mod}'. System & OS modules are blocked by default sandbox.`);
      detectedPatterns.push(`import ${mod}`);
    }
  }

  // 2. Check for forbidden builtin calls (eval, exec, __import__, open, etc.)
  for (const call of FORBIDDEN_CALLS) {
    const callRegex = new RegExp(`\\b${call}\\s*\\(`, 'i');
    if (callRegex.test(code)) {
      violations.push(`Forbidden function invocation: '${call}()'. Dynamic evaluation and system calls are blocked.`);
      detectedPatterns.push(`${call}()`);
    }
  }

  // 3. Check for dunder traversal (__subclasses__, __class__, __builtins__, etc.)
  for (const dunder of FORBIDDEN_DUNDERS) {
    const dunderRegex = new RegExp(`\\b${dunder}\\b`, 'i');
    if (dunderRegex.test(code)) {
      violations.push(`Forbidden dunder attribute access: '${dunder}'. Object traversal is restricted.`);
      detectedPatterns.push(dunder);
    }
  }

  // 4. Check for OS command execution method invocations (.system(, .popen(, etc.)
  for (const method of FORBIDDEN_COMMAND_METHODS) {
    const methodRegex = new RegExp(`\\.${method}\\s*\\(`, 'i');
    if (methodRegex.test(code)) {
      violations.push(`Forbidden execution method invocation: '.${method}()'. Arbitrary command execution is disallowed.`);
      detectedPatterns.push(`.${method}()`);
    }
  }

  // 5. Check for obfuscation techniques (chr() concatenation, base64 decode, hex escapes)
  if (/(chr\s*\(\s*\d+\s*\)\s*(\+|\.join)){3,}/i.test(code)) {
    violations.push(`Potential obfuscation detected: concatenated character codes.`);
    detectedPatterns.push('char_obfuscation');
  }

  const isSafe = violations.length === 0;
  const severity = violations.length > 0 ? 'critical' : 'none';

  return {
    isSafe,
    violations,
    severity,
    detectedPatterns,
  };
}

/**
 * Detects potential indirect prompt injection vectors in untrusted dataset metadata or queries.
 */
export function detectPromptInjection(input: string): { isSuspicious: boolean; reason?: string } {
  if (!input || typeof input !== 'string') return { isSuspicious: false };

  const suspiciousPatterns = [
    { pattern: /ignore\s+(all\s+)?(previous|prior)\s+instructions/i, reason: 'Instruction override directive' },
    { pattern: /(system\s*prompt|system\s*directive|admin\s*mode|root\s*access)/i, reason: 'Privilege escalation prompt pattern' },
    { pattern: /(__import__\s*\(|os\.system|subprocess\.|exec\s*\(|eval\s*\()/i, reason: 'Direct RCE payload embedding' },
    { pattern: /(cat\s+\/etc\/passwd|rm\s+-rf|whoami|id\s+>)/i, reason: 'UNIX command injection token' },
    { pattern: /print\(open\(.*\)\.read\(\)\)/i, reason: 'Arbitrary file disclosure pattern' },
  ];

  for (const { pattern, reason } of suspiciousPatterns) {
    if (pattern.test(input)) {
      return { isSuspicious: true, reason };
    }
  }

  return { isSuspicious: false };
}

/**
 * Sanitizes untrusted user strings, stripping non-printable control characters.
 */
export function sanitizeUntrustedInput(input: string): string {
  if (!input || typeof input !== 'string') return '';
  return input
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '') // remove unprintable control chars
    .trim();
}
