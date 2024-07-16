import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AddNewUserSpace,
  DeleteSpaceUser,
  DeleteWorkspace,
  GetSpaceUser,
} from "@/services/spaces";

export const useGetSpaceUsers = (spaceId: string) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetSpaceUsers", spaceId],
    queryFn: () => GetSpaceUser(spaceId),
    enabled: !!spaceId,
  });
  return { data, isLoading, error, isError };
};

export const useDeleteSpaceUsers = () => {
  const queryClient = useQueryClient();
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (params: any) =>
      DeleteSpaceUser(params.spaceId, params.payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["useGetSpaceUsers"] });
    },
  });
  return { data, isPending, error, isError, mutateAsync };
};
export const useAddSpaceUsers = () => {
  const queryClient = useQueryClient();
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (params: any) =>
      AddNewUserSpace(params.spaceId, params.payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["useGetSpaceUsers"] });
    },
  });
  return { data, isPending, error, isError, mutateAsync };
};
export const useDeleteWorkspace = () => {
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (params: any) => DeleteWorkspace(params.id),
    onSuccess: () => {},
  });
  return { data, isPending, error, isError, mutateAsync };
};
