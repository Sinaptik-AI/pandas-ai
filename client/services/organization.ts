import { GetRequest, PostRequest } from "@/utils/apiUtils";
import { BASE_API_URL } from "utils/constants";
interface DataFrameData {
  name: string;
  url: string;
}

const orgApiUrl = `${BASE_API_URL}/api/organization`;

export const AddOrganization = async (dataToAdd: DataFrameData) => {
  const addUrl = `${orgApiUrl}`;
  try {
    const result = await PostRequest(addUrl, dataToAdd);
    return result;
  } catch (error) {
    console.error("Add request failed", error);
    throw error;
  }
};

export const GetOrganizations = async () => {
  const apiUrl = `${orgApiUrl}`;
  try {
    const response = await GetRequest(apiUrl);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
export const GetMembersList = async (id: string) => {
  const apiUrl = `${orgApiUrl}/${id}/members`;
  try {
    const data = await GetRequest(apiUrl);
    return data;
  } catch (error) {
    console.error("Delete request failed", error);
    throw error;
  }
};

export const GetOrganizationsDetail = async (id: string) => {
  const apiUrl = `${orgApiUrl}/${id}`;
  try {
    const data = await GetRequest(apiUrl);
    return data;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};

export const GetOrganizationsSettings = async () => {
  const apiUrl = `${orgApiUrl}/settings/fetch`;
  try {
    const data = await GetRequest(apiUrl);
    return data;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
export const AddOrganizationsSettings = async (body) => {
  const apiUrl = `${orgApiUrl}/settings`;
  try {
    const data = await PostRequest(apiUrl, body);
    return data;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
