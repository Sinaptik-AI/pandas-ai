import fs from 'fs';
import path from 'path';

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

export interface Dataset {
  id: string;
  name: string;
  description: string;
  rows: Record<string, any>[];
  columns: ColumnStats[];
  columnNames: string[];
  suggestedPrompts: string[];
}

export function parseCSV(content: string): Record<string, any>[] {
  const lines = content.split(/\r?\n/).filter(line => line.trim().length > 0);
  if (lines.length === 0) return [];

  // Parse header
  const parseLine = (line: string): string[] => {
    const result: string[] = [];
    let cur = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          cur += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === ',' && !inQuotes) {
        result.push(cur.trim());
        cur = '';
      } else {
        cur += char;
      }
    }
    result.push(cur.trim());
    return result;
  };

  const headers = parseLine(lines[0]);
  const rows: Record<string, any>[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseLine(lines[i]);
    if (values.length !== headers.length && values.length === 1 && values[0] === '') {
      continue;
    }
    const row: Record<string, any> = {};
    headers.forEach((header, idx) => {
      const rawVal = values[idx] !== undefined ? values[idx] : '';
      if (rawVal === '' || rawVal === null || rawVal === undefined) {
        row[header] = null;
      } else if (!isNaN(Number(rawVal)) && rawVal.trim() !== '') {
        row[header] = Number(rawVal);
      } else if (rawVal.toLowerCase() === 'true') {
        row[header] = true;
      } else if (rawVal.toLowerCase() === 'false') {
        row[header] = false;
      } else {
        row[header] = rawVal;
      }
    });
    rows.push(row);
  }

  return rows;
}

export function computeColumnStats(rows: Record<string, any>[]): ColumnStats[] {
  if (rows.length === 0) return [];
  const columnNames = Object.keys(rows[0]);

  return columnNames.map(col => {
    const values = rows.map(r => r[col]);
    const nonNullValues = values.filter(v => v !== null && v !== undefined && v !== '');
    const nullCount = values.length - nonNullValues.length;
    const distinctSet = new Set(nonNullValues);
    const sampleValues = Array.from(distinctSet).slice(0, 5);

    const numericCount = nonNullValues.filter(v => typeof v === 'number').length;
    const isNumeric = nonNullValues.length > 0 && numericCount / nonNullValues.length > 0.85;

    if (isNumeric) {
      const numVals = nonNullValues.filter(v => typeof v === 'number') as number[];
      numVals.sort((a, b) => a - b);
      const min = numVals.length > 0 ? numVals[0] : 0;
      const max = numVals.length > 0 ? numVals[numVals.length - 1] : 0;
      const sum = numVals.reduce((acc, v) => acc + v, 0);
      const mean = numVals.length > 0 ? Number((sum / numVals.length).toFixed(2)) : 0;
      const median = numVals.length > 0 ? numVals[Math.floor(numVals.length / 2)] : 0;

      return {
        name: col,
        type: 'numeric',
        nullCount,
        distinctCount: distinctSet.size,
        min,
        max,
        mean,
        median,
        sampleValues,
      };
    }

    return {
      name: col,
      type: 'string',
      nullCount,
      distinctCount: distinctSet.size,
      sampleValues,
    };
  });
}

export class DatasetRepository {
  private datasets: Map<string, Dataset> = new Map();

  constructor() {
    this.loadDefaultDatasets();
  }

  private loadDefaultDatasets() {
    try {
      const heartPath = path.join(process.cwd(), 'data', 'heart.csv');
      if (fs.existsSync(heartPath)) {
        const heartContent = fs.readFileSync(heartPath, 'utf-8');
        const rows = parseCSV(heartContent);
        const stats = computeColumnStats(rows);
        this.datasets.set('heart', {
          id: 'heart',
          name: 'Heart Disease Clinical Dataset',
          description: 'Cardiovascular clinical records across 918 patients with cholesterol, BP, max HR, and diagnosis.',
          rows,
          columns: stats,
          columnNames: Object.keys(rows[0] || {}),
          suggestedPrompts: [
            'Plot a bar chart of average cholesterol by ChestPainType',
            'What is the distribution of patient age?',
            'What is the average resting BP for patients with vs without heart disease?',
            'Show the count of patients by ExerciseAngina and HeartDisease',
            'Find the top 5 highest maximum heart rates recorded',
          ],
        });
      }

      const loansPath = path.join(process.cwd(), 'data', 'loans_payments.csv');
      if (fs.existsSync(loansPath)) {
        const loansContent = fs.readFileSync(loansPath, 'utf-8');
        const rows = parseCSV(loansContent);
        const stats = computeColumnStats(rows);
        this.datasets.set('loans', {
          id: 'loans',
          name: 'Loan Payments & Delinquency',
          description: 'Payment status, principal, terms, and borrower demographics for 500 loan records.',
          rows,
          columns: stats,
          columnNames: Object.keys(rows[0] || {}),
          suggestedPrompts: [
            'Plot a bar chart of loan counts by loan_status',
            'What is the average principal amount by education level?',
            'Show the distribution of borrower age',
            'How many loans are in COLLECTION status by Gender?',
            'Show the top 5 loans by principal amount',
          ],
        });
      }
    } catch (err) {
      console.error('Error loading default datasets:', err);
    }
  }

  public getAllSummaries() {
    return Array.from(this.datasets.values()).map(d => ({
      id: d.id,
      name: d.name,
      description: d.description,
      rowCount: d.rows.length,
      columnCount: d.columns.length,
    }));
  }

  public getDataset(id: string): Dataset | undefined {
    return this.datasets.get(id);
  }

  public addCustomDataset(id: string, name: string, description: string, csvContent: string): Dataset {
    const rows = parseCSV(csvContent);
    const stats = computeColumnStats(rows);
    const colNames = Object.keys(rows[0] || {});
    const numericCols = stats.filter(s => s.type === 'numeric').map(s => s.name);
    const categoricalCols = stats.filter(s => s.type === 'string').map(s => s.name);

    const suggestedPrompts: string[] = [
      `Summarize the dataset and key statistics`,
    ];
    if (categoricalCols.length > 0 && numericCols.length > 0) {
      suggestedPrompts.push(`Plot average ${numericCols[0]} by ${categoricalCols[0]}`);
    }
    if (numericCols.length > 0) {
      suggestedPrompts.push(`Show the distribution of ${numericCols[0]}`);
    }
    if (categoricalCols.length > 0) {
      suggestedPrompts.push(`Show the breakdown of counts by ${categoricalCols[0]}`);
    }

    const dataset: Dataset = {
      id,
      name,
      description,
      rows,
      columns: stats,
      columnNames: colNames,
      suggestedPrompts,
    };

    this.datasets.set(id, dataset);
    return dataset;
  }
}
