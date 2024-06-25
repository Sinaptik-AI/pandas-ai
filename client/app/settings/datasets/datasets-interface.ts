export interface IDatasetDetails {
  id?: string;
  name?: string;
  table_name?: string;
  description?: string | null;
  created_at?: string;
  head?: {
    headers?: string[];
    rows?: (string | number | null)[][];
  };
  user_id?: string;
  organization_id?: string;
  connector_id?: string;
  field_descriptions?: string | null;
  filterable_columns?: string[] | null;
}


export interface ValidationErrorsAddForm {
  name?: string;
  description?: string;
  table?: string;
  database?: string;
  host?: string;
  port?: string;
  userName?: string;
  password?: string;
  account?: string;
  dbSchema?: string;
  token?: string;
  apiKey?: string;
  baseId?: string;
  httpPath?: string;
  warehouse?: string;
  tableName?: string;
  tableDescription?: string;
  projectID?: string;
}
