import { useDeleteWithBody, useGetApi, usePostApi } from "hooks/apiHook";
import { BASE_API_URL } from "utils/constants";

const spaceApiUrl = `${BASE_API_URL}/api/spaces`;

type userSpace = {
  new_member_email: string;
};

export const GetAllSpacesList = async () => {
  const apiUrl = `${spaceApiUrl}/list`;
  const data = await useGetApi(apiUrl);
  return data;
};

export const GetSpaceUser = async (id: string) => {
  const apiUrl = `${spaceApiUrl}/${id}/user`;
  const data = await useGetApi(apiUrl);
  return data;
};
export const AddNewUserSpace = async (id: string, dataToAdd: userSpace) => {
  const addUrl = `${spaceApiUrl}/${id}/user`;
  try {
    const result = await usePostApi(addUrl, dataToAdd);
    return result;
  } catch (error) {
    console.error("Add request failed", error);
  }
};

export const DeleteSpaceUser = async (id: string, user_id) => {
  const apiUrl = `${spaceApiUrl}/${id}/user`;
  try {
    const data = await useDeleteWithBody(apiUrl, user_id);
    return data;
  } catch (error) {
    console.error("Delete request failed", error);
    throw error;
  }
};