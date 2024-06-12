import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AddOrganizationsSettings,
  GetMembersList,
  GetOrganizations,
  GetOrganizationsDetail,
  GetOrganizationsSettings,
} from "@/services/organization";

export const useGetOrganizations = () => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetOrganizations"],
    queryFn: GetOrganizations,
  });
  return { data, isLoading, error, isError };
};
export const useGetOrganizationsDetail = (orgId: string) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetOrganizationsDetail", orgId],
    queryFn: () => GetOrganizationsDetail(orgId),
  });
  return { data, isLoading, error, isError };
};
export const useGetMembersList = (orgId: string) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetMembersList", orgId],
    queryFn: () => GetMembersList(orgId),
    enabled: !!orgId,
  });
  return { data, isLoading, error, isError };
};
export const useGetOrganizationsSettings = () => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetOrganizationsSettings"],
    queryFn: () => GetOrganizationsSettings(),
  });
  return { data, isLoading, error, isError };
};
export const useAddOrganizationsSettings = () => {
  const queryClient = useQueryClient();
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (body: any) => AddOrganizationsSettings(body),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["useGetOrganizationsSettings", "useGetOrganizationsDetail"],
      });
    },
  });
  return { data, isPending, error, isError, mutateAsync };
};
