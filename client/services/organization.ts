import {
  useDeleteApi,
  useGetApi,
  usePatchApi,
  usePostApi,
} from "hooks/apiHook";
import { BASE_API_URL } from "utils/constants";
interface DataFrameData {
  name: string;
  url: string;
}
interface DataMembers {
  first_name: string;
  last_name: string;
  email?: string;
  role: string;
}

interface OrgID {
  organization_id: string;
}

const orgApiUrl = `${BASE_API_URL}/api/organization`;


export const AddOrganization = async (dataToAdd: DataFrameData) => {
  const addUrl = `${orgApiUrl}`;
  try {
    const result = await usePostApi(addUrl, dataToAdd);
    return result;
  } catch (error) {
    console.error("Add request failed", error);
    throw error;
  }
};

export const GetOrganizations = async () => {
  const apiUrl = `${orgApiUrl}`;
  try {
    const response = await useGetApi(apiUrl);
    return response;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
export const GetMembersList = async (id: string) => {
  const apiUrl = `${orgApiUrl}/${id}/members`;
  try {
    const data = await useGetApi(apiUrl);
    return data;
  } catch (error) {
    console.error("Delete request failed", error);
    throw error;
  }
};

export const AddMembers = async (id: number, dataToAdd: DataMembers) => {
  const addUrl = `${orgApiUrl}/${id}/members`;
  try {
    const result = await usePostApi(addUrl, dataToAdd);
    return result;
  } catch (error) {
    console.error("Add request failed", error);
    throw Error
  }
};
export const EditMembers = async (id: number, dataToAdd: DataMembers) => {
  const updateUrl = `${orgApiUrl}/${id}/members`;
  try {
    const result = await usePatchApi(updateUrl, dataToAdd);
    return result;
  } catch (error) {
    console.error("update request failed", error);
    throw error;
  }
};
export const DeleteMember = async (orgId: string, memberId: string) => {
  const deleteUrl = `${orgApiUrl}/${orgId}/members/${memberId}`;
  try {
    const result = await useDeleteApi(deleteUrl);
    return result;
  } catch (error) {
    console.error("update request failed", error);
    throw error;
  }
};
export const Deleteorganization = async (id: number) => {
  const apiUrl = `${orgApiUrl}/${id}`;
  try {
    const data = await useDeleteApi(apiUrl);
    return data;
  } catch (error) {
    console.error("Delete request failed", error);
    throw error;
  }
};
export const GetOrganizationsDetail = async (id: string) => {
  const apiUrl = `${orgApiUrl}/${id}`;
  try {
    const data = await useGetApi(apiUrl);
    return data;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};

export const UpdateOrganization = async (id, dataToAdd) => {
  const updateUrl = `${orgApiUrl}/${id}`;
  try {
    const result = await usePatchApi(updateUrl, dataToAdd);
    return result;
  } catch (error) {
    console.error("update request failed", error);
    throw error;
  }
};

export const SwitchOrganization = async (dataToAdd: OrgID) => {
  const addUrl = `${orgApiUrl}/switch`;
  try {
    const response = await usePostApi(addUrl, dataToAdd);
    return response;
  } catch (error) {
    console.error("Add request failed", error);
    throw error;
  }
};

export const VeryfyInvitation = async () => {
  const apiUrl = `${orgApiUrl}/invitations/accept`;
  const data = await usePostApi(apiUrl, {});
  return data;
};

export const GetOrganizationsSettings = async () => {
  const apiUrl = `${orgApiUrl}/settings/fetch`;
  try {
    const data = await useGetApi(apiUrl);
    return data;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};
export const AddOrganizationsSettings = async (body) => {
  const apiUrl = `${orgApiUrl}/settings`;
  try {
    const data = await usePostApi(apiUrl, body);
    return data;
  } catch (error) {
    console.error("Get request failed", error);
    throw error;
  }
};