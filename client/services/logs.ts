
import { GetRequest } from '@/utils/apiUtils';

const logsApiUrl = `/v1/logs`;


export const GetLogs = async () => {
    try {
        const response = await GetRequest(`${logsApiUrl}/`);
        return response;
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};
export const GetLogDetails = async (logId: string) => {
    try {
        const response = await GetRequest(`${logsApiUrl}/${logId}`);
        return response;
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};