import { GetRequest, PostRequest } from "@/utils/apiUtils";

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