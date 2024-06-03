import { DeleteRequestWithBody, GetRequest, PostRequest } from "@/utils/apiUtils";
import { BASE_API_URL } from "utils/constants";

const spaceApiUrl = `${BASE_API_URL}/api/spaces`;

type userSpace = {
  new_member_email: string;
};

export const GetAllSpacesList = async () => {
  const apiUrl = `${spaceApiUrl}/list`;
  const data = await GetRequest(apiUrl);
  return data;
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