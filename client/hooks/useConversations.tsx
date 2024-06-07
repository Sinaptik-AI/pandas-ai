import { useQuery } from "@tanstack/react-query";
import { ExplainConversationMessage, GetChatLabel } from "@/services/chat";

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
