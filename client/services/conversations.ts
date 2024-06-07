import { DeleteRequest, GetRequest } from "@/utils/apiUtils";

const apiUrl = `/v1/conversations`;


export const GetConversations = async (skip: number, limit: number) => {
    try {
        const response = await GetRequest(`${apiUrl}/?skip=${skip}&limit=${limit}`);
        return response;
    } catch (error) {
        console.error("Get request failed", error);
        throw error;
    }
};

export const ConversationMessages = async (
    conversationId: string,
    skip: number,
) => {
    try {
        const response = await GetRequest(`${apiUrl}/${conversationId}/messages?skip=${skip}&limit=8`);
        return response;
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};

export const ArchiveConversationApi = async (conversationId) => {
    try {
        const response = await DeleteRequest(`${apiUrl}/${conversationId}`);
        return response;
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};