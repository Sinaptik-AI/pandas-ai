
import { BASE_API_URL } from '@/utils/constants';

const logsApiUrl = `/v1/logs`;

export const GetLogs = async () => {
    try {
        const response = await fetch(`${BASE_API_URL}${logsApiUrl}/`, { next: { tags: ['GetLogs'] } });
        return await response.json();
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};

export const GetLogDetails = async (logId: string) => {
    try {
        const response = await fetch(`${BASE_API_URL}${logsApiUrl}/${logId}/`, { next: { tags: ['GetLogDetails', logId] } });
        return await response.json();
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};