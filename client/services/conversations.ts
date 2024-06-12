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
    skip?: number,
    limit?: number,
) => {
    let url = ''
    if (skip && limit) {
        url = `${apiUrl}/${conversationId}/messages?skip=${skip}&limit=${limit}`
    } else {
        url = `${apiUrl}/${conversationId}/messages`
    }
    try {
        const response = await GetRequest(url);
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