import { ChatMessageData } from "@/types/chat-types";

export interface ChatScreenProps {
  scrollLoad: boolean;
  isTyping: boolean;
  sendQuery: boolean;
  setSendQuery: (value: boolean) => void;
  chatData: ChatMessageData[];
  setChatData: (e) => void;
  hasMore: boolean;
  scrollDivRef?: React.RefObject<HTMLDivElement>
  queryRef: React.RefObject<HTMLInputElement>;
  setFollowUpQuestionDiv?: (e) => void;
  followUpQuestionDiv?: boolean;
  followUpQuestions?: { id: string, question: string }[];
  loading?: boolean;
}
