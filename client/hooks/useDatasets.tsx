import {
  CreateDataset,
  DeleteDataset,
  GetAllDataSets,
  GetDatasetDetails,
  UpdateDatasetCard,
} from "@/services/datasets";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export const useGetAllDataSets = () => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetAllDataSets"],
    queryFn: () => GetAllDataSets(),
  });
  return { data, isLoading, error, isError };
};
export const useGetDatasetDetails = (id: string) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetDatasetDetails", id],
    queryFn: () => GetDatasetDetails(id),
  });
  return { data, isLoading, error, isError };
};

export const useUpdateDatasetCard = () => {
  const queryClient = useQueryClient();
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (params: any) => UpdateDatasetCard(params.id, params.body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["useGetDatasetDetails"] });
    },
  });
  return { data, isPending, error, isError, mutateAsync };
};
export const useCreateDataset = () => {
  const queryClient = useQueryClient();
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (params: any) => {
      return CreateDataset(params.formBody);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["useGetDatasetDetails", "useGetAllDataSets"],
      });
    },
  });
  return { data, isPending, error, isError, mutateAsync };
};
export const useDeleteDataset = () => {
  const queryClient = useQueryClient();
  const { data, isPending, error, isError, mutateAsync } = useMutation({
    mutationFn: (params: any) => {
      return DeleteDataset(params.id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["useGetDatasetDetails", "useGetAllDataSets"],
      });
    },
  });
  return { data, isPending, error, isError, mutateAsync };
};
