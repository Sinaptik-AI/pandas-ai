import { useQuery } from "@tanstack/react-query";
import {
  ConversationChatBySpaceApi,
  ExplainConversationMessage,
  FetchFollowUpQuestions,
  GetChatLabel,
} from "@/services/chatInterface";

export const useGetConversations = (spaceId, page, rowsPerPage) => {
  const { data, isLoading, error, isError, refetch, isFetching } = useQuery({
    queryKey: ["ConversationChatApi"],
    queryFn: () => ConversationChatBySpaceApi(spaceId, page, rowsPerPage),
  });
  return { data, isLoading, error, isError, refetch, isFetching };
};
export const useGetFollowUpQuestions = (conversationId) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetFollowUpQuestions"],
    queryFn: () => FetchFollowUpQuestions(conversationId),
    enabled: !!conversationId,
  });
  return { data, isLoading, error, isError };
};
export const useGetChatLabel = (chatId: string) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useGetChatLabel", chatId],
    queryFn: () => GetChatLabel(chatId),
  });
  return { data, isLoading, error, isError };
};
export const useExplainConversationMessage = (
  conversationId: string,
  chatId: string
) => {
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["useExplainConversationMessage", conversationId, chatId],
    queryFn: () => ExplainConversationMessage(conversationId, chatId),
  });
  return { data, isLoading, error, isError };
};
