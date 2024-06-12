import { GetChatLabelLoader } from "components/Skeletons";
import { useGetChatLabel } from "hooks/useConversations";
import React from "react";

interface IProps {
  chatId: string;
  message: number | string;
}

const ChatLabel = ({ chatId, message }: IProps) => {
  const { isLoading, data, isError, error } = useGetChatLabel(chatId && chatId);

  return (
    <div className="flex flex-col bg-white dark:bg-[#333333] rounded-[16px] max-w-60">
      <span className="text-base font-normal dark:text-white p-3">
        {isLoading ? (
          <GetChatLabelLoader />
        ) : isError ? (
          error.message
        ) : (
          data?.data?.data?.["result-label"]
        )}
      </span>
      <div className="border-b dark:border-white w-full" />
      <h1 className="font-bold text-4xl py-4 px-3 text-center">
        {message && message}
      </h1>
    </div>
  );
};

export default ChatLabel;
