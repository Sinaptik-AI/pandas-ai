import { GetRequest } from "@/utils/apiUtils";

const apiUrl = `/v1/users`;

export const getMe = async () => {
    try {
        const response = await GetRequest(`${apiUrl}/me`);
        return response;
    } catch (error) {
        console.error("Get request failed", error);
        throw error;
    }
};