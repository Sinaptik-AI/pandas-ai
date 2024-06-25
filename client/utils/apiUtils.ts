import axios, { AxiosResponse } from 'axios';
import { BASE_API_URL } from './constants';

export const axiosInstance = axios.create({
  baseURL: BASE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// axiosInstance.interceptors.request.use((config) => {
//   const token = localStorage.getItem('accessToken');
//   if (token) {
//     config.headers['Authorization'] = `Bearer ${token}`;
//   }
//   return config;
// }, (error) => {
//   return Promise.reject(error);
// });

export async function GetRequest(url: string): Promise<AxiosResponse<any, any>> {
  try {
    const response = await axiosInstance.get(url);
    return response;
  } catch (error) {
    throw error;
  }
}

export async function PostRequest(url: string, requestData: object, headers = {}): Promise<AxiosResponse<any, any>> {
  try {
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };
    const updatedHeader = { ...defaultHeaders, ...headers }

    const response = await axiosInstance.post(url, requestData, { headers: updatedHeader });
    return response;
  } catch (error) {
    throw error;
  }
}

export async function DeleteRequest(url: string): Promise<AxiosResponse<any, any>> {
  try {
    const response = await axiosInstance.delete(url);
    return response;
  } catch (error) {
    throw error;
  }
}

export async function PutRequest(url: string, data: object): Promise<AxiosResponse<any, any>> {
  try {
    const response = await axiosInstance.put(url, data);
    return response;
  } catch (error) {
    throw error;
  }
}

export async function PatchRequest(url: string, data: object): Promise<AxiosResponse<any, any>> {
  try {
    const response = await axiosInstance.patch(url, data);
    return response;
  } catch (error) {
    throw error;
  }
}

export async function DeleteRequestWithBody(url: string, requestData: object): Promise<AxiosResponse<any, any>> {
  try {
    const response = await axiosInstance.delete(url, { data: requestData });
    return response;
  } catch (error) {
    throw error;
  }
}
