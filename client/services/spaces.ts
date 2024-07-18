import { DeleteRequest, DeleteRequestWithBody, GetRequest, PostRequest, PutRequest } from "@/utils/apiUtils";
import { BASE_API_URL } from "utils/constants";

const spaceApiUrl = `${BASE_API_URL}/v1/workspace`;

type userSpace = {
  new_member_email: string;
};


export const GetAllWorkspaces = async () => {
  try {
    const response = await fetch(`${spaceApiUrl}/list`, { next: { tags: ['GetAllWorkspaces'] } });
    return await response.json();
  } catch (error) {
    console.error('Get request failed', error);
    throw error;
  }
};

export const GetWorkspaceDetails = async (id: string) => {
  try {
    const response = await fetch(`${spaceApiUrl}/${id}/details`, { next: { tags: ['GetWorkspaceDetails'] } });
    return await response.json();
  } catch (error) {
    console.error('Get request failed', error);
    throw error;
  }
};

export const AddWorkspace = async (body) => {
  const apiUrl = `${spaceApiUrl}/add`;
  try {
    const data = await PostRequest(apiUrl, body);
    return data;
  } catch (error) {
    console.error("add request failed", error);
    throw error;
  }
};

export const UpdateWorkspace = async (id: string, body) => {
  const apiUrl = `${spaceApiUrl}/${id}/edit`;
  try {
    const data = await PutRequest(apiUrl, body);
    return data;
  } catch (error) {
    console.error("add request failed", error);
    throw error;
  }
};

export const DeleteWorkspace = async (id: string) => {
  const apiUrl = `${spaceApiUrl}/${id}`;
  try {
    const data = await DeleteRequest(apiUrl);
    return data;
  } catch (error) {
    console.error("Delete request failed", error);
    throw error;
  }
};

export const GetSpaceUser = async (id: string) => {
  const apiUrl = `${spaceApiUrl}/${id}/user`;
  const data = await GetRequest(apiUrl);
  return data;
};
export const AddNewUserSpace = async (id: string, dataToAdd: userSpace) => {
  const addUrl = `${spaceApiUrl}/${id}/user`;
  try {
    const result = await PostRequest(addUrl, dataToAdd);
    return result;
  } catch (error) {
    console.error("Add request failed", error);
  }
};

export const DeleteSpaceUser = async (id: string, user_id) => {
  const apiUrl = `${spaceApiUrl}/${id}/user`;
  try {
    const data = await DeleteRequestWithBody(apiUrl, user_id);
    return data;
  } catch (error) {
    console.error("Delete request failed", error);
    throw error;
  }
};