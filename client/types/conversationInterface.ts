export interface DataRow {
  [key: string]: string | number | null | undefined;
}
interface DataFrame {
  headers: string[];
  rows: DataRow[];
}
interface DataSetData {
  Connector: {
    length: number;
    id: number;
    type?: string;
    config?: {
      database: string;
      host: string;
      password: string;
      port: number;
      table: string;
      username: string;
    };
    created_at: string;
    dataframe: {
      id: number;
      name: string;
      description: string;
      dataframe: DataFrame;
    };
  };
  description: string;
  name: string;
  id: number;
  type: string;
  config: {
    database: string;
    host: string;
    password: string;
    port: number;
    table: string;
    username: string;
  };
  created_at: string;
  dataframe: {
    id: number;
    name: string;
    description: string;
    dataframe: DataFrame;
  };
}

export interface DataSetContextData {
  data?: {
    isSwitched: boolean;
    conversations?: {
      conversationCount: number;
      conversationData: {
        id: string;
        created_at: string;
        space: {
          id: string;
          name: string;
        };
        space_id: string;
        user_id: string;
        mesages: {
          id: string;
          query: string;
        }[]
        conversation_id: string;
        query: string;
        response: {
          type: string;
          message: string;
          value: {
            headers: string[];
            rows: string[];
          };
        };
        log_id: number;
      }[];
    };
    stateChangevalue: boolean;
    isAdmin: string;
    adminStatus: string;
    datasets?: {
      isDataSetsLoading: boolean;
      dataSetData?: DataSetData[];
    };
  };
  setGlobalData?: (data: unknown) => void;
}
export interface ChatDetailContextData {
  data?: {
    chatInterfaceToggle: boolean;
  };
  setGlobalData?: (data: unknown) => void;
}
