import { GetLogDetails, GetLogs } from "@/services/logs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export const useGetLogs = () => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetLogs"],
    queryFn: () => GetLogs(),
  });
  return { data, isLoading, error, isError };
};

export const useGetLogDetails = (logId: string) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetLogDetails", logId],
    queryFn: () => GetLogDetails(logId),
  });
  return { data, isLoading, error, isError };
};
