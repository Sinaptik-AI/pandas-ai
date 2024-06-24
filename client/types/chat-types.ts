export interface ChatMessageData {
  reaction_id?: string | null;
  id?: string;
  space_id?: string;
  conversation_id?: string;
  query?: string;
  response?: ChatResponseItem[];
  error?: boolean;
  type?: string;
  value?: string;
  thumbs_up?: boolean;
  code?: string;
  plotSettings?: any
}

export interface ChatResponseItem {
  type?: string;
  message?: string;
  value?: {
    headers?: string[] | null;
    rows?: (string | number)[][] | { [key: string]: React.ReactNode }[];
    id?: string
  }
}
