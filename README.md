# ✦ SecureData AI

### Conversational data analysis, built with secure code execution in mind.

**SecureData AI** is a full-stack web application for exploring datasets through natural-language questions. Upload a CSV, inspect its structure, ask questions in plain English, generate visualizations, and review the analysis code — while keeping generated Python behind a restricted, fail-closed execution layer.

> **Open-source contribution focus:** this project specifically hardens the LLM-generated code execution path against the unsandboxed execution risk identified in PandasAI **Issue #1895**, while preserving the existing application's overall structure and user experience.

---

## ✨ What it does

SecureData AI combines a familiar data-explorer workflow with conversational analysis:

| Capability | Description |
|---|---|
| 💬 **Natural-language analysis** | Ask questions about tabular data without writing queries manually. |
| 📊 **Interactive charts** | Render bar charts, line plots, pie charts, and histograms from analysis results. |
| 🧮 **Generated Python** | Inspect the Python/Pandas code produced for an analysis. |
| 🗂️ **CSV upload** | Drag and drop your own tabular datasets. |
| 🔎 **Data Explorer** | Browse, search, sort, and paginate dataframe records. |
| 🧬 **Schema Inspector** | Review null counts, distinct values, min/max, averages, and sample values. |
| 🛡️ **Secure execution layer** | Validate and restrict generated code before it reaches the execution environment. |
| 🧪 **Attack-defense testing** | Test whether common OS-command injection patterns are blocked. |
| ⚡ **Keyboard navigation** | Global shortcuts (`Cmd/Ctrl+K` dataset switcher, `Cmd/Ctrl+Enter` message submit, `Cmd/Ctrl+1/2/3` tab navigation). |
| 💾 **JSON & CSV export** | Export conversational history, generated code, and query dataframe results as JSON or CSV directly from `ChatQueryView`. |
| 🤖 **Gemini AI engine** | Powered by Google Gemini 3.8 Flash for natural analytics reasoning, visual query planning, and statistical dataset insights. |
| 🌿 **Natural dark aesthetic** | Earthen obsidian theme with warm honey amber accents, organic rounded containers, and high-legibility dark Recharts visualizations. |
| 🔄 **Session persistence** | Automatic `localStorage` synchronization preserving conversation histories and active dataset selections across page reloads. |

---

## 🔐 Security hardening

The central contribution in this repository is the protection of the generated-code execution boundary.

### The original risk

The reported vulnerability in PandasAI's default execution flow allowed generated Python to run through `exec(...)` without a restricted `__builtins__` environment or a mandatory sandbox. In an application that processes untrusted datasets or prompts, indirect prompt injection could influence generated code and potentially lead to arbitrary OS command execution.

This project treats **LLM-generated code as untrusted input**.

### The implemented defense

The current implementation adds multiple defensive layers:

#### 1. Restricted built-ins

Generated Python runs with an explicit safe allowlist rather than the unrestricted Python built-in namespace.

Examples of permitted primitives include:

```text
abs
min
max
sum
len
range
dict
list
round
```

Dangerous dynamic execution helpers such as:

```text
__import__
eval
exec
open
compile
globals
```

are not exposed to the execution environment.

#### 2. AST validation

Code is parsed and checked **before execution**.

The validator blocks patterns associated with:

- operating-system imports such as `os`, `sys`, and `subprocess`
- process/network/system-oriented modules such as `shutil`, `socket`, and `ctypes`
- dangerous dunder traversal such as `__subclasses__`, `__class__`, and `__builtins__`
- command-execution methods such as `.system()`, `.popen()`, and `.run()`

The policy is **fail closed**: a validation violation stops execution before evaluation.

#### 3. Prompt-injection hardening

Dataset metadata and generated analysis inputs are treated as potentially hostile.

The query layer applies guardrails intended to keep model output focused on dataframe analysis and checks generated code again before it can be executed.

#### 4. Visible security controls

The UI exposes the execution state and provides a dedicated code-execution path for the sandbox.

The code viewer also includes an **Attack Defense Test** flow so the protection layer can be exercised directly.

> **Important:** This is a defense-in-depth implementation, not a guarantee of perfect isolation. Do not treat AST filtering or restricted built-ins as equivalent to a hardened operating-system sandbox for hostile code.

---

## 🧱 Architecture

```text
┌───────────────────────────────┐
│           React UI            │
│                               │
│  Chat · Explorer · Schema     │
│  Charts · Code Viewer         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Express API             │
│                               │
│  Dataset / Query Endpoints    │
└───────────────┬───────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌───────────────┐  ┌────────────────┐
│ Query Engine  │  │ Data Engine    │
│               │  │                │
│ NL → analysis │  │ Data loading   │
│ + code output │  │ + inspection   │
└───────┬───────┘  └────────────────┘
        │
        ▼
┌────────────────────────────────┐
│     Security Execution Layer   │
│                                │
│  AST validation                │
│  Safe built-ins                │
│  Fail-closed execution         │
└────────────────────────────────┘
```

The frontend is intentionally kept close to the application's existing component structure, while the security changes are concentrated in the execution and query paths.

---

## 🛠️ Tech stack

- **React 18**
- **Vite**
- **TypeScript**
- **Tailwind CSS**
- **Motion**
- **Recharts**
- **Lucide React**
- **Express**
- **Node.js 22**
- **npm**
- **Python-based sandbox runner**
- **Generative-AI query integration**

The application exposes its server API under `/api/*` and is configured for port `3000` in the development setup.

---

## 🚀 Getting started

### Prerequisites

Make sure you have:

- Node.js 22+
- npm
- Python 3.x

### Install

```bash
git clone <your-repository-url>
cd <your-repository-folder>

npm install
```

### Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Then configure the variables required by your local environment.

### Run the development server

Use the project's existing npm scripts, for example:

```bash
npm run dev
```

The development server is configured around:

```text
http://localhost:3000
```

### Build

```bash
npm run build
```

---

## 🧪 Security testing

The repository includes a UI flow for exercising the defense layer.

You can use the **Test Attack Defense** action to verify that a representative OS-command injection pattern is rejected by the validator rather than executed.

For development work, also test:

```text
1. Normal dataframe operations
2. Valid generated analysis code
3. Invalid imports
4. Dangerous dunder access
5. File-access attempts
6. OS/process execution attempts
7. Prompt-injection content embedded in dataset metadata
```

A security control should be considered successful only when unsafe code is rejected **before execution**.

---

## ⌨️ Global Keyboard Shortcuts & Data Export

### Global Keyboard Shortcuts
To maximize navigation speed and analytic efficiency, global shortcuts are active across the app:

| Shortcut | Action | Description |
|---|---|---|
| `Cmd/Ctrl + Enter` | **Send Message** | Submits your current query or prompts the active input field. |
| `Cmd/Ctrl + K` | **Switch Dataset** | Opens the instant command palette with fuzzy search and arrow-key selection. |
| `Cmd/Ctrl + 1` | **AI Chat** | Jumps directly to the conversational analytics interface. |
| `Cmd/Ctrl + 2` | **Data Explorer** | Swaps to the raw tabular data browser with sorting and search. |
| `Cmd/Ctrl + 3` | **Schema Inspector** | Opens column null checks, sample stats, and distributions. |
| `Cmd/Ctrl + U` | **Upload CSV** | Opens the drag-and-drop CSV dataset ingestion modal. |
| `?` or `Cmd/Ctrl + /` | **Shortcuts Guide** | Opens the shortcuts reference modal. |
| `Escape` | **Dismiss** | Closes any open modal, dialog, or command palette. |

### Conversation & Results Export
The `ChatQueryView` component includes an **Export** toolbar and per-result export actions:
- **Chat Conversation Export**:
  - **JSON (`.json`)**: Exports the full structured conversation including messages, generated Python snippets, execution timings, and sandbox security audits.
  - **CSV (`.csv`)**: RFC4180-compliant export of conversational Q&A rows.
- **Data Results Export**:
  - **CSV (`.csv`)**: Exports tabular dataframe or chart data into clean comma-separated format.
  - **JSON (`.json`)**: Exports data rows as an array of structured JSON records.

---

## 📁 Project structure

```text
.
├── server/
│   ├── dataEngine.ts
│   ├── queryEngine.ts
│   └── security/
│       ├── codeValidator.ts
│       ├── sandboxExecutor.ts
│       └── sandboxRunner.py
│
├── src/
│   ├── components/
│   │   ├── ChartRenderer.tsx
│   │   ├── ChatQueryView.tsx
│   │   ├── CodeViewer.tsx
│   │   ├── DataExplorerView.tsx
│   │   ├── DataframeTable.tsx
│   │   ├── DatasetSwitcherModal.tsx
│   │   ├── ExportModal.tsx
│   │   ├── KeyboardShortcutsModal.tsx
│   │   ├── Navbar.tsx
│   │   ├── SchemaView.tsx
│   │   └── UploadModal.tsx
│   ├── utils/
│   │   └── exportUtils.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── types.ts
│   └── index.css
│
├── .env.example
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 🤝 Contributing

Contributions are welcome, especially around:

- stronger execution isolation
- security regression tests
- prompt-injection resistance
- dataset parsing and validation
- visualization improvements
- accessibility and UI polish
- performance and reliability
- documentation

### Contribution workflow

```bash
git checkout -b feature/your-change

# make your changes
npm install
npm run build

git add .
git commit -m "feat: describe your change"
git push origin feature/your-change
```

Then open a pull request with:

1. **What changed**
2. **Why it changed**
3. **How it was tested**
4. **Any security implications**

---

## 🛡️ Responsible security reporting

Please do **not** publish a reproducible exploit for a newly discovered vulnerability in a public issue.

For security-sensitive findings, provide:

- affected component
- impact
- reproduction summary
- proposed mitigation
- relevant environment details

Keep exploit details private until a fix or coordinated disclosure is possible.

---

## 📌 Project status

This repository is an open-source development project focused on **conversational data analysis and secure generated-code execution**.

The security work documented here specifically addresses the execution-path weaknesses described in the referenced PandasAI issue and adds defense-in-depth controls to this application.

Security-sensitive software should still be reviewed and tested independently before being deployed against hostile or highly sensitive workloads.

---

## ⭐ Why this project?

Natural-language data analysis is powerful, but generated code changes the security model.

**The goal of SecureData AI is simple:**

> **Make it easy to ask questions about data — without treating generated code as trusted code.**

---

## 📄 License

Add the repository's intended open-source license here, for example:

```text
MIT License
```

Make sure the selected license matches the actual license of the repository and any upstream components before publishing.
