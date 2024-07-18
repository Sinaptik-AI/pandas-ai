import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getMe, updateUserRoutes } from "@/services/users";

export const useGetMe = () => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetMe"],
    queryFn: getMe,
  });
  return { data, isLoading, error, isError };
};

export const useUpdateUserRoutes = () => {
  const queryClient = useQueryClient();
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (params: any) => updateUserRoutes(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["useGetMe"] });
    },
  });
  return { data, isPending, error, isError, mutateAsync };
};
