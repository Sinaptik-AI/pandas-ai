export interface SpacesData {
  length: number;
  dataframes: number[];
  dataframes_count: number;
  id: string;
  name: string;
}
export interface SpacesContextData {
  data?: {
    user: {
      firstName: string;
      lastName: string;
    };
    stateChangevalue: boolean;
    isAdmin: string;
    adminStatus: string;
    spaces?: {
      spaceLoading: boolean;
      spacesData?: SpacesData[];
    };
  };
  setGlobalData?: (data: unknown) => void;
}

export interface SpaceDataDetail {
  dataframes_count: React.ReactNode;
  length: number;
  name?: string;
  id?: number | string;
  dataframes?: {
    dataframe: {
      name?: string;
      description?: string;
      dataframes_count: number;
      id: number;
      headers?: string[];
      rows?: (string | number)[][] | { [key: string]: React.ReactNode }[];
    };
  }[];
}
export interface LogsContextData {
  data?: {
    stateChangevalue: boolean;
    isAdmin: string;
    adminStatus: string;
  };
  setGlobalData?: (data: unknown) => void;
}
