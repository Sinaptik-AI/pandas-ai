
import { DeleteRequest, PostRequest, PutRequest } from '@/utils/apiUtils';
import { BASE_API_URL } from '@/utils/constants';

const datasetsApiUrl = `/v1/datasets`;


export const GetAllDataSets = async () => {
    try {
        const response = await fetch(`${BASE_API_URL}${datasetsApiUrl}/`, { next: { tags: ['GetAllDataSets'] } });
        return await response.json();
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};

export const GetDatasetDetails = async (datasetId: string) => {
    try {
        const response = await fetch(`${BASE_API_URL}${datasetsApiUrl}/${datasetId}`, { next: { tags: ['GetDatasetDetails', datasetId] } })
        return await response.json();
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};
export const UpdateDatasetCard = async (datasetId: string, body: { name: string, description?: string }) => {
    try {
        const response = await PutRequest(`${datasetsApiUrl}/${datasetId}`, body);
        return response;
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};

export const CreateDataset = async (body) => {
    try {
        const headers = {
            'Content-Type': 'multipart/form-data',
        }
        const response = await PostRequest(`${datasetsApiUrl}`, body, headers);
        return response;
    } catch (error) {
        console.error('request failed', error);
        throw error;
    }
};

export const DeleteDataset = async (dataset_id: string) => {
    try {
        const response = await DeleteRequest(`${datasetsApiUrl}/${dataset_id}`);
        return response;
    } catch (error) {
        console.error('request failed', error);
        throw error;
    }
};
