
import { DeleteRequest, GetRequest, PostRequest, PutRequest } from '@/utils/apiUtils';

const datasetsApiUrl = `/v1/datasets`;


export const GetAllDataSets = async () => {
    try {
        const response = await GetRequest(`${datasetsApiUrl}/`);
        return response;
    } catch (error) {
        console.error('Get request failed', error);
        throw error;
    }
};

export const GetDatasetDetails = async (datasetId: string) => {
    try {
        const response = await GetRequest(`${datasetsApiUrl}/${datasetId}`);
        return response;
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
