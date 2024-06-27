export interface LogsData extends Array<LogData> { }
export interface LogData {
  timestamp: string | number | Date;
  id?: number;
  query?: string;
  executionDate?: string;
  success?: boolean;
  last_name?: string;
  first_name?: string;
  execution_time?: string;
  name?: string;
  surname?: string;
}

export interface LogsContextData {
  data?: {
    user: { firstName: string; lastName: string };
    name: string;
    surname: string;
    stateChangevalue: boolean;
    isAdmin: string;
    adminStatus: string;
    logs?: {
      logsCount: number;
      logsLoader: boolean;
      logsData?: LogData[];
    };
  };
  setGlobalData?: (data: unknown) => void;
}
export interface valueProps {
  type: string;
  value: {
    headers: string[];
    rows: (string | number)[][];
  };
}
export interface LogsDetailInterface {
  name?: string;
  first_name?: string;
  last_name?: string;
  dataframes?: {
    headers?: string[];
    rows?: (string | number)[][];
  }[];
  execution_time?: number;
  created_at?: string;
  query_info?: {
    conversation_id: string;
    instance: string;
    is_related_query: boolean;
    output_type?: string | null;
    query: string;
  };
  response: {
    type?: string;
    value?:
    | string
    | {
      headers?: string[];
      rows?: (string | number)[][];
    };
  };
  steps?: {
    content_type: string;
    data: {
      exception: string;
      content_type: string;
      value: string | valueProps | null | any;
    };
    execution_time?: number;
    generated_prompt?: string;
    prompt_class?: string;
    success?: boolean;
    type?: string | null;
    code_generated?: string;
    message?: string;
    result: {
      type?: string | boolean | null | number;
      value:
      | string
      | {
        headers?: [];
        rows?: (string | number)[][];
      };
    };
  }[];
}

export interface userName {
  last_name: string;
  first_name: string;
}
