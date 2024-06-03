import { DeleteRequest, GetRequest, PatchRequest, PostRequest } from "@/utils/apiUtils";
import { BASE_API_URL } from "utils/constants";

const chatApiUrl = `${BASE_API_URL}/api/chat`;


export const ChatApi = async (chatdata) => {
  try {
    const response = await PostRequest(chatApiUrl, chatdata);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
export const ChatReactionApi = async (id, chatdata) => {
  const apiUrl = `${chatApiUrl}/conversation-message/${id}/user-rating`;
  try {
    const response = await PostRequest(apiUrl, chatdata);
    return response;
  } catch (error) {
    console.error('Get request failed', error);
    throw error;
  }
};

export const ChatMessageRetry = async (messageId: string) => {
  const apiUrl = `${chatApiUrl}/conversation-message/${messageId}/retry-code`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error('Get request failed', error);
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
export const AddPartialDF = async (conversationId: string, body) => {
  const apiUrl = `${chatApiUrl}/conversation-message/${conversationId}/partial-df`;
  try {
    const response = await PostRequest(apiUrl, body);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};

export const ConversationChatApi = async (page, rowsPerPage) => {
  const apiUrl = `${chatApiUrl}/conversations?page_number=${page}&rows_per_page=${rowsPerPage}`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error('Get request failed', error);
    throw error;
  }
};
export const ConversationChatBySpaceApi = async (spaceId, page, rowsPerPage) => {
  const apiUrl = `${chatApiUrl}/conversations?space_id=${spaceId}&page_number=${page}&rows_per_page=${rowsPerPage}`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error('Get request failed', error);
    throw error;
  }
};

export const ArchiveConversationApi = async (conversationId) => {
  const apiUrl = `${chatApiUrl}/conversation/${conversationId}`;
  try {
    const response = await DeleteRequest(apiUrl);
    return response;
  } catch (error) {
    console.error('Get request failed', error);
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

export const EditCode = async (
  messageId: string,
  dataToUpdate,
) => {
  const addUrl = `${chatApiUrl}/conversation-message/${messageId}/code`;
  try {
    const response = await PatchRequest(addUrl, dataToUpdate);
    return response;
  } catch (error) {
    console.error("Update request failed", error);
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
export const GetDataframeFilters = async (messageId: string) => {
  const apiUrl = `${chatApiUrl}/conversation-message/${messageId}/dataframe-filter`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
export const AddDataframeFilters = async (messageId: string, body) => {
  const apiUrl = `${chatApiUrl}/conversation-message/${messageId}/apply-filters`;
  try {
    const response = await PostRequest(apiUrl, body);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};