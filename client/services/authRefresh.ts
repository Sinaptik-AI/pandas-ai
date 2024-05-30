import { BASE_API_URL } from "@/utils/constants";
import axios from "axios";


export const AuthPostRefreshToken = async () => {
  const apiUrl = `${BASE_API_URL}/api/auth/refresh-token`;
  const token = localStorage.getItem("refreshToken");
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  try {
    const response = await axios.post(apiUrl, {}, { headers });
    if (response?.request?.status !== 200) {
      localStorage.clear();
      window.location.reload();
      return false;
    } else {
      localStorage.setItem("accessToken", response?.data?.data?.accessToken);
      return true;
    }
  } catch (error) {
    localStorage.clear();
    return window.location.reload();
  }
};

export const AuthRefreshToken = async () => {
  const apiUrl = `${BASE_API_URL}/api/auth/refresh-token`;
  const token = localStorage.getItem("refreshToken");
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  try {
    const response = await axios.post(apiUrl, {}, { headers });
    if (response?.request?.status !== 200) {
      localStorage.clear();
      return window.location.reload();
    } else {
      localStorage.setItem("accessToken", response?.data?.data?.accessToken);
      return window.location.reload();
    }
  } catch (error) {
    localStorage.clear();
    return window.location.reload();
  }
};
