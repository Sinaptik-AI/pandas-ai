import { useQuery } from "@tanstack/react-query";
import { getMe } from "@/services/users";

export const useGetMe = () => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetMe"],
    queryFn: getMe,
  });
  return { data, isLoading, error, isError };
};
