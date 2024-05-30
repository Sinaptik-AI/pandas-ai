import axios, { AxiosResponse } from 'axios';
import { AuthPostRefreshToken, AuthRefreshToken } from '../services/authRefresh';

export async function useGetApi(url: string): Promise<AxiosResponse<any, any>> {
  const token = localStorage.getItem('accessToken');
  try {
    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
    const response = await axios.get(url, { headers });

    return response;
  } catch (error) {
    if (error?.response?.status === 401) {
      await AuthRefreshToken();
    }
    throw error;
  }
}

export async function usePostApi(url: string, requestData: object, headers = {}): Promise<AxiosResponse<any, any>> {
  try {
    const token = localStorage.getItem('accessToken');
    const defaultHeaders = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
    const updatedHeader = { ...defaultHeaders, ...headers }

    const response = await axios.post(url, requestData, { headers: updatedHeader });

    return response;
  } catch (error) {
    if (error?.response?.status === 401) {
      const newToken = await AuthPostRefreshToken();
      if (newToken) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const refreshedResponse = await usePostApi(url, requestData);
        return refreshedResponse;
      }
    }
    throw error;
  }
}
export async function useSignUpPostApi(url: string, requestData: object): Promise<AxiosResponse<any, any>> {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
    const response = await axios.post(url, requestData, { headers });
    return response;
  } catch (error) {
    if (error?.response?.status === 401) {
      const newToken = await AuthPostRefreshToken();
      if (newToken) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const refreshedResponse = await usePostApi(url, requestData);
        return refreshedResponse;
      }
    }
    throw error;
  }
}

export async function useDeleteApi(url: string): Promise<AxiosResponse<any, any>> {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = {
      Authorization: `Bearer ${token}`,
    };
    const response = await axios.delete(url, { headers });
    return response;
  } catch (error) {
    if (error?.response?.status === 401) {
      const newToken = await AuthPostRefreshToken();
      if (newToken) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const refreshedResponse = await useDeleteApi(url);
        return refreshedResponse;
      }
    }
    throw error;
  }
}

export async function usePutApi(url: string, data: object): Promise<AxiosResponse<any, any>> {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
    const response = await axios.put(url, data, { headers });
    return response;
  } catch (error) {
    if (error?.response?.status === 401) {
      const newToken = await AuthPostRefreshToken();
      if (newToken) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const refreshedResponse = await usePutApi(url, data);
        return refreshedResponse;
      }
    }
    throw error;
  }
}

export async function usePatchApi(url: string, data: object): Promise<AxiosResponse<any, any>> {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
    const response = await axios.patch(url, data, { headers });
    return response;
  } catch (error) {
    if (error?.response?.status === 401) {
      const newToken = await AuthPostRefreshToken();
      if (newToken) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const refreshedResponse = await usePatchApi(url, data);
        return refreshedResponse;
      }
    }
    throw error;
  }
}

export async function useDeleteWithBody(url: string, requestData: object): Promise<AxiosResponse<any, any>> {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
    const response = await axios.delete(url, { headers, data: requestData });
    return response;
  } catch (error) {
    if (error?.response?.status === 401) {
      const newToken = await AuthPostRefreshToken();
      if (newToken) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const refreshedResponse = await useDeleteWithBody(url, requestData);
        return refreshedResponse;
      }
    }
    throw error;
  }
}
