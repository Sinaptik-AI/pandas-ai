import { ChatMessageData } from "@/types/chat-types";
import EmptyHeart from "components/Icons/EmptyHeart";
import GenerateCodeIcon from "components/Icons/GenerateCodeIcon";
import ReloadChatIcon from "components/Icons/ReloadChatIcon";
import React from "react";
import { useAppStore } from "store";
import { Tooltip } from "react-tooltip";
import ExplainIcon from "components/Icons/ExplainIcon";

interface IProps {
  handleUserRating: (id: string, reaction: boolean) => void;
  handleRetry: (id) => void;
  handleCodeView: (id) => void;
  chat: ChatMessageData;
}

const ChatReaction = ({
  handleUserRating,
  handleRetry,
  handleCodeView,
  chat,
}: IProps) => {
  const darkMode = useAppStore((state) => state.darkMode);
  const setSelectedChatItem = useAppStore((state) => state.setSelectedChatItem);
  const setIsExplainViewOpen = useAppStore(
    (state) => state.setIsExplainViewOpen
  );
  return (
    <div className="flex items-center gap-2">
      <div
        data-tooltip-id={chat.id}
        className="cursor-pointer"
        onClick={() => {
          handleUserRating(chat?.id, chat?.thumbs_up ? false : true);
        }}
      >
        <EmptyHeart
          color={chat?.thumbs_up ? "red" : darkMode ? "white" : "grey"}
        />
      </div>
      <Tooltip id={chat.id} variant="dark" opacity="unset">
        {chat.thumbs_up ? "Remove from feed" : "Add to the feed"}
      </Tooltip>
      <div
        data-tooltip-id="retry"
        className="cursor-pointer"
        onClick={() => {
          handleRetry(chat?.id);
        }}
      >
        <ReloadChatIcon color={darkMode ? "white" : "black"} />
      </div>
      <Tooltip id="retry">Retry</Tooltip>

      {chat?.code && (
        <div
          data-tooltip-id="code"
          className="cursor-pointer"
          onClick={() => {
            handleCodeView(chat?.id);
          }}
        >
          <GenerateCodeIcon color={darkMode ? "white" : "black"} />
        </div>
      )}
      <Tooltip id="code">Edit code</Tooltip>
      <div
        data-tooltip-id="explain"
        className="cursor-pointer"
        onClick={() => {
          setSelectedChatItem(chat);
          setIsExplainViewOpen(true);
        }}
      >
        <ExplainIcon color={darkMode ? "white" : "black"} />
      </div>
      <Tooltip id="explain">Explain</Tooltip>
    </div>
  );
};

export default ChatReaction;
