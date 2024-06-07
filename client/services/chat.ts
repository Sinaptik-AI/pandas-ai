import { DeleteRequest, GetRequest, PatchRequest, PostRequest } from "@/utils/apiUtils";

const chatApiUrl = `/v1/chat`;


export const ChatApi = async (chatdata) => {
  try {
    const response = await PostRequest(`${chatApiUrl}/`, chatdata);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};

export const FetchDataframe = async (id: number | string) => {
  const apiUrl = `${chatApiUrl}/conversation-message-dataframe/${id}`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};

export const ConversationHistory = async (
  conversationId: string,
  page: number
) => {
  const apiUrl = `${chatApiUrl}/conversations/${conversationId}?page_number=${page}&rows_per_page=${8}`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error('Get request failed', error);
    throw error;
  }
};

export const FetchFollowUpQuestions = async (conversationId: string) => {
  const apiUrl = `${chatApiUrl}/conversations/${conversationId}/followup-questions`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
export const GetChatLabel = async (chatId: string) => {
  const apiUrl = `${chatApiUrl}/conversation-message/${chatId}/result-label`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};

export const ExplainConversationMessage = async (conversationId: string, messageId: string) => {
  const apiUrl = `${chatApiUrl}/conversation/${conversationId}/conversation-message/${messageId}/explain`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};